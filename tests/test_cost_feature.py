from decimal import Decimal

import models
from integrations.openrouteservice import get_hgv_route
from services.cost_estimation import assess_match, calculate_costs


def test_deterministic_cost_calculation():
    result = calculate_costs(
        distance_km=400,
        duration_minutes=600,
        fuel_consumption_l_per_100km=30,
        fuel_price_per_litre=Decimal("1.50"),
        driver_daily_allowance=Decimal("100.00"),
        maintenance_per_km=Decimal("0.50"),
        toll_assumption=Decimal("20.00"),
        other_costs=Decimal("10.00"),
        proposed_amount=Decimal("1000.00"),
    )

    assert result["fuel_cost"] == Decimal("180.00")
    assert result["driver_cost"] == Decimal("100.00")
    assert result["maintenance_cost"] == Decimal("200.00")
    assert result["estimated_total_cost"] == Decimal("510.00")
    assert result["estimated_margin"] == Decimal("490.00")
    assert result["outcome"] == models.MatchOutcome.PROFIT


def test_openrouteservice_uses_longitude_latitude_order(monkeypatch):
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "routes": [
                    {
                        "summary": {
                            "distance": 386306.3,
                            "duration": 18718.0,
                        }
                    }
                ]
            }

    def fake_post(url, headers, json, timeout):
        captured["json"] = json
        return FakeResponse()

    monkeypatch.setattr("integrations.openrouteservice.ORS_API_KEY", "test-key")
    monkeypatch.setattr("integrations.openrouteservice.httpx.post", fake_post)

    route = get_hgv_route(
        origin_latitude=-15.3875,
        origin_longitude=28.3228,
        destination_latitude=-12.8024,
        destination_longitude=28.2132,
    )

    assert captured["json"]["coordinates"] == [
        [28.3228, -15.3875],
        [28.2132, -12.8024],
    ]
    assert route["distance_km"] == 386.31
    assert route["duration_minutes"] == 312


def test_cost_assessment_updates_match_without_ai_failure_breaking_baseline(
    db_session,
    sample_match,
    sample_fleet_company,
    sample_fleet_user,
    monkeypatch,
):
    sample_fleet_company.fuel_price_per_litre = Decimal("1.50")
    sample_fleet_company.driver_daily_allowance = Decimal("100.00")
    sample_fleet_company.toll_assumption = Decimal("20.00")
    sample_fleet_company.other_costs = Decimal("10.00")
    db_session.commit()

    monkeypatch.setattr(
        "services.cost_estimation.get_hgv_route",
        lambda *args, **kwargs: {"distance_km": 400.0, "duration_minutes": 600},
    )
    monkeypatch.setattr(
        "services.cost_estimation.explain_cost_assessment",
        lambda context: None,
    )

    result = assess_match(
        db_session,
        sample_fleet_company.company_id,
        sample_fleet_user.user_id,
        sample_match.match_id,
    )

    assert result["estimated_total_cost"] > 0
    assert sample_match.estimated_total_cost == result["estimated_total_cost"]
    assert result["ai_status"] == "not_configured"
