"""Development settings — still reads the packed secrets blob, like every
settings module outside the file-backed allow-list."""

CACHE_BACKEND = "network"
CACHE_HOST = "cache.invalid"
CACHE_PORT = 6379
REQUIRE_CLOUD_CREDENTIALS = False
