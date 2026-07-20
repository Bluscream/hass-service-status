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

# Normalized severity values (exposed as the "severity" attribute; the
# sensor state itself is the raw status text from the API)
STATE_ALL_OPERATIONAL = "All Operational"
STATE_MAINTENANCE = "Maintenance"
STATE_MINOR_OUTAGE = "Minor Outage"
STATE_MAJOR_OUTAGE = "Major Outage"
STATE_TOTAL_OUTAGE = "Total Outage"
STATE_UNKNOWN = "Unknown"

# Rank used to pick the worst state for the overall sensor.
STATE_SEVERITY = {
    STATE_UNKNOWN: -1,
    STATE_ALL_OPERATIONAL: 0,
    STATE_MAINTENANCE: 1,
    STATE_MINOR_OUTAGE: 2,
    STATE_MAJOR_OUTAGE: 3,
    STATE_TOTAL_OUTAGE: 4,
}

# Upstream "indicator" values mapped onto our states.
INDICATOR_TO_STATE = {
    "none": STATE_ALL_OPERATIONAL,
    "operational": STATE_ALL_OPERATIONAL,
    "maintenance": STATE_MAINTENANCE,
    "minor": STATE_MINOR_OUTAGE,
    "major": STATE_MAJOR_OUTAGE,
    "critical": STATE_TOTAL_OUTAGE,
    "offline": STATE_TOTAL_OUTAGE,
}
