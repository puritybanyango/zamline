# Owner: Jesca Amondi
# Feature: Route Information

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from dependency import require_role, require_verified_company
from models.users import UserRole
from schemas.routes import RouteResponse
from services.routes import get_route_for_match

router = APIRouter(prefix="/routes", tags=["route information"])

fleet_manager = require_role(UserRole.FLEET_MANAGER)


@router.get("/{match_id}", response_model=RouteResponse)
def read_route(
    match_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(fleet_manager),
    company=Depends(require_verified_company),
):
    return get_route_for_match(db, company.company_id, match_id)
