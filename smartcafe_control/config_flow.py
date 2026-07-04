"""Config flow for SmartCafe Control integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult, OptionsFlow, ConfigEntry
from homeassistant.core import callback

from .const import (
    CONF_PING_COUNT,
    CONF_SCAN_INTERVAL,
    DEFAULT_PING_COUNT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

DEVICE_SENSOR_ENTITY = "sensor.smartcafe_devices"


class SmartCafeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SmartCafe Control."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> SmartCafeOptionsFlow:
        """Get the options flow for this handler."""
        return SmartCafeOptionsFlow()

    def __init__(self) -> None:
        """Initialize config flow."""
        self._devices: list[dict] = []

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Step 1: Show intro and detect devices."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                state = self.hass.states.get(DEVICE_SENSOR_ENTITY)
                if state is None:
                    errors["base"] = "no_sensor_found"
                else:
                    devices = state.attributes.get("devices", [])
                    if not devices:
                        errors["base"] = "no_devices_found"
                    else:
                        self._devices = devices
                        return await self.async_step_devices()
            except Exception as e:
                _LOGGER.error("SmartCafe config flow error: %s", e)
                errors["base"] = "no_sensor_found"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
            errors=errors,
            description_placeholders={
                "entity_id": DEVICE_SENSOR_ENTITY,
            },
        )

    async def async_step_devices(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Step 2: Select devices to import."""
        errors: dict[str, str] = {}

        if user_input is not None:
            selected_ips = user_input.get("devices", [])
            if not selected_ips:
                errors["devices"] = "no_devices_selected"
            else:
                for device in self._devices:
                    if device["ip"] in selected_ips:
                        await self.async_set_unique_id(device["ip"])
                        if self._abort_if_unique_id_configured():
                            continue

                        await self.hass.config_entries.flow.async_init(
                            DOMAIN,
                            context={"source": "import"},
                            data={
                                "name": device.get("name", device["ip"]),
                                "host_ip": device["ip"],
                                "mac": device.get("mac", ""),
                            },
                        )

                return self.async_abort(reason="import_success")

        device_options = {}
        for device in self._devices:
            label = f"{device.get('name', device['ip'])} ({device['ip']})"
            device_options[device["ip"]] = label

        return self.async_show_form(
            step_id="devices",
            data_schema=vol.Schema(
                {
                    vol.Required("devices"): vol.All(
                        vol.Coerce(list),
                        [vol.In(device_options)],
                    ),
                }
            ),
            errors=errors,
        )

    async def async_step_import(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle import from internal flow."""
        if user_input is None:
            return self.async_abort(reason="import_failed")

        return self.async_create_entry(
            title=user_input.get("name", "PC"),
            data=user_input,
        )


class SmartCafeOptionsFlow(OptionsFlow):
    """Handle options for SmartCafe Control."""

    def __init__(self) -> None:
        super().__init__()

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Per-device scan interval and ping count override."""
        errors: dict[str, str] = {}

        if user_input is not None:
            scan_interval = user_input.get(CONF_SCAN_INTERVAL)
            ping_count = user_input.get(CONF_PING_COUNT)

            new_options = dict(self.config_entry.options)
            if scan_interval is not None:
                new_options[CONF_SCAN_INTERVAL] = scan_interval
            if ping_count is not None:
                new_options[CONF_PING_COUNT] = ping_count

            self.hass.config_entries.async_update_entry(
                self.config_entry, options=new_options
            )
            return self.async_create_entry(title="", data={})

        current_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )
        current_count = self.config_entry.options.get(
            CONF_PING_COUNT, DEFAULT_PING_COUNT
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SCAN_INTERVAL, default=current_interval
                    ): vol.All(int, vol.Range(min=5, max=3600)),
                    vol.Required(
                        CONF_PING_COUNT, default=current_count
                    ): vol.All(int, vol.Range(min=1, max=10)),
                }
            ),
            errors=errors,
        )
