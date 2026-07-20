"""Shared entity base for Service Status."""

from __future__ import annotations

from urllib.parse import urlparse

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ServiceStatusCoordinator


class ServiceStatusEntity(CoordinatorEntity[ServiceStatusCoordinator]):
    """Base entity that ties to the status device."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: ServiceStatusCoordinator, key: str) -> None:
        super().__init__(coordinator)
        entry = coordinator.entry
        parsed = urlparse(coordinator.client.url)
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer=parsed.hostname or "Status Lookup",
            model="Aggregated status page",
            configuration_url=f"{parsed.scheme}://{parsed.netloc}",
        )
