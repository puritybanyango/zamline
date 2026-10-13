# Feature README: Shamy Umukundwa

## Owns
- F-01 Fleet Matching
- F-02 Acceptance, Reservation and Contact Handoff

## Owned files
- `repositories/shipment_matches.py`
- `repositories/reservations.py`
- `schemas/shipment_matches.py`
- `schemas/reservations.py`
- `services/shipment_matches.py`
- `services/reservations.py`
- `routers/shipment_matches.py`
- `routers/reservations.py`
- matching/acceptance tests

## Uses shared contracts
- `models/shipments.py`
- `models/trucks.py`
- `models/shipment_matches.py`
- `models/reservations.py`
- `models/companies.py`
- `models/users.py`
- `dependency.py`
- `services/audit_logs.py`

## Important behavior
Matching uses kg capacity, body type and truck availability. Acceptance must create one reservation only, confirm the shipment, close competing pending matches and reveal contact details only after a valid reservation.

## Do not change without coordination
`models/`, `database.py`, `dependency.py`, `main.py`, `alembic/`, `pyproject.toml`, shared security and integration files.

## Test
```bash
uv run --no-sync pytest tests/test_matching_feature.py tests/test_shipment_matches.py tests/test_reservations.py
```

SQLite tests ordinary behavior. The simultaneous first-acceptance race still requires isolated PostgreSQL integration testing.
