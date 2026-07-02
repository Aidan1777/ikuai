"""IKUAI Update Entities"""
import logging
from homeassistant.components.update import (
    UpdateEntity,
    UpdateDeviceClass,
    UpdateEntityFeature,
)
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import COORDINATOR, DOMAIN, UPDATE_ENTRY, UPDATE_TYPES

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up iKuai update entities from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]
    async_add_entities([IKUAIUpdate(coordinator)], False)


class IKUAIUpdate(UpdateEntity):
    """Define an iKuai firmware update entity."""

    _attr_has_entity_name = True
    _attr_supported_features = UpdateEntityFeature.INSTALL
    _attr_device_class = UpdateDeviceClass.FIRMWARE

    def __init__(self, coordinator):
        """Initialize the update entity."""
        super().__init__()
        self.coordinator = coordinator
        self._attr_unique_id = f"{DOMAIN}_{UPDATE_ENTRY}_{coordinator.host}"
        self._attr_name = UPDATE_TYPES[UPDATE_ENTRY]["name"]
        self._attr_icon = UPDATE_TYPES[UPDATE_ENTRY]["icon"]

        data = self.coordinator.data if self.coordinator.data else {}
        self._attr_device_info = {
            "identifiers": {(DOMAIN, self.coordinator.host)},
            "name": data.get("device_name", "iKuai Router"),
            "manufacturer": "iKuai",
            "model": "iKuai Router",
            "sw_version": data.get("sw_version", "Unknown"),
        }

    @property
    def should_poll(self) -> bool:
        """No polling needed for coordinator entities."""
        return False

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success

    @property
    def installed_version(self) -> str | None:
        """Return the currently installed firmware version."""
        if self.coordinator.data:
            return self.coordinator.data.get("sw_version")
        return None

    @property
    def latest_version(self) -> str | None:
        """Return the latest available firmware version."""
        if self.coordinator.data:
            latest = self.coordinator.data.get("firmware_latest_version")
            if latest:
                return latest
        return None

    @property
    def release_url(self) -> str | None:
        """Return the URL for the firmware release."""
        if self.coordinator.data:
            return self.coordinator.data.get("firmware_release_url") or None
        return None

    @property
    def release_summary(self) -> str | None:
        """Return the release summary/changelog."""
        if self.coordinator.data:
            return self.coordinator.data.get("firmware_release_summary") or None
        return None

    async def async_install(
        self, version: str | None, backup: bool, **kwargs
    ) -> None:
        """Install the latest firmware update."""
        _LOGGER.warning("触发爱快固件升级，升级过程可能需要几分钟，期间路由器会重启")
        sess_key = await self.coordinator.get_access_token()
        if not sess_key:
            _LOGGER.error("Failed to get access token for firmware upgrade")
            return

        result = await self.coordinator._fetcher.do_firmware_upgrade(sess_key)
        if result is not None:
            _LOGGER.info("Firmware upgrade initiated successfully")
        else:
            _LOGGER.error("Firmware upgrade request failed")

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self) -> None:
        """Update entity."""
        pass
