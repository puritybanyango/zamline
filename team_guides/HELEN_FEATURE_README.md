# Feature README: Helen Mezgebe

## Owns
- F-03 User Registration and Secure Access
- F-04 PACRA Business Verification

## Owned files
- `repositories/users.py`
- `repositories/companies.py`
- `schemas/users.py`
- `schemas/companies.py`
- `services/users.py`
- `services/companies.py`
- `services/email_service.py`
- `routers/users.py`
- `routers/companies.py`
- `security/passwords.py`
- `security/tokens.py`
- `security/otp.py`
- auth/verification tests

## Uses shared contracts
- `models/users.py`
- `models/companies.py`
- `models/audit_logs.py`
- `dependency.py`
- `services/audit_logs.py`

## Important behavior
Passwords are hashed with Argon2 through the password helper. OTP codes are short-lived, single-use and attempt-limited. Business verification does not invent a PACRA API; the service stores submission/result metadata and exposes the verification state used by feature gates.

## OTP deployment note
The current OTP store is process memory so the seven-table database remains unchanged. It is fine for local/single-process MVP work, but multiple dynos need a shared TTL store behind the same boundary.

## Do not change without coordination
`models/`, `database.py`, `main.py`, `alembic/`, `pyproject.toml`, or another feature owner's files.

## Test
```bash
uv run --no-sync pytest tests/test_auth_feature.py tests/test_users.py tests/test_companies.py
```
