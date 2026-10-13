# ZamLine Backend Testing Guide

## Local checks

Install from the project source of truth:

```bash
uv venv
uv pip install -r pyproject.toml --group dev
```

Run:

```bash
uv run --no-sync ruff check .
uv run --no-sync ruff format --check .
uv run --no-sync pytest --cov --cov-report=term-missing
```

## Test database

Normal tests use an isolated in-memory SQLite database with foreign keys enabled. They must never point at a shared development or production PostgreSQL database.

SQLite is suitable here for:

- model persistence and basic constraints
- repository filtering
- ordinary service behavior
- tenant-scoping logic
- validation and state transitions
- deterministic cost calculation
- mocking ORS and Gemini boundaries

## PostgreSQL-only confidence

SQLite does not prove PostgreSQL transaction behavior. Before production acceptance, add an isolated PostgreSQL integration test for:

- two Fleet Managers attempting the same shipment at nearly the same time
- `SELECT ... FOR UPDATE` behavior
- one successful reservation per shipment
- unique-constraint fallback behavior
- transaction rollback after the losing acceptance

The test must show that exactly one reservation is created and only one match becomes accepted.

## External integrations

Unit tests must mock OpenRouteService and Gemini. Do not spend real API quota in the normal test suite.

For a manual ORS integration smoke test, verify:

- profile is `driving-hgv`
- payload coordinate order is longitude then latitude
- returned metres are converted to kilometres once
- returned seconds are converted to minutes once

For Gemini, verify separately that:

- missing configuration does not break deterministic cost calculation
- an expired/missing remote file is re-uploaded from the original Markdown file
- invalid remote references are never reused
- model output cannot change IDs, authorization, match decisions or reservations

## Security regression checks

Every protected feature should test at least:

- unauthenticated request rejected
- wrong role rejected
- wrong company cannot read another company's resource
- unverified company cannot perform verified-business actions
- private cost settings remain fleet-company scoped
- contact details are unavailable without a valid reservation
