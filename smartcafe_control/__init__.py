"""PC Manager integration - manage PCs with WOL and ping monitoring."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, PLATFORMS
from .coordinator import PCManagerCoordinator
from .rest_api import async_register_api

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the PC Manager integration (YAML config not supported)."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up PC Manager from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Initialize coordinator on first entry
    if "coordinator" not in hass.data[DOMAIN]:
        coordinator = PCManagerCoordinator(hass, entry)
        hass.data[DOMAIN]["coordinator"] = coordinator

        # Register REST API for external integrations
        await async_register_api(hass)
    else:
        coordinator: PCManagerCoordinator = hass.data[DOMAIN]["coordinator"]

    # Forward entry setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Trigger first refresh if this is the first entry
    if len(hass.config_entries.async_entries(DOMAIN)) == 1:
        await coordinator.async_config_entry_first_refresh()

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a PC Manager config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        # If no more entries, clean up coordinator
        remaining = hass.config_entries.async_entries(DOMAIN)
        if len(remaining) <= 1:  # Current entry is still counted during unload
            hass.data.pop(DOMAIN, None)

    return unload_ok
