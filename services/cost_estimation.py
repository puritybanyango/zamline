# Owner: Jesca Amondi
# Feature: Cost Estimation and Margin Decision Support

import math
from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from integrations.gemini import GeminiReferenceError, explain_cost_assessment
from integrations.openrouteservice import OpenRouteServiceError, get_hgv_route
from models.shipment_matches import ManagerDecision, MatchOutcome
from repositories.cost_estimation import get_fleet_match
from repositories.companies import get_company_by_id
from services.audit_logs import record_event

MONEY = Decimal("0.01")


def _money(value) -> Decimal:
    return Decimal(str(value or 0)).quantize(MONEY, rounding=ROUND_HALF_UP)


def calculate_costs(
    distance_km: float,
    duration_minutes: int,
    fuel_consumption_l_per_100km: float,
    fuel_price_per_litre,
    driver_daily_allowance,
    maintenance_per_km,
    toll_assumption,
    other_costs,
    proposed_amount,
) -> dict:
    fuel_litres = (
        Decimal(str(distance_km))
        / Decimal("100")
        * Decimal(str(fuel_consumption_l_per_100km))
    )
    fuel_cost = _money(fuel_litres * Decimal(str(fuel_price_per_litre)))
    driver_days = max(1, math.ceil(duration_minutes / 1440))
    driver_cost = _money(Decimal(driver_days) * Decimal(str(driver_daily_allowance)))
    maintenance_cost = _money(
        Decimal(str(distance_km)) * Decimal(str(maintenance_per_km))
    )
    toll_cost = _money(toll_assumption)
    other_cost = _money(other_costs)

    total = _money(fuel_cost + driver_cost + maintenance_cost + toll_cost + other_cost)
    proposed = _money(proposed_amount)
    margin = _money(proposed - total)

    if margin > 0:
        outcome = MatchOutcome.PROFIT
    elif margin < 0:
        outcome = MatchOutcome.LOSS
    else:
        outcome = MatchOutcome.BREAK_EVEN

    return {
        "fuel_cost": fuel_cost,
        "driver_cost": driver_cost,
        "maintenance_cost": maintenance_cost,
        "toll_cost": toll_cost,
        "other_cost": other_cost,
        "estimated_total_cost": total,
        "proposed_amount": proposed,
        "estimated_margin": margin,
        "outcome": outcome,
    }


def assess_match(
    db: Session,
    company_id: UUID,
    user_id: UUID,
    match_id: UUID,
) -> dict:
    match = get_fleet_match(db, company_id, match_id)
    if match is None:
        raise HTTPException(status_code=404, detail="Match not found")

    if match.manager_decision != ManagerDecision.PENDING:
        raise HTTPException(
            status_code=409,
            detail="Only pending matches can be assessed",
        )

    company = get_company_by_id(db, company_id)
    truck = match.truck
    shipment = match.shipment

    required_settings = {
        "fuel price": company.fuel_price_per_litre,
        "driver allowance": company.driver_daily_allowance,
        "maintenance rate": truck.maintenance_per_km,
    }
    missing = [name for name, value in required_settings.items() if value is None]
    if missing:
        raise HTTPException(
            status_code=409,
            detail=f"Missing operating cost settings: {', '.join(missing)}",
        )

    try:
        route = get_hgv_route(
            float(shipment.origin_latitude),
            float(shipment.origin_longitude),
            float(shipment.destination_latitude),
            float(shipment.destination_longitude),
        )
    except OpenRouteServiceError as error:
        raise HTTPException(status_code=502, detail=str(error))

    costs = calculate_costs(
        distance_km=route["distance_km"],
        duration_minutes=route["duration_minutes"],
        fuel_consumption_l_per_100km=truck.fuel_consumption_l_per_100km,
        fuel_price_per_litre=company.fuel_price_per_litre,
        driver_daily_allowance=company.driver_daily_allowance,
        maintenance_per_km=truck.maintenance_per_km,
        toll_assumption=company.toll_assumption,
        other_costs=company.other_costs,
        proposed_amount=shipment.proposed_amount,
    )

    match.distance_km = route["distance_km"]
    match.duration = route["duration_minutes"]
    match.fuel_cost = costs["fuel_cost"]
    match.driver_cost = costs["driver_cost"]
    match.maintenance_cost = costs["maintenance_cost"]
    match.toll_cost = costs["toll_cost"]
    match.other_cost = costs["other_cost"]
    match.estimated_total_cost = costs["estimated_total_cost"]
    match.proposed_amount = costs["proposed_amount"]
    match.estimated_margin = costs["estimated_margin"]
    match.outcome = costs["outcome"]

    ai_status = "not_configured"
    ai_explanation = None
    ai_context = {
        "distance_km": route["distance_km"],
        "duration_minutes": route["duration_minutes"],
        "fuel_cost": costs["fuel_cost"],
        "driver_cost": costs["driver_cost"],
        "maintenance_cost": costs["maintenance_cost"],
        "toll_cost": costs["toll_cost"],
        "other_cost": costs["other_cost"],
        "estimated_total_cost": costs["estimated_total_cost"],
        "proposed_amount": costs["proposed_amount"],
        "estimated_margin": costs["estimated_margin"],
        "outcome": costs["outcome"].value,
    }

    try:
        ai_explanation = explain_cost_assessment(ai_context)
        if ai_explanation:
            ai_status = "available"
        match.ai_explanation = ai_explanation
    except GeminiReferenceError:
        ai_status = "reference_refresh_failed"
        match.ai_explanation = None
    except RuntimeError:
        ai_status = "unavailable"
        match.ai_explanation = None

    record_event(
        db,
        "cost_assessed",
        user_id=user_id,
        company_id=company_id,
        entity_type="shipment_match",
        entity_id=match.match_id,
        details={"outcome": costs["outcome"].value},
    )
    db.commit()
    db.refresh(match)

    return {
        "match_id": match.match_id,
        "distance_km": route["distance_km"],
        "duration_minutes": route["duration_minutes"],
        **costs,
        "ai_explanation": match.ai_explanation,
        "ai_status": ai_status,
    }
