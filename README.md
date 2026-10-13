# ZamLine Backend

ZamLine is the Team Nexa freight coordination and decision-support backend.

## Stack

- Python 3.11
- FastAPI
- SQLAlchemy classic `Column` style
- PostgreSQL in deployed environments
- SQLite for isolated ordinary tests
- Alembic migrations
- OpenRouteService for HGV route information
- Gemini for AI-assisted explanation after deterministic cost calculation

## Set up

```bash
uv venv
uv pip install -r pyproject.toml --group dev
cp .env.example .env
```

Set at minimum a database URL and JWT secret. External feature keys are required only when those integrations are exercised.

Apply migrations:

```bash
uv run --no-sync alembic upgrade head
```

Run the API:

```bash
uv run --no-sync uvicorn main:app --reload
```

Swagger is available at `http://localhost:8000/docs`.

## Checks

```bash
uv run --no-sync ruff check .
uv run --no-sync ruff format --check .
uv run --no-sync pytest --cov --cov-report=term-missing
```

Read `TEAM_OWNERSHIP.md`, `TEAM_INTEGRATION_GUIDE.md` and `TESTING_GUIDE.md` before editing shared files.
