from app.rate_limit import RateLimiter


def test_rate_limit_resets_after_window():
    limiter = RateLimiter(limit=2, window_seconds=10)
    assert limiter.allow("client-a", 0)
    assert limiter.allow("client-a", 1)
    assert not limiter.allow("client-a", 2)
    assert limiter.allow("client-b", 2)
    assert limiter.allow("client-a", 11)


def test_zero_limit_disables_limiter():
    limiter = RateLimiter(limit=0)
    assert all(limiter.allow("client", 0) for _ in range(100))
