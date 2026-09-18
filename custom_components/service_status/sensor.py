"""Sensor entities for Service Status.

One sensor per monitored service. The state is the raw status text reported
by the API (e.g. "All Systems Operational"). Services are discovered from
the poll data, and services that appear later are added on the fly.
"""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import ServiceStatusConfigEntry
from .const import STATE_UNKNOWN
from .coordinator import ServiceStatusCoordinator
from .entity import ServiceStatusEntity
from .models import ServiceStatus


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ServiceStatusConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up one sensor per discovered service."""
    coordinator = entry.runtime_data
    known: set[str] = set()

    @callback
    def _sync_services() -> None:
        data = coordinator.data
        if data is None:
            return
        new_slugs = [slug for slug in data.services if slug not in known]
        if new_slugs:
            known.update(new_slugs)
            async_add_entities(StatusServiceSensor(coordinator, slug) for slug in new_slugs)

    _sync_services()
    entry.async_on_unload(coordinator.async_add_listener(_sync_services))


class StatusServiceSensor(ServiceStatusEntity, SensorEntity):
    """Status of a single service."""

    def __init__(self, coordinator: ServiceStatusCoordinator, slug: str) -> None:
        super().__init__(coordinator, slug)
        self._slug = slug
        service = self._service
        self._attr_name = service.name if service else slug.title()

    @property
    def _service(self) -> ServiceStatus | None:
        data = self.coordinator.data
        if data is None:
            return None
        return data.services.get(self._slug)

    @property
    def available(self) -> bool:
        return super().available and self._service is not None

    @property
    def native_value(self) -> str:
        service = self._service
        if service is None or not service.status_text:
            return STATE_UNKNOWN
        return service.status_text

    @property
    def entity_picture(self) -> str | None:
        service = self._service
        return service.icon if service else None

    @property
    def extra_state_attributes(self) -> dict:
        service = self._service
        if service is None:
            return {}
        return {
            k: v
            for k, v in {
                "operational": service.operational,
                "maintenance": service.maintenance,
                "category": service.category,
                "page_url": service.page_url,
                "active_incidents": service.active_incidents,
                "incidents": [inc.as_attribute() for inc in service.incidents],
                "status_color": service.status_color,
                "service_color": service.service_color,
                "updated_at": service.updated_at,
            }.items()
            if v is not None
        }
