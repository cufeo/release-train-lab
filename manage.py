#!/usr/bin/env python3
"""Stands in for `manage.py check` — the command the runner-image smoke test runs.

Run it the way CI does:

    APP_SETTINGS=app.settings.production python manage.py check

With no SECRETS set this dies at package import, before any settings module loads.
Set APP_BUILD_OVERRIDES=1 to apply the build-settings overrides on top of whichever
module is named — the same two overrides, against the real import chain.
"""

import importlib
import os
import sys

import app  # noqa: F401  — constructing the Environment happens here
from app.config import check_cache_reachable, check_credentials_present


def check():
    module = os.getenv("APP_SETTINGS", "app.settings.local")
    settings = importlib.import_module(module)

    cache_backend = getattr(settings, "CACHE_BACKEND", "dummy")
    needs_credentials = getattr(settings, "REQUIRE_CLOUD_CREDENTIALS", False)

    if os.getenv("APP_BUILD_OVERRIDES") == "1":
        cache_backend = "dummy"
        needs_credentials = False

    if cache_backend != "dummy":
        check_cache_reachable(settings.CACHE_HOST, settings.CACHE_PORT)

    if needs_credentials:
        check_credentials_present()

    print(f"System check identified no issues (0 silenced).  [{module}]")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] != "check":
        sys.exit("usage: manage.py check")
    check()
