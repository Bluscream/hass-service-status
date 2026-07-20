"""Config and options flow for Service Status."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .api import CannotConnect, InvalidData, StatusApiClient
from .const import (
    CONF_NAME,
    CONF_SCAN_INTERVAL,
    CONF_URL,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_URL,
    DOMAIN,
    MIN_SCAN_INTERVAL,
)

_URL_SELECTOR = TextSelector(TextSelectorConfig(type=TextSelectorType.URL))
_INTERVAL_SELECTOR = NumberSelector(
    NumberSelectorConfig(
        min=MIN_SCAN_INTERVAL,
        max=86400,
        step=1,
        unit_of_measurement="s",
        mode=NumberSelectorMode.BOX,
    )
)


class ServiceStatusConfigFlow(ConfigFlow, domain=DOMAIN):
    """One entry per status endpoint."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            url = user_input[CONF_URL].strip()
            await self.async_set_unique_id(url)
            self._abort_if_unique_id_configured()
            client = StatusApiClient(async_get_clientsession(self.hass), url)
            try:
                await client.async_fetch()
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidData:
                errors["base"] = "invalid_data"
            else:
                return self.async_create_entry(
                    title=user_input.get(CONF_NAME) or DEFAULT_NAME,
                    data={CONF_URL: url},
                    options={
                        CONF_SCAN_INTERVAL: int(
                            user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
                        )
                    },
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_URL, default=DEFAULT_URL): _URL_SELECTOR,
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
                vol.Required(
                    CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                ): _INTERVAL_SELECTOR,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return ServiceStatusOptionsFlow()


class ServiceStatusOptionsFlow(OptionsFlow):
    """Adjust URL and polling interval."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        entry = self.config_entry
        if user_input is not None:
            url = user_input[CONF_URL].strip()
            client = StatusApiClient(async_get_clientsession(self.hass), url)
            try:
                await client.async_fetch()
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidData:
                errors["base"] = "invalid_data"
            else:
                return self.async_create_entry(
                    data={
                        CONF_URL: url,
                        CONF_SCAN_INTERVAL: int(user_input[CONF_SCAN_INTERVAL]),
                    }
                )

        current_url = entry.options.get(CONF_URL) or entry.data[CONF_URL]
        current_scan = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        schema = vol.Schema(
            {
                vol.Required(CONF_URL, default=current_url): _URL_SELECTOR,
                vol.Required(
                    CONF_SCAN_INTERVAL, default=current_scan
                ): _INTERVAL_SELECTOR,
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema, errors=errors)
