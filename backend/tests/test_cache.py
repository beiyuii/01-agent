import time

from app.utils.cache import TTLCache


def test_cache_set_and_expire():
    cache = TTLCache(ttl_seconds=1)
    cache.set("foo", "bar")
    assert cache.get("foo") == "bar"
    time.sleep(1.1)
    assert cache.get("foo") is None
    stats = cache.stats()
    assert stats["hits"] == 1
    assert stats["misses"] == 1


def test_cache_clear():
    cache = TTLCache(ttl_seconds=10)
    cache.set("foo", 123)
    cache.clear()
    assert cache.get("foo") is None
    stats = cache.stats()
    assert stats["hits"] == 0
    assert stats["misses"] == 1
