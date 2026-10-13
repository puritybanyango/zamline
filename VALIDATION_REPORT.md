# ZamLine Backend Validation Report

## Completed checks

- Full pytest suite: **153 passed**
- Coverage run: **81% total coverage**
- Python compile check: **passed**
- FastAPI `/health`: **200 OK**
- SQLAlchemy metadata: exactly **7 domain tables**
  - `audit_logs`
  - `companies`
  - `reservations`
  - `shipment_matches`
  - `shipments`
  - `trucks`
  - `users`
- Alembic initial migration upgrade on isolated SQLite: **passed**
- Alembic downgrade to base on isolated SQLite: **passed**
- Long Python lines above 88 characters: **0**
- Simple unused-import precheck: **0 findings**

## Checks not executed in this environment

### Ruff

The build environment does not have the Ruff executable installed and cannot reach PyPI, so `ruff check .` and `ruff format --check .` could not be executed here.

Run locally or in GitHub Actions:

```bash
uv run --no-sync ruff check .
uv run --no-sync ruff format --check .
```

### PostgreSQL race-condition test

The ordinary suite uses isolated SQLite. A real PostgreSQL integration test is still required for simultaneous first-valid acceptance, row locking and transaction isolation.

### Live external API calls

OpenRouteService and Gemini were not called live because no user API keys were used. Their boundaries are tested without spending external API quota.

## Distribution note

All teammate ZIPs are slices of the same shared implementation. They are not separate architectures.
