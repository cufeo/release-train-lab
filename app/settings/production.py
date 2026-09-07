"""Production settings. Warms a cache and resolves credentials in its ready hook."""

CACHE_BACKEND = "network"
CACHE_HOST = "cache.invalid"
CACHE_PORT = 6379
REQUIRE_CLOUD_CREDENTIALS = True
