# Owner: Shared Team
# Feature: Application integration

from fastapi import FastAPI

from routers import (
    companies,
    cost_estimation,
    cost_settings,
    reservations,
    routes,
    shipment_matches,
    shipments,
    trucks,
    users,
)

app = FastAPI(title="ZamLine", version="0.2.0")

app.include_router(users.router)
app.include_router(companies.router)
app.include_router(trucks.router)
app.include_router(cost_settings.router)
app.include_router(shipments.router)
app.include_router(shipment_matches.router)
app.include_router(routes.router)
app.include_router(cost_estimation.router)
app.include_router(reservations.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
