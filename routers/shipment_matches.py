# Owner: Shamy Umukundwa
# Feature: Fleet Matching and Acceptance

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from dependency import require_role, require_verified_company
from models.users import UserRole
from schemas.shipment_matches import (
    MatchDecisionRequest,
    MatchRefreshResponse,
    MatchResponse,
)
from services.shipment_matches import decide_match, list_matches, refresh_matches

router = APIRouter(prefix="/shipment-matches", tags=["matching"])

fleet_manager = require_role(UserRole.FLEET_MANAGER)


@router.post("/refresh", response_model=MatchRefreshResponse)
def refresh(
    db: Session = Depends(get_db),
    current_user=Depends(fleet_manager),
    company=Depends(require_verified_company),
):
    count = refresh_matches(db, company.company_id, current_user.user_id)
    return MatchRefreshResponse(created_matches=count)


@router.get("", response_model=list[MatchResponse])
def list_all(
    db: Session = Depends(get_db),
    current_user=Depends(fleet_manager),
    company=Depends(require_verified_company),
):
    return list_matches(db, company.company_id)


@router.post("/{match_id}/decision", response_model=MatchResponse)
def decide(
    match_id: UUID,
    payload: MatchDecisionRequest,
    db: Session = Depends(get_db),
    current_user=Depends(fleet_manager),
    company=Depends(require_verified_company),
):
    return decide_match(
        db,
        company.company_id,
        current_user.user_id,
        match_id,
        payload.decision,
    )
