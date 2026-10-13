# Feature README: Sandra Twala

## Owns
- F-09 Shipment Management
- F-10 Cargo Validation

## Owned files
- `repositories/shipments.py`
- `schemas/shipments.py`
- `services/shipments.py`
- `routers/shipments.py`
- shipment feature tests

## Uses shared contracts
- `models/shipments.py`
- `models/companies.py`
- `models/users.py`
- `dependency.py`
- `services/audit_logs.py`

## Important behavior
Only verified Shippers create shipment opportunities. Cargo validation happens before publishing. Matching consumes only open eligible shipments. Matching is based on weight in kilograms and required body type, not volume.

The actual approved unaccepted-cargo values are configured through `UNACCEPTED_CARGO_TYPES`; do not invent legal/regulatory categories.

## Do not change without coordination
Matching/reservation logic, truck code, shared models, database foundation or auth/security.

## Test
```bash
uv run --no-sync pytest tests/test_shipments_feature.py tests/test_shipments.py
```
