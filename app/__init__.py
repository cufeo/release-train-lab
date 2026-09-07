"""Importing the package constructs the Environment, exactly as a celery module would.

This is why the smoke test fails before the settings module is ever reached: the
failure happens at package import, not at settings import.
"""

from .config import Environment

env = Environment()
