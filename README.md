# Rate-Limiter Gateway

Small gateway service that will expose a `POST /check` endpoint to decide **allow/deny**
based on per-key token-bucket limits (coming in Day 2+). Day 1 sets up the FastAPI
skeleton, health endpoints, config, and request-ID logging.

## Tech
- FastAPI + Uvicorn
- Pydantic Settings for config (`.env`)
- Redis (to be wired in Day 2+)
- Request-ID middleware for traceability
- /api/check: decision-only (always 200)
- /api/enforce: enforcement (200/429), include Retry-After

## Design: Token Bucket (pure function)
- `capacity`: max tokens the bucket can hold.
- `refill_rate_per_sec`: tokens added per second (fractional OK).
- `try_consume(config, state, cost, now_s)`:
  - Refill to `now_s`, then attempt to deduct `cost`.
  - Returns `(Decision, new_state)`.
  - If `cost > capacity`: permanently denied (`retry_after_s=None`).
  - If not enough tokens: denied with `retry_after_s = (cost - tokens)/refill_rate_per_sec`.


## Quick Start (Dev)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./scripts/run_dev.sh
```

## Quick Start (Docker)
```bash
docker compose up --build
curl -i http://localhost:8000/healthz
curl -i -X POST http://localhost:8000/api/check -H 'content-type: application/json' -d '{"key":"u1","cost":1}'
```

## Endpoints
/healthz (liveness)
/api/readyz (readiness + Redis ping)
/api/check (token bucket decision + headers)
/metrics (Prometheus)

## Rate-limit headers

RateLimit-Limit
RateLimit-Remaining
RateLimit-Reset
Retry-After

## Runbook

If /api/readyz fails → Redis is down / wrong REDIS_URL
Check compose logs: docker compose logs -f gateway redis
Verify Redis healthy: docker compose ps
