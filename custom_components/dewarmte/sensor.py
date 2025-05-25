import logging
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
)
from homeassistant.const import UnitOfTemperature, UnitOfEnergy
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import DeviceInfo


from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SENSOR_KEYS = {
    "supply_temperature": (SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS, None),
    "target_temperature": (SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS, None),
    "actual_temperature": (SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS, None),
    "heat_input": (SensorDeviceClass.ENERGY, UnitOfEnergy.KILO_WATT_HOUR, "total"),
    "heat_output": (SensorDeviceClass.ENERGY, UnitOfEnergy.KILO_WATT_HOUR, "total"),
    "electricity_consumption": (SensorDeviceClass.ENERGY,  UnitOfEnergy.KILO_WATT_HOUR, "total")
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up MyIntegration sensors from config entry."""

    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    entities = []

    for device_id, device in coordinator.data.items():
        nickname = device.get("nickname", device_id)
        status = device.get("status", {})
        device_model = device.get("type", {})

        for key, (device_class, unit, state_class) in SENSOR_KEYS.items():
            if key in status:
                name = f"{nickname} {key.replace('_', ' ').title()}"
                entities.append(
                    MySensor(
                        coordinator=coordinator,
                        device_id=device_id,
                        device_name=nickname,
                        device_model = device_model,
                        key=key,
                        name=name,
                        unit=unit,
                        device_class=device_class,
                        state_class=state_class
                    )
                )
        
        key="outside_temperature"
        entities.append(
            OutdoorSensor(
                coordinator=coordinator,
                device_id=device_id,
                device_name=nickname,
                device_model=device_model,
                key=key,
                name=f"{nickname} {key.replace('_', ' ').title()}",
                unit=UnitOfTemperature.CELSIUS,
                device_class=SensorDeviceClass.TEMPERATURE
            )
        )

    if entities:
        async_add_entities(entities)


class MySensor(CoordinatorEntity, SensorEntity):
    """Representation of a sensor pulled from the API via coordinator."""

    def __init__(self, coordinator, device_id, device_name, device_model, key, name, unit, device_class, state_class=None):
        super().__init__(coordinator)
        self.device_id = device_id
        self.key = key
        self.device_name = device_name
        self.device_model = device_model

        self._attr_name = name
        self._attr_unique_id = f"{device_id}_{key}"
        self._attr_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_should_poll = False
        if state_class is not None:
            self._attr_state_class = state_class
        self._attr_native_unit_of_measurement = unit

    @property
    def native_value(self):
        """Return the sensor value."""
        device_data = self.coordinator.data.get(self.device_id, {})
        value = device_data.get("status", {}).get(self.key)
        return value

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


class OutdoorSensor(CoordinatorEntity, SensorEntity):

    def __init__(self, coordinator, device_id, device_name, device_model, key, name, unit, device_class):
        super().__init__(coordinator)
        self.device_id = device_id
        self.key = key
        self.device_name = device_name
        self.device_model = device_model

        self._attr_name = name
        self._attr_unique_id = f"{device_id}_{key}"
        self._attr_unit_of_measurement = unit
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_should_poll = False

    @property
    def native_value(self):
        """Return the sensor value."""
        device_data = self.coordinator.data.get(self.device_id, {})
        value = device_data.get("outdoor_temp", {})
        return value

    @property
    def available(self):
        """Return True if entity is available."""
        return (
                super().available
                and self.device_id in self.coordinator.data
                and self.coordinator.data[self.device_id].get("outdoor_temp") is not None
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