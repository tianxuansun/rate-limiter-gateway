import math
from app.ratelimit.token_bucket import BucketConfig, BucketState, try_consume

T0 = 1_000.0  # arbitrary epoch seconds


def test_refill_to_capacity_over_time():
    cfg = BucketConfig(capacity=5.0, refill_rate_per_sec=1.0)
    s0 = BucketState(tokens=0.0, last_refill_ts=T0)

    # After 3 seconds: 3 tokens (not capped yet)
    d, s1 = try_consume(cfg, s0, cost=0.0, now_s=T0 + 3.0)
    assert d.allowed is True
    assert math.isclose(s1.tokens, 3.0, rel_tol=1e-9)

    # After 10 seconds total: should be capped at 5
    d, s2 = try_consume(cfg, s1, cost=0.0, now_s=T0 + 10.0)
    assert math.isclose(s2.tokens, 5.0, rel_tol=1e-9)


def test_allows_when_enough_tokens():
    cfg = BucketConfig(capacity=3.0, refill_rate_per_sec=100.0)  # high rate to isolate
    s0 = BucketState(tokens=3.0, last_refill_ts=T0)

    d, s1 = try_consume(cfg, s0, cost=2.0, now_s=T0)
    assert d.allowed is True
    assert math.isclose(d.remaining_tokens, 1.0, rel_tol=1e-9)
    assert math.isclose(s1.tokens, 1.0, rel_tol=1e-9)
    assert math.isclose(d.retry_after_s, 0.0, rel_tol=1e-9)


def test_denies_when_insufficient_tokens_and_returns_retry_after():
    cfg = BucketConfig(capacity=5.0, refill_rate_per_sec=2.0)  # 2 tokens/sec
    s0 = BucketState(tokens=1.0, last_refill_ts=T0)

    # Need cost=3, currently 1 token → short by 2 → 2/2 = 1s
    d, s1 = try_consume(cfg, s0, cost=3.0, now_s=T0)
    assert d.allowed is False
    assert math.isclose(d.remaining_tokens, 1.0, rel_tol=1e-9)
    assert math.isclose(d.retry_after_s, 1.0, rel_tol=1e-9)
    # State shouldn't change on deny
    assert math.isclose(s1.tokens, 1.0, rel_tol=1e-9)


def test_partial_refill_then_consume():
    cfg = BucketConfig(capacity=10.0, refill_rate_per_sec=2.0)
    s0 = BucketState(tokens=0.0, last_refill_ts=T0)

    # After 0.5s → 1 token
    d, s1 = try_consume(cfg, s0, cost=0.0, now_s=T0 + 0.5)
    assert math.isclose(s1.tokens, 1.0, rel_tol=1e-9)

    # Try to spend 1.0 now → should allow and go to 0.0
    d, s2 = try_consume(cfg, s1, cost=1.0, now_s=T0 + 0.5)
    assert d.allowed is True
    assert math.isclose(s2.tokens, 0.0, rel_tol=1e-9)


def test_cost_greater_than_capacity_is_permanent_deny():
    cfg = BucketConfig(capacity=1.0, refill_rate_per_sec=10.0)
    s0 = BucketState(tokens=1.0, last_refill_ts=T0)
    d, s1 = try_consume(cfg, s0, cost=2.0, now_s=T0)
    assert d.allowed is False
    assert d.retry_after_s is None
    # No state change on deny
    assert math.isclose(s1.tokens, 1.0, rel_tol=1e-9)


def test_zero_cost_is_noop_and_allowed():
    cfg = BucketConfig(capacity=3.0, refill_rate_per_sec=1.0)
    s0 = BucketState(tokens=2.0, last_refill_ts=T0)
    d, s1 = try_consume(cfg, s0, cost=0.0, now_s=T0 + 5.0)
    # It refills during the call; capacity cap applies
    assert d.allowed is True
    assert math.isclose(s1.tokens, 3.0, rel_tol=1e-9)
    assert math.isclose(d.remaining_tokens, 3.0, rel_tol=1e-9)
