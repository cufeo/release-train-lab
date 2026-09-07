"""The fix, and it already existed in the real codebase.

Inherits production wholesale, then overrides only the two things that require live
infrastructure. The full import chain still executes, so the smoke test keeps its
whole purpose: catching a dependency that resolves in the CI image but not the
slim runtime image.
"""

from .production import *  # noqa: F401,F403

CACHE_BACKEND = "dummy"
REQUIRE_CLOUD_CREDENTIALS = False
