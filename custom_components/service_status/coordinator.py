"""Data update coordinator for Service Status."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import StatusApiClient, StatusApiError
from .const import (
    CONF_SCAN_INTERVAL,
    CONF_URL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)
from .models import StatusData

_LOGGER = logging.getLogger(__name__)


class ServiceStatusCoordinator(DataUpdateCoordinator[StatusData]):
    """Polls the aggregated status endpoint."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        url: str = entry.options.get(CONF_URL) or entry.data[CONF_URL]
        scan = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        self.client = StatusApiClient(async_get_clientsession(hass), url)
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} ({entry.title})",
            update_interval=timedelta(seconds=scan),
        )

    async def _async_update_data(self) -> StatusData:
        try:
            return await self.client.async_fetch()
        except StatusApiError as err:
            raise UpdateFailed(str(err)) from err
