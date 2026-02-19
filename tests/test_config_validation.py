import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_rejects_non_positive_capacity():
    with pytest.raises(ValidationError):
        Settings(BUCKET_CAPACITY=0)


def test_rejects_non_positive_refill_rate():
    with pytest.raises(ValidationError):
        Settings(BUCKET_REFILL_RATE_PER_SEC=0)


def test_rejects_negative_ttl():
    with pytest.raises(ValidationError):
        Settings(BUCKET_KEY_TTL_SEC=-1)


def test_rejects_negative_body_limit():
    with pytest.raises(ValidationError):
        Settings(MAX_BODY_BYTES=-1)
