# ZamLine Backend Team Ownership

This file is the merge-conflict boundary for the backend. The seven model files are shared contracts. A feature owner may read shared files, but shared files are changed only after the team agrees on the change and the matching migration/tests are prepared.

| Area | Owner | Primary files | Other features that consume it |
|---|---|---|---|
| Fleet Matching, Acceptance, Reservation, Contact Handoff | Shamy Umukundwa | `repositories/shipment_matches.py`, `repositories/reservations.py`, `schemas/shipment_matches.py`, `schemas/reservations.py`, `services/shipment_matches.py`, `services/reservations.py`, `routers/shipment_matches.py`, `routers/reservations.py` | Jesca reads matches; Sandra shipment status is updated on acceptance; Purity truck availability is updated on acceptance |
| User Registration, Secure Access, PACRA Verification | Helen Mezgebe | `repositories/users.py`, `repositories/companies.py`, `schemas/users.py`, `schemas/companies.py`, `services/users.py`, `services/companies.py`, `services/email_service.py`, `routers/users.py`, `routers/companies.py`, `security/passwords.py`, `security/tokens.py`, `security/otp.py` | Every protected feature uses authenticated user/company context |
| Route Information, Cost Estimation, AI Margin Decision Support | Jesca Amondi | `repositories/cost_estimation.py`, `schemas/routes.py`, `schemas/cost_estimation.py`, `services/routes.py`, `services/cost_estimation.py`, `routers/routes.py`, `routers/cost_estimation.py`, `integrations/openrouteservice.py`, `integrations/gemini.py` | Shamy displays the assessment attached to a match |
| Fleet Management, Private Operating Cost Settings | Purity Anyango | `repositories/trucks.py`, `repositories/cost_settings.py`, `schemas/trucks.py`, `schemas/cost_settings.py`, `services/trucks.py`, `services/cost_settings.py`, `routers/trucks.py`, `routers/cost_settings.py` | Matching reads available trucks; cost estimation reads truck/company cost inputs |
| Shipment Management, Cargo Validation | Sandra Twala | `repositories/shipments.py`, `schemas/shipments.py`, `services/shipments.py`, `routers/shipments.py` | Matching reads eligible open shipments; cost estimation reads shipment route/payment data |

## Shared files: coordination required

- `models/`
- `database.py`
- `dependency.py`
- `config.py`
- `main.py`
- `alembic/`
- `alembic.ini`
- `pyproject.toml`
- `.env.example`
- `repositories/audit_logs.py`
- `services/audit_logs.py`
- `.github/`

Shamy acts as integration lead for changes to shared wiring. Helen is the security lead for authentication/security changes. Jesca owns external route/AI integration details. No teammate should create a duplicate `Base`, database engine, auth dependency, or model.

## Shared model change rule

Before changing any model, write down:

1. Why the existing field/constraint cannot support the feature.
2. Which features are affected.
3. The Alembic migration needed.
4. The tests that must change.

Do not change a model only to make one feature branch easier.
