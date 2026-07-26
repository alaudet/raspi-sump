"""Config flow for the Raspi-Sump integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_SSL,
    CONF_VERIFY_SSL,
)
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from . import build_base_url
from .api import RaspiSumpClient, RaspiSumpError, UnsupportedApiVersion
from .const import (
    CONF_PATH,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)
from .coordinator import RaspiSumpConfigEntry

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
        vol.Optional(CONF_SSL, default=False): cv.boolean,
        vol.Optional(CONF_VERIFY_SSL, default=True): cv.boolean,
        vol.Optional(CONF_PATH, default=""): cv.string,
    }
)


class RaspiSumpConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the Raspi-Sump config flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Ask for the address of the raspi-sump web UI and verify it answers."""
        errors: dict[str, str] = {}

        if user_input is not None:
            base_url = build_base_url(user_input)
            session = async_get_clientsession(
                self.hass, verify_ssl=user_input[CONF_VERIFY_SSL]
            )
            client = RaspiSumpClient(session, base_url)
            try:
                await client.async_get_status()
            except UnsupportedApiVersion:
                errors["base"] = "unsupported_version"
            except RaspiSumpError as err:
                _LOGGER.debug("Cannot connect to %s: %s", base_url, err)
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(base_url)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input[CONF_HOST], data=user_input
                )

        # Re-show the form pre-filled with whatever the user last typed, so a
        # typo in the host doesn't mean re-entering every field.
        schema = STEP_USER_DATA_SCHEMA
        if user_input is not None:
            schema = self.add_suggested_values_to_schema(schema, user_input)

        return self.async_show_form(
            step_id="user", data_schema=schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(entry: RaspiSumpConfigEntry) -> OptionsFlow:
        """Return the options flow."""
        return RaspiSumpOptionsFlow()


class RaspiSumpOptionsFlow(OptionsFlow):
    """Handle the Raspi-Sump options."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Let the user tune how often raspi-sump is polled."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        current = self.config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_SCAN_INTERVAL, default=current): vol.All(
                        vol.Coerce(int),
                        vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL),
                    )
                }
            ),
        )
