# Owner: Purity Anyango
# Feature: Fleet Management

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from dependency import require_role, require_verified_company
from models.users import UserRole
from schemas.trucks import TruckCreate, TruckResponse, TruckUpdate
from services.trucks import create_truck, get_truck, list_trucks, update_truck

router = APIRouter(prefix="/trucks", tags=["fleet"])

fleet_manager = require_role(UserRole.FLEET_MANAGER)


@router.post("", response_model=TruckResponse, status_code=status.HTTP_201_CREATED)
def create(
    payload: TruckCreate,
    db: Session = Depends(get_db),
    current_user=Depends(fleet_manager),
    company=Depends(require_verified_company),
):
    return create_truck(db, company.company_id, current_user.user_id, payload)


@router.get("", response_model=list[TruckResponse])
def list_all(
    db: Session = Depends(get_db),
    current_user=Depends(fleet_manager),
    company=Depends(require_verified_company),
):
    return list_trucks(db, company.company_id)


@router.get("/{truck_id}", response_model=TruckResponse)
def read(
    truck_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(fleet_manager),
    company=Depends(require_verified_company),
):
    return get_truck(db, company.company_id, truck_id)


@router.patch("/{truck_id}", response_model=TruckResponse)
def update(
    truck_id: UUID,
    payload: TruckUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(fleet_manager),
    company=Depends(require_verified_company),
):
    return update_truck(
        db,
        company.company_id,
        current_user.user_id,
        truck_id,
        payload,
    )
