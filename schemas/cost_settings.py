# Owner: Purity Anyango
# Feature: Private Operating Cost Settings

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CostSettingsUpdate(BaseModel):
    fuel_price_per_litre: Decimal | None = Field(default=None, gt=0)
    driver_daily_allowance: Decimal | None = Field(default=None, ge=0)
    toll_assumption: Decimal | None = Field(default=None, ge=0)
    other_costs: Decimal | None = Field(default=None, ge=0)


class CostSettingsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    fuel_price_per_litre: Decimal | None
    driver_daily_allowance: Decimal | None
    toll_assumption: Decimal | None
    other_costs: Decimal | None
