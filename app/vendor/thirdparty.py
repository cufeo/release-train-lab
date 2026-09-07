"""Vendored code that the path filter is supposed to EXCLUDE from backend CI.

Editing only this file should leave the backend jobs unselected. Under the broken
filter it selects them anyway; under the corrected filter it does not.
"""

VENDOR_VERSION = "1.0.0"
