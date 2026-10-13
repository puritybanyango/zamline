# Owner: Jesca Amondi
# Feature: Cost Estimation and Margin Decision Support

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from models.shipment_matches import MatchOutcome


class CostAssessmentResponse(BaseModel):
    match_id: UUID
    distance_km: float
    duration_minutes: int
    fuel_cost: Decimal
    driver_cost: Decimal
    toll_cost: Decimal
    maintenance_cost: Decimal
    other_cost: Decimal
    estimated_total_cost: Decimal
    proposed_amount: Decimal
    estimated_margin: Decimal
    outcome: MatchOutcome
    ai_explanation: str | None
    ai_status: str
