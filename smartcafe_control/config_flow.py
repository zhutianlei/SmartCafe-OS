"""Config flow for SmartCafe Control integration."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult, OptionsFlow, ConfigEntry
from homeassistant.core import callback

from .const import (
    CONF_HA_ASSISTANT_URL,
    CONF_PING_COUNT,
    CONF_SCAN_INTERVAL,
    DEFAULT_PING_COUNT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class SmartCafeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SmartCafe Control."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> SmartCafeOptionsFlow:
        """Get the options flow for this handler."""
        return SmartCafeOptionsFlow(config_entry)

    def __init__(self) -> None:
        """Initialize config flow."""
        self._ha_assistant_url: str = ""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Step 1: Configure HA Assistant connection."""
        errors: dict[str, str] = {}

        # 自动使用localhost连接服务端
        self._ha_assistant_url = "http://localhost:8766"

        # Test connection
        if not await self._test_connection(self._ha_assistant_url):
            errors["base"] = "connection_failed"
        else:
            return await self.async_step_devices()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
            errors=errors,
        )

    async def async_step_devices(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Step 2: Select devices to import."""
        errors: dict[str, str] = {}

        # Fetch devices from HA Assistant
        devices = await self._fetch_devices(self._ha_assistant_url)

        if user_input is not None:
            selected_ips = user_input.get("devices", [])
            if not selected_ips:
                errors["devices"] = "no_devices_selected"
            else:
                # Create config entries for selected devices
                for device in devices:
                    if device["ip"] in selected_ips:
                        # Check if already configured
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
                                CONF_HA_ASSISTANT_URL: self._ha_assistant_url,
                            },
                        )

                return self.async_abort(reason="import_success")

        # Build device options
        device_options = []
        for device in devices:
            label = f"{device.get('name', device['ip'])} ({device['ip']})"
            device_options.append({"value": device["ip"], "label": label})

        if not device_options:
            return self.async_abort(reason="no_devices_found")

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
            description_placeholders={
                "device_count": str(len(device_options)),
            },
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

    async def _test_connection(self, url: str) -> bool:
        """Test connection to HA Assistant."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{url}/admin/whitelist/devices",
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    return resp.status == 200
        except Exception as err:
            _LOGGER.warning("Connection test failed: %s", err)
            return False

    async def _fetch_devices(self, url: str) -> list[dict]:
        """Fetch devices from HA Assistant."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{url}/admin/whitelist/devices",
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status == 200:
                        return await resp.json()
        except Exception as err:
            _LOGGER.warning("Failed to fetch devices: %s", err)
        return []


class SmartCafeOptionsFlow(OptionsFlow):
    """Handle options for SmartCafe Control."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Directly show per-device settings."""
        return await self.async_step_device_settings(user_input)

    async def async_step_device_settings(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Per-device scan interval and ping count override."""
        errors: dict[str, str] = {}

        if user_input is not None:
            scan_interval = user_input.get(CONF_SCAN_INTERVAL)
            ping_count = user_input.get(CONF_PING_COUNT)

            new_options = dict(self._config_entry.options)
            if scan_interval is not None:
                new_options[CONF_SCAN_INTERVAL] = scan_interval
            if ping_count is not None:
                new_options[CONF_PING_COUNT] = ping_count

            self.hass.config_entries.async_update_entry(
                self._config_entry, options=new_options
            )
            return self.async_create_entry(title="", data={})

        current_interval = self._config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )
        current_count = self._config_entry.options.get(
            CONF_PING_COUNT, DEFAULT_PING_COUNT
        )

        return self.async_show_form(
            step_id="device_settings",
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
            description_placeholders={
                "name": self._config_entry.title,
            },
        )
