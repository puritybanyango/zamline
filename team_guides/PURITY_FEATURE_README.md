# Feature README: Purity Anyango

## Owns
- F-07 Fleet Management
- F-08 Private Operating Cost Settings

## Owned files
- `repositories/trucks.py`
- `repositories/cost_settings.py`
- `schemas/trucks.py`
- `schemas/cost_settings.py`
- `services/trucks.py`
- `services/cost_settings.py`
- `routers/trucks.py`
- `routers/cost_settings.py`
- fleet tests

## Uses shared contracts
- `models/trucks.py`
- `models/companies.py`
- `dependency.py`
- `services/audit_logs.py`

## Important behavior
All truck access is company-scoped. Private operating costs are Fleet Manager data and must never be exposed through Shipper endpoints. Truck availability is a shared input to matching.

## Do not change without coordination
Helen's full company repository/service, matching logic, shared models, database foundation or auth/security.

## Test
```bash
uv run --no-sync pytest tests/test_fleet_feature.py tests/test_trucks.py
```
