"""Reproduces the settings-import chain that makes a runner-image smoke test fail.

This is a faithful reproduction of the *mechanism*, not a copy of any application:
an Environment is constructed at import time, and for every settings module except a
small allow-list it unpacks a JSON blob from an environment variable that is absent
from the checked-in example env file.
"""

import json
import os
import socket

# Settings modules that read secrets from a local file instead of the packed blob.
FILE_BACKED = ("local", "test", "build")


class Environment:
    def __init__(self):
        self.module = os.getenv("APP_SETTINGS", "app.settings.local")
        self.name = self.module.split(".")[-1]
        self.load_secrets()

    def load_secrets(self):
        if self.name in FILE_BACKED:
            self.load_env_file_secrets()
        else:
            self.load_packed_secrets()

    @staticmethod
    def load_env_file_secrets():
        return None

    def load_packed_secrets(self):
        # BLOCKER 1. get_secret returns the literal string "undefined" when unset,
        # and SECRETS is not present in .env.example, so this raises JSONDecodeError.
        packed = json.loads(self.get_secret("SECRETS"))
        for key, value in packed.items():
            os.environ[key] = value

    @staticmethod
    def get_secret(name, default="undefined"):
        return os.getenv(name, default)


def check_cache_reachable(host, port, timeout=2.0):
    """BLOCKER 2. An app-ready hook warms a cache before any check runs."""
    with socket.create_connection((host, port), timeout=timeout):
        return True


def check_credentials_present():
    """BLOCKER 3. The database engine resolves its password from a secrets manager."""
    if not os.getenv("CLOUD_CREDENTIALS"):
        raise RuntimeError(
            "UnrecognizedClientException: The security token included in the "
            "request is invalid (resolving database credentials)"
        )
    return True

STABILISATION_FIX = "found during rc1 soak"

HOTFIX_MARKER = True
