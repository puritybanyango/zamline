# Owner: Jesca Amondi
# Feature: Cost Estimation and Margin Decision Support

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from dependency import require_role, require_verified_company
from models.users import UserRole
from schemas.cost_estimation import CostAssessmentResponse
from services.cost_estimation import assess_match

router = APIRouter(prefix="/cost-estimation", tags=["cost estimation"])

fleet_manager = require_role(UserRole.FLEET_MANAGER)


@router.post("/{match_id}", response_model=CostAssessmentResponse)
def assess(
    match_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(fleet_manager),
    company=Depends(require_verified_company),
):
    return assess_match(
        db,
        company.company_id,
        current_user.user_id,
        match_id,
    )
