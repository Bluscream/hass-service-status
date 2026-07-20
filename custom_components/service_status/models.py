"""Data models for the Service Status integration."""

from __future__ import annotations

from dataclasses import dataclass, field

from .const import INDICATOR_SEVERITY


@dataclass(frozen=True)
class Incident:
    """One active incident or maintenance window."""

    service: str
    name: str | None = None
    impact: str | None = None
    status: str | None = None
    url: str | None = None
    started_at: str | None = None
    updated_at: str | None = None
    scheduled_until: str | None = None

    @classmethod
    def from_dict(cls, raw: dict) -> Incident:
        return cls(
            service=str(raw.get("service", "")),
            name=raw.get("name"),
            impact=raw.get("impact"),
            status=raw.get("status"),
            url=raw.get("url"),
            started_at=raw.get("started_at"),
            updated_at=raw.get("updated_at"),
            scheduled_until=raw.get("scheduled_until"),
        )

    def as_attribute(self) -> dict:
        return {
            k: v
            for k, v in {
                "name": self.name,
                "impact": self.impact,
                "status": self.status,
                "url": self.url,
                "started_at": self.started_at,
                "updated_at": self.updated_at,
                "scheduled_until": self.scheduled_until,
            }.items()
            if v is not None
        }


@dataclass(frozen=True)
class ServiceStatus:
    """Normalized status of one service."""

    slug: str
    name: str
    indicator: str | None = None
    status_text: str | None = None
    operational: bool | None = None
    updated_at: str | None = None
    page_url: str | None = None
    icon: str | None = None
    category: str | None = None
    active_incidents: int = 0
    maintenance: bool = False
    status_color: str | None = None
    service_color: str | None = None
    incidents: tuple[Incident, ...] = ()

    @classmethod
    def from_dict(cls, raw: dict, incidents: tuple[Incident, ...]) -> ServiceStatus:
        slug = str(raw.get("service") or raw.get("name") or "").lower()
        return cls(
            slug=slug,
            name=raw.get("name") or slug,
            indicator=raw.get("indicator"),
            status_text=raw.get("status"),
            operational=raw.get("operational"),
            updated_at=raw.get("updated_at"),
            page_url=raw.get("page_url"),
            icon=raw.get("icon"),
            category=raw.get("category"),
            active_incidents=int(raw.get("active_incidents") or 0),
            maintenance=bool(raw.get("maintenance")),
            status_color=raw.get("status_color"),
            service_color=raw.get("service_color"),
            incidents=incidents,
        )

    @property
    def severity(self) -> int:
        """Internal ranking of how badly this service is affected."""
        if self.indicator:
            ranked = INDICATOR_SEVERITY.get(self.indicator.lower())
            if ranked is not None:
                return ranked
        if self.operational is True:
            return 0
        if self.operational is False:
            return 2
        return -1


@dataclass
class StatusData:
    """Everything one poll returned."""

    services: dict[str, ServiceStatus] = field(default_factory=dict)
    incidents: tuple[Incident, ...] = ()
    lookup_time: str | None = None

    @property
    def worst_service(self) -> ServiceStatus | None:
        worst: ServiceStatus | None = None
        for service in self.services.values():
            if worst is None or service.severity > worst.severity:
                worst = service
        return worst
