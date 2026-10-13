# Owner: Purity Anyango
# Feature: Private Operating Cost Settings

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from dependency import require_role, require_verified_company
from models.users import UserRole
from schemas.cost_settings import CostSettingsResponse, CostSettingsUpdate
from services.cost_settings import get_cost_settings, update_cost_settings

router = APIRouter(prefix="/cost-settings", tags=["fleet"])

fleet_manager = require_role(UserRole.FLEET_MANAGER)


@router.get("", response_model=CostSettingsResponse)
def read(
    db: Session = Depends(get_db),
    current_user=Depends(fleet_manager),
    company=Depends(require_verified_company),
):
    return get_cost_settings(db, company.company_id)


@router.patch("", response_model=CostSettingsResponse)
def update(
    payload: CostSettingsUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(fleet_manager),
    company=Depends(require_verified_company),
):
    return update_cost_settings(
        db,
        company.company_id,
        current_user.user_id,
        payload,
    )
