"""Client for the status lookup API."""

from __future__ import annotations

import asyncio
import logging

import aiohttp

from .const import REQUEST_TIMEOUT
from .models import Incident, ServiceStatus, StatusData

_LOGGER = logging.getLogger(__name__)


class StatusApiError(Exception):
    """Base error for the status API."""


class CannotConnect(StatusApiError):
    """Network-level failure talking to the API."""


class InvalidData(StatusApiError):
    """The API answered but the payload is not usable."""


class StatusApiClient:
    """Fetches and parses the aggregated status endpoint."""

    def __init__(self, session: aiohttp.ClientSession, url: str) -> None:
        self._session = session
        self._url = url

    @property
    def url(self) -> str:
        return self._url

    async def async_fetch(self) -> StatusData:
        try:
            async with asyncio.timeout(REQUEST_TIMEOUT):
                resp = await self._session.get(self._url)
                resp.raise_for_status()
                payload = await resp.json(content_type=None)
        except (TimeoutError, aiohttp.ClientError) as err:
            raise CannotConnect(f"Error fetching {self._url}: {err}") from err
        except ValueError as err:
            raise InvalidData(f"Response from {self._url} is not JSON: {err}") from err
        return self.parse_payload(payload)

    @staticmethod
    def parse_payload(payload: dict) -> StatusData:
        if not isinstance(payload, dict):
            raise InvalidData("Payload is not a JSON object")
        if payload.get("success") is False:
            raise InvalidData(f"API reported failure: {payload.get('errors')}")

        # The endpoint wraps its data in "response"; accept a bare
        # {services, incidents} object too so other hosts of the API work.
        body = payload.get("response", payload)
        raw_services = body.get("services")
        if not isinstance(raw_services, list):
            raise InvalidData("Payload has no 'services' list")

        incidents = tuple(
            Incident.from_dict(item)
            for item in body.get("incidents") or []
            if isinstance(item, dict)
        )

        services: dict[str, ServiceStatus] = {}
        for item in raw_services:
            if not isinstance(item, dict):
                continue
            slug = str(item.get("service") or item.get("name") or "").lower()
            if not slug:
                continue
            own_incidents = tuple(i for i in incidents if i.service == slug)
            services[slug] = ServiceStatus.from_dict(item, own_incidents)
        services = dict(sorted(services.items(), key=lambda kv: kv[1].name.lower()))

        return StatusData(
            services=services,
            incidents=incidents,
            lookup_time=payload.get("lookup_time"),
        )
