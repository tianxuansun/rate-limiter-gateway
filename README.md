# Rate-Limiter Gateway (Redis Token Bucket)

A production-style rate limiting gateway that implements **token-bucket throttling per key** backed by Redis (atomic Lua script).

It exposes two APIs:

- `POST /api/check` → **decision-only** (always returns `200 OK`)
- `POST /api/enforce` → **enforcement** (`200 OK` or `429 Too Many Requests`)

Includes Prometheus metrics, readiness/version endpoints, request tracing headers, Docker Compose, CI, and tests.

---

## Key Features

- **Atomic rate limiting** via Redis **Lua** (safe under concurrency and multi-instance deployments)
- **Standard-ish RateLimit headers** + `Retry-After` support
- **TTL** for bucket keys to prevent unbounded Redis growth
- **Observability**: Prometheus `/metrics`, request IDs, decision metrics
- **Gateway guardrails**: request body size limit (`413 Payload Too Large`)
- **Developer experience**: Docker Compose, Makefile, Postman collection, k6 load test
- **Quality**: Ruff format/lint, pytest, CI, Docker build in GitHub Actions

---

## Endpoints

- `GET /healthz` — liveness (process up)
- `GET /metrics` — Prometheus scrape
- `GET /api/readyz` — readiness (Redis ping)
- `GET /api/version` — version/build metadata
- `POST /api/check` — decision-only (always `200`)
- `POST /api/enforce` — enforced (`200` or `429` when denied)

---

## Response Headers

Returned on `/api/check` and `/api/enforce`:

- `RateLimit-Limit`
- `RateLimit-Remaining`
- `RateLimit-Reset`
- `Retry-After` (only when denied)

Debug headers:

- `X-RateLimit-Decision: allowed|denied|impossible`
- `RateLimit-Reason: insufficient_tokens|cost_exceeds_capacity` (only when not allowed)

---

## Configuration (Environment Variables)

### Common

- `REDIS_URL` (default: `redis://localhost:6379/0`)
- `REDIS_KEY_PREFIX` (default: `bucket:`)

### Token Bucket Defaults

- `BUCKET_CAPACITY` (default: `5`)
- `BUCKET_REFILL_RATE_PER_SEC` (default: `1`)
- `BUCKET_KEY_TTL_SEC` (default: `3600`)

### Gateway Guardrails

- `MAX_BODY_BYTES` (default: `32768`)

---

# Quick Start

## Docker

Start the stack:

```bash
docker compose up --build
```

Sanity check:

```bash
curl -i http://localhost:8000/healthz
curl -i http://localhost:8000/api/version
curl -i http://localhost:8000/api/readyz
```

### Decision-only

```bash
curl -i -X POST http://localhost:8000/api/check \
  -H 'content-type: application/json' \
  -d '{"key":"user-123","cost":1}'
```

### Enforced

Trigger a `429` by draining the bucket and calling again immediately:

```bash
curl -i -X POST http://localhost:8000/api/enforce \
  -H 'content-type: application/json' \
  -d '{"key":"demo","cost":5}'

curl -i -X POST http://localhost:8000/api/enforce \
  -H 'content-type: application/json' \
  -d '{"key":"demo","cost":1}'
```

Stop:

```bash
docker compose down --remove-orphans
```

---

## Dev (Local)

```bash
python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
pip install -r requirements-dev.txt

./scripts/run_dev.sh
```

---

## Integration

### Postman

A Postman collection is included:

```
postman/RateLimiterGateway.postman_collection.json
```

Set `baseUrl` to your running server (default: `http://localhost:8000`).

---

## Load Testing (k6)

Run the included benchmark:

```bash
make k6
```

Optional overrides:

```bash
BASE_URL=http://localhost:8000 VUS=50 DURATION=30s k6 run load/k6_check.js
```

> Note: Results vary by environment (WSL vs native Linux, Docker Desktop, CPU load).

---

## Development Commands

```bash
make format   # ruff format + ruff check
make lint     # ruff check
make test     # pytest
make up       # docker compose up --build
make down     # docker compose down --remove-orphans
```

---

## Repository Structure

```
app/                     # FastAPI app, routes, middleware, Redis client, rate limiter logic
tests/                   # unit + endpoint tests
load/                    # k6 benchmark
postman/                 # Postman collection
.github/workflows/       # CI (format/lint/tests + docker build)
```
