"""SmartCafe Control - manage PCs with WOL and ping monitoring."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, PLATFORMS
from .coordinator import PCManagerCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})

    if "coordinator" not in hass.data[DOMAIN]:
        coordinator = PCManagerCoordinator(hass, entry)
        hass.data[DOMAIN]["coordinator"] = coordinator
    else:
        coordinator: PCManagerCoordinator = hass.data[DOMAIN]["coordinator"]

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    if len(hass.config_entries.async_entries(DOMAIN)) == 1:
        await coordinator.async_config_entry_first_refresh()

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        remaining = hass.config_entries.async_entries(DOMAIN)
        if len(remaining) <= 1:
            hass.data.pop(DOMAIN, None)

    return unload_ok
