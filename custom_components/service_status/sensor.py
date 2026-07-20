"""Sensor entities for Service Status.

One enum sensor per monitored service plus one overall sensor. Services are
discovered from the poll data, and services that appear later are added on
the fly.
"""

from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import ServiceStatusConfigEntry
from .const import STATE_OPTIONS, STATE_SEVERITY, STATE_UNKNOWN
from .coordinator import ServiceStatusCoordinator
from .entity import ServiceStatusEntity
from .models import ServiceStatus


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ServiceStatusConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the overall sensor and one sensor per discovered service."""
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
            async_add_entities(
                StatusServiceSensor(coordinator, slug) for slug in new_slugs
            )

    async_add_entities([OverallStatusSensor(coordinator)])
    _sync_services()
    entry.async_on_unload(coordinator.async_add_listener(_sync_services))


class OverallStatusSensor(ServiceStatusEntity, SensorEntity):
    """Worst status across all monitored services."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = STATE_OPTIONS
    _attr_name = "Overall"
    _attr_icon = "mdi:server-network"

    def __init__(self, coordinator: ServiceStatusCoordinator) -> None:
        super().__init__(coordinator, "overall")

    @property
    def native_value(self) -> str:
        data = self.coordinator.data
        if data is None:
            return STATE_UNKNOWN
        return data.overall_state

    @property
    def extra_state_attributes(self) -> dict:
        data = self.coordinator.data
        if data is None:
            return {}
        counts: dict[str, int] = {}
        affected: list[str] = []
        for service in data.services.values():
            counts[service.state] = counts.get(service.state, 0) + 1
            if STATE_SEVERITY[service.state] > 0:
                affected.append(service.name)
        return {
            "services_total": len(data.services),
            "services_affected": sorted(affected),
            "counts": counts,
            "incidents": [inc.as_attribute() | {"service": inc.service} for inc in data.incidents],
            "lookup_time": data.lookup_time,
        }


class StatusServiceSensor(ServiceStatusEntity, SensorEntity):
    """Status of a single service."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = STATE_OPTIONS

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
        if service is None:
            return STATE_UNKNOWN
        return service.state

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
                "status": service.status_text,
                "indicator": service.indicator,
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
