# Rate-Limiter Gateway

A small gateway service that implements **token-bucket rate limiting per key** backed by Redis.
It exposes:
- `POST /api/check` → **decision-only** (always 200)
- `POST /api/enforce` → **enforcement** (200 or 429)

Includes Prometheus metrics, readiness checks, request IDs, and Docker Compose for local runs.

## Tech
- FastAPI + Uvicorn
- Redis + Lua script (atomic token bucket)
- Prometheus `/metrics`
- GitHub Actions CI
- Docker / Docker Compose

## Endpoints
- `GET /healthz` — liveness
- `GET /metrics` — Prometheus scrape
- `POST /api/check` — decision-only (always 200)
- `POST /api/enforce` — enforcement (200 or 429)
- `GET /api/readyz` — readiness (Redis ping)
- `GET /api/version` — build metadata

## Rate-limit headers
Returned on `/api/check` and `/api/enforce`:
- `RateLimit-Limit`
- `RateLimit-Remaining`
- `RateLimit-Reset`
- `Retry-After` (only when denied)

Additional debug headers:
- `X-RateLimit-Decision: allowed|denied|impossible`
- `RateLimit-Reason: insufficient_tokens|cost_exceeds_capacity` (only when not allowed)

## Request size limit
Gateway rejects oversized API requests with `413 Payload Too Large`.
Config: `MAX_BODY_BYTES` (default `32768`).

## Integration
A Postman collection is available at:
- `postman/RateLimiterGateway.postman_collection.json`

Set `baseUrl` to your running server (default `http://localhost:8000`).

## Performance (local)
Run the included k6 test:
```bash
make k6


## Quick Start (Dev)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
./scripts/run_dev.sh

