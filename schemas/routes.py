# Owner: Jesca Amondi
# Feature: Route Information

from pydantic import BaseModel


class RouteResponse(BaseModel):
    distance_km: float
    duration_minutes: int
