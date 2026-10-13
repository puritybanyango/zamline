# ZamLine Backend Integration Guide

## Implementation order

1. Shared foundation: database configuration, Alembic, dependencies, security helpers, audit helper.
2. Helen: registration, login, OTP boundary, company verification submission.
3. Purity and Sandra can work in parallel: fleet/truck/cost settings and shipment/cargo flows.
4. Jesca: OpenRouteService and deterministic/AI cost assessment.
5. Shamy: matching, acceptance, reservation, contact handoff integration.
6. Full regression, PostgreSQL-specific acceptance tests, peer review, merge.

## Branch dependency plan

Recommended feature branches:

- `feature/auth-verification`
- `feature/fleet-management`
- `feature/shipment-management`
- `feature/route-cost-estimation`
- `feature/fleet-matching`

Each feature branch should start from the latest `develop` after the shared foundation is merged. Purity and Sandra can work in parallel. Jesca depends on shipment and truck/cost-setting contracts. Shamy depends on the stable shipment, truck, security and cost-assessment contracts.

## Shared API contracts

### Authentication and verification

- `POST /users/register`
- `POST /users/verify-otp`
- `POST /users/resend-otp`
- `POST /users/login`
- `GET /companies/me`
- `POST /companies/me/verification`

Protected endpoints use the shared bearer-token dependency. Verified-business actions also use `require_verified_company`.

### Fleet management

- `POST /trucks`
- `GET /trucks`
- `GET /trucks/{truck_id}`
- `PATCH /trucks/{truck_id}`
- `GET /cost-settings`
- `PATCH /cost-settings`

Truck records are always scoped to the authenticated Fleet Manager's company. Private operating costs are never returned through Shipper endpoints.

### Shipment management

- `POST /shipments`
- `GET /shipments`
- `GET /shipments/{shipment_id}`
- `POST /shipments/{shipment_id}/cancel`

Cargo validation happens before a shipment is published. The approved unaccepted-cargo values are configured through `UNACCEPTED_CARGO_TYPES`.

### Matching and acceptance

- `POST /shipment-matches/refresh`
- `GET /shipment-matches`
- `POST /shipment-matches/{match_id}/decision`
- `GET /reservations/{reservation_id}`
- `GET /reservations/{reservation_id}/contact`

Matching uses kilograms, required body type and truck availability. Acceptance locks the shipment row on PostgreSQL, creates one reservation, confirms the shipment, closes competing pending matches and makes the accepted truck unavailable.

### Route and cost assessment

- `GET /routes/{match_id}`
- `POST /cost-estimation/{match_id}`

OpenRouteService receives route coordinates only. Coordinates are sent in `[longitude, latitude]` order using `driving-hgv`.

The deterministic cost calculation is the trusted baseline. Gemini only explains the already-calculated result. Gemini cannot accept a shipment or create a reservation.

## Status contracts

Shipment:

- `open`
- `confirmed`
- `cancelled`
- `expired`

Match decision:

- `pending`
- `accepted`
- `declined`
- `closed`

Financial outcome:

- `profit`
- `loss`
- `break_even`

Reservation:

- `accepted`
- `cancelled`

Verification:

- `pending`
- `verified`
- `resubmit`
- `rejected`

## Shared helper contracts

- `dependency.get_current_user`: authenticated active user.
- `dependency.get_current_company`: authenticated user's company.
- `dependency.require_role(...)`: backend role enforcement.
- `dependency.require_verified_company`: company verification gate.
- `services.audit_logs.record_event(...)`: cross-cutting audit helper.
- `integrations.openrouteservice.get_hgv_route(...)`: route provider boundary.
- `integrations.gemini.explain_cost_assessment(...)`: AI explanation boundary.

## Merge-conflict avoidance

- Do not edit another owner's service/repository to add convenience logic. Ask for a small public helper or contract instead.
- Do not put queries in routers.
- Do not copy authentication checks into feature services.
- Do not create another `dependencies.py`; the current project uses `dependency.py`.
- Do not create new tables without a team-approved shared model change.
- Keep external API clients inside `integrations/`.
- Update tests in the same PR as Python feature changes.

## OTP production boundary

The included OTP store is short-lived, single-use, attempt-limited and intentionally kept outside the seven-table database. It is process memory, so it is appropriate for local/single-process MVP work but is not multi-instance durable. Before running multiple Heroku dynos, replace only the OTP storage boundary with a shared TTL store while keeping the service/router contract unchanged.

## Gemini reference-file boundary

Approved Markdown reference files remain in server-side storage under `reference_data/` or another configured path. Runtime Gemini file metadata is written to `data/gemini_file_state.json`. Before use, the integration checks the remote file reference and re-uploads the original file when the reference is no longer available.

## Integration test order

1. Registration and email verification.
2. Login and protected endpoint access.
3. Company verification gate.
4. Fleet truck/cost-setting ownership.
5. Shipment creation and cargo rejection.
6. Match generation from open shipment + available compatible truck.
7. Route lookup and deterministic cost calculation.
8. AI explanation failure/success behavior.
9. Acceptance and reservation.
10. Contact handoff.
11. PostgreSQL simultaneous-acceptance race test.
