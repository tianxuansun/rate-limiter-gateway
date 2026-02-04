import time
from prometheus_client import Counter, Histogram

# --- Request-level ---
HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)

HTTP_REQUEST_LATENCY_SECONDS = Histogram(
    "http_request_latency_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
)

# --- Rate limiter specific ---
RATE_LIMIT_CHECKS_TOTAL = Counter(
    "rate_limit_checks_total",
    "Total /api/check calls by decision",
    ["result"],  # "allowed" | "denied" | "impossible"
)

RATE_LIMIT_REDIS_ERRORS_TOTAL = Counter(
    "rate_limit_redis_errors_total",
    "Total Redis errors while processing /api/check",
)

RATE_LIMIT_DECISION_LATENCY_SECONDS = Histogram(
    "rate_limit_decision_latency_seconds",
    "Latency for Redis token-bucket decision",
)

def now_s() -> float:
    return time.time()

def monotonic_s() -> float:
    return time.perf_counter()
