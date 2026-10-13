# Feature README: Jesca Amondi

## Owns
- F-05 Route Information
- F-06 Cost Estimation and Margin Decision Support

## Owned files
- `repositories/cost_estimation.py`
- `schemas/routes.py`
- `schemas/cost_estimation.py`
- `services/routes.py`
- `services/cost_estimation.py`
- `routers/routes.py`
- `routers/cost_estimation.py`
- `integrations/openrouteservice.py`
- `integrations/gemini.py`
- route/cost tests

## Uses shared contracts
- `models/shipments.py`
- `models/trucks.py`
- `models/shipment_matches.py`
- `models/companies.py`
- Shamy's match lifecycle
- Purity's truck/private-cost data
- Sandra's shipment route/payment data

## Important behavior
ORS receives route coordinates only and uses `[longitude, latitude]` with `driving-hgv`. Deterministic cost calculation happens before AI. Gemini may explain a result but cannot accept shipments, create reservations or make authorization decisions.

## Do not change without coordination
`repositories/shipment_matches.py`, reservation logic, shared models, auth/security, or database foundation.

## Test
```bash
uv run --no-sync pytest tests/test_cost_feature.py
```
