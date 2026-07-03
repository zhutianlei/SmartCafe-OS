"""DataUpdateCoordinator for PC Manager - fetches devices from HA Assistant."""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_HA_ASSISTANT_URL,
    CONF_PING_COUNT,
    CONF_SCAN_INTERVAL,
    DEFAULT_PING_COUNT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class PCManagerCoordinator(DataUpdateCoordinator[dict[str, dict[str, Any]]]):
    """Coordinator that fetches devices from HA Assistant and pings them.

    Data structure:
        {
            "ip_address": {
                "name": str,
                "ip": str,
                "mac": str,
                "is_online": bool,
            }
        }
    """

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            config_entry=entry,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
            always_update=True,
        )
        self.data: dict[str, dict[str, Any]] = {}
        self._ha_assistant_url: str = entry.data.get(CONF_HA_ASSISTANT_URL, "")

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        """Fetch devices from HA Assistant and ping them."""
        # 记录更新前的设备IP列表
        old_ips = set(self.data.keys())

        # Fetch device list from HA Assistant
        devices = await self._fetch_devices()

        # 获取当前存在的设备IP列表
        new_ips = set()
        for device in devices:
            ip = device.get("ip", "")
            if ip:
                new_ips.add(ip)

        # 删除已移除的设备数据和实体
        removed_ips = old_ips - new_ips
        if removed_ips:
            _LOGGER.info("Removing %d devices: %s", len(removed_ips), removed_ips)
            await self._remove_devices(removed_ips)

        # Ping all devices
        if devices:
            tasks = []
            for device in devices:
                ip = device.get("ip", "")
                if ip:
                    tasks.append(self._async_ping(ip))

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for device, result in zip(devices, results):
                ip = device.get("ip", "")
                if not ip:
                    continue

                if isinstance(result, Exception):
                    _LOGGER.warning("Ping failed for %s: %s", ip, result)
                    is_online = False
                else:
                    is_online = result

                self.data[ip] = {
                    "name": device.get("name", ip),
                    "ip": ip,
                    "mac": device.get("mac", ""),
                    "is_online": is_online,
                }

        return self.data

    async def _remove_devices(self, ips: set[str]) -> None:
        """Remove devices and their entities from HA."""
        entity_registry = er.async_get(self.hass)

        for ip in ips:
            # 删除对应的实体
            unique_ids_to_remove = [
                f"pc_manager_{ip}_switch",
                f"pc_manager_{ip}_online",
            ]
            for unique_id in unique_ids_to_remove:
                entity_id = entity_registry.async_get_entity_id(
                    DOMAIN, DOMAIN, unique_id
                )
                if entity_id:
                    _LOGGER.info("Removing entity: %s", entity_id)
                    entity_registry.async_remove(entity_id)

            # 删除设备数据
            self.data.pop(ip, None)

    async def _fetch_devices(self) -> list[dict]:
        """Fetch devices from HA Assistant."""
        if not self._ha_assistant_url:
            return []

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self._ha_assistant_url}/admin/whitelist/devices",
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        _LOGGER.warning(
                            "Failed to fetch devices: HTTP %s", resp.status
                        )
        except Exception as err:
            _LOGGER.warning("Failed to fetch devices: %s", err)

        return []

    async def _async_ping(self, host: str) -> bool:
        """Ping a host and return True if reachable."""
        try:
            proc = await asyncio.create_subprocess_exec(
                "ping",
                "-c",
                str(DEFAULT_PING_COUNT),
                "-W",
                "2",
                host,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await asyncio.wait_for(proc.wait(), timeout=DEFAULT_PING_COUNT * 3 + 2)
            return proc.returncode == 0
        except (asyncio.TimeoutError, OSError) as err:
            _LOGGER.debug("Ping error for %s: %s", host, err)
            return False

    def get_device_by_ip(self, ip: str) -> dict[str, Any] | None:
        """Get device data by IP address."""
        return self.data.get(ip)
