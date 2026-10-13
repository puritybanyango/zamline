# Owner: Shamy Umukundwa
# Feature: Fleet Matching and Acceptance

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from models.shipment_matches import ManagerDecision, MatchOutcome


class MatchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    match_id: UUID
    shipment_id: UUID
    truck_id: UUID
    user_id: UUID | None
    distance_km: float | None
    duration: int | None
    fuel_cost: Decimal | None
    driver_cost: Decimal | None
    toll_cost: Decimal | None
    maintenance_cost: Decimal | None
    other_cost: Decimal | None
    estimated_total_cost: Decimal | None
    proposed_amount: Decimal | None
    estimated_margin: Decimal | None
    outcome: MatchOutcome | None
    ai_explanation: str | None
    manager_decision: ManagerDecision
    created_at: datetime
    decided_at: datetime | None


class MatchRefreshResponse(BaseModel):
    created_matches: int


class MatchDecisionRequest(BaseModel):
    decision: ManagerDecision
