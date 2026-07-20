"""Constants for the Service Status integration."""

from __future__ import annotations

DOMAIN = "service_status"

PLATFORMS = ["sensor"]

# Config keys
CONF_URL = "url"
CONF_NAME = "name"

# Options keys
CONF_SCAN_INTERVAL = "scan_interval"

# Defaults
DEFAULT_NAME = "Service Status"
DEFAULT_URL = "https://lookup.minopia.de/api/status/all?wait=true"
DEFAULT_SCAN_INTERVAL = 900  # 15 min; status pages update slowly
MIN_SCAN_INTERVAL = 60

# Request timeout: generous because ?wait=true blocks until fresh data exists.
REQUEST_TIMEOUT = 90

# Fallback state when the API reports no status text for a service.
STATE_UNKNOWN = "Unknown"
