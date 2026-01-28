# Rate-Limiter Gateway

Small gateway service that will expose a `POST /check` endpoint to decide **allow/deny**
based on per-key token-bucket limits (coming in Day 2+). Day 1 sets up the FastAPI
skeleton, health endpoints, config, and request-ID logging.

## Tech
- FastAPI + Uvicorn
- Pydantic Settings for config (`.env`)
- Redis (to be wired in Day 2+)
- Request-ID middleware for traceability

## Quick Start (Dev)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./scripts/run_dev.sh
