# Owner: Helen Mezgebe
# Feature: PACRA Business Verification


from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, HttpUrl

from models.companies import CompanyType, VerificationStatus


class CompanyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    company_id: UUID
    company_type: CompanyType
    business_name: str
    registration_number: str
    company_email: str
    phone_number: str
    verification_status: VerificationStatus
    verified_at: datetime | None
    certificate_file_url: str | None


class CompanyVerificationSubmit(BaseModel):
    certificate_file_url: HttpUrl


class VerificationResultInput(BaseModel):
    status: VerificationStatus
    failure_reason: str | None = None


class PrivateCostSettingsResponse(BaseModel):
    fuel_price_per_litre: Decimal | None
    driver_daily_allowance: Decimal | None
    toll_assumption: Decimal | None
    other_costs: Decimal | None
