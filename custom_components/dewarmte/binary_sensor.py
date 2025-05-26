import logging
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

BINARY_SENSOR_KEYS = {
    "is_on": BinarySensorDeviceClass.RUNNING,
    "gas_boiler": BinarySensorDeviceClass.RUNNING,
    "is_connected": BinarySensorDeviceClass.CONNECTIVITY,
    "thermostat": BinarySensorDeviceClass.RUNNING,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up MyIntegration binary sensors from config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinaFtor"]

    entities = []

    for device_id, device in coordinator.data.items():
        nickname = device.get("nickname", device_id)
        status = device.get("status", {})
        device_model = device.get("type", {})

        for key, device_class in BINARY_SENSOR_KEYS.items():
            if key in status:
                name = f"{nickname} {key.replace('_', ' ').title()}"
                entities.append(
                    MyBinarySensor(
                        coordinator=coordinator,
                        device_id=device_id,
                        device_name=nickname,
                        device_model=device_model,
                        key=key,
                        name=name,
                        device_class=device_class,
                    )
                )

    if entities:
        async_add_entities(entities)


class MyBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a binary sensor."""

    def __init__(self, coordinator, device_id, device_name, device_model, key, name, device_class):
        super().__init__(coordinator)
        self.device_id = device_id
        self.key = key
        self.device_name = device_name
        self.device_model = device_model

        self._attr_name = name
        self._attr_unique_id = f"{device_id}_{key}"
        self._attr_device_class = device_class

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        device_data = self.coordinator.data.get(self.device_id, {})
        return device_data.get("status", {}).get(self.key)

    @property
    def available(self):
        """Return True if entity is available."""
        return (
            super().available
            and self.device_id in self.coordinator.data
            and self.coordinator.data[self.device_id].get("status") is not None
        )

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.device_id)},
            name=self.device_name,
            manufacturer="DeWarmte",
            model=self.device_model,
            configuration_url="https://my.dewarmte.com",
        )