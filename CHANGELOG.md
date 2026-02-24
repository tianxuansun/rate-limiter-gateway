# Changelog

## v0.2.0 (Day 9)
- Added release polish: OpenAPI examples, integration artifacts, and benchmark notes.

## v0.1.0
- Redis-backed token-bucket rate limiter (Lua atomic updates).
- Endpoints: /api/check (decision-only) and /api/enforce (429 on deny).
- RateLimit headers + Retry-After.
- Prometheus metrics (/metrics) and request-ID middleware.
- Readiness (/api/readyz) and version (/api/version).
- Dockerfile + docker-compose + GitHub Actions CI.
- TTL for bucket keys and request body size limit middleware.
