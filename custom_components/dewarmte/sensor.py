import logging
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass, SensorStateClass,
)
from homeassistant.const import UnitOfTemperature, UnitOfEnergy, UnitOfVolumeFlowRate
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STATUS_KEYS = {
    "supply_temperature": (SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS, "status"),
    "target_temperature": (SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS, "status"),
    "actual_temperature": (SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS, "status"),
    "heat_sum": (SensorDeviceClass.ENERGY, UnitOfEnergy.KILO_WATT_HOUR, "insights"),
    "cop": ("", "", "insights"),
    "calculated_consumed_electricity": (SensorDeviceClass.ENERGY, UnitOfEnergy.KILO_WATT_HOUR, "insights"),
    "heat_input": (SensorDeviceClass.ENERGY, UnitOfEnergy.KILO_WATT_HOUR, "status"),
    "heat_output": (SensorDeviceClass.ENERGY, UnitOfEnergy.KILO_WATT_HOUR, "status"),
    "water_flow": (SensorDeviceClass.VOLUME_FLOW_RATE, UnitOfVolumeFlowRate.LITERS_PER_MINUTE, "status"),
}

STATS_KEYS = {
    "electricity_sum": (SensorDeviceClass.ENERGY, UnitOfEnergy.KILO_WATT_HOUR, "insights", SensorStateClass.TOTAL),
    "electricity_consumption": (SensorDeviceClass.ENERGY, UnitOfEnergy.KILO_WATT_HOUR, "status", SensorStateClass.MEASUREMENT)
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up MyIntegration sensors from config entry."""

    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinaFtor"]
    entities = []


    for device_id, device in coordinator.data.items():
        nickname = device.get("nickname", device_id)
        device_model = device.get("type", {})

        for key, (device_class, unit, target_api) in STATUS_KEYS.items():
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
                    target_api= target_api,
                    device_class=device_class
                )
            )

        for key, (device_class, unit, target_api, state_class) in STATS_KEYS.items():
            name = f"{nickname} {key.replace('_', ' ').title()}"
            entities.append(
                StatsSensor(
                    coordinator=coordinator,
                    device_id=device_id,
                    device_name=nickname,
                    device_model = device_model,
                    key=key,
                    name=name,
                    unit=unit,
                    target_api= target_api,
                    device_class=device_class,
                    state_class = state_class
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

    def __init__(self, coordinator, device_id, device_name, device_model, key, name, unit, device_class, target_api):
        super().__init__(coordinator)
        self.device_id = device_id
        self.key = key
        self.device_name = device_name
        self.device_model = device_model
        self.target_api = target_api

        self._attr_name = name
        self._attr_unique_id = f"{device_id}_{key}"
        self._attr_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_should_poll = False
        self._attr_native_unit_of_measurement = unit

    @property
    def native_value(self):
        """Return the sensor value."""
        device_data = self.coordinator.data.get(self.device_id, {})
        value = device_data.get(self.target_api, {}).get(self.key)
        return value

    @property
    def available(self):
        """Return True if entity is available."""
        return (
            super().available
            and self.device_id in self.coordinator.data
            and self.coordinator.data[self.device_id].get(self.target_api) is not None
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
        self._attr_device_class = device_class
        self._attr_should_poll = False
        self._attr_native_unit_of_measurement = unit

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

class StatsSensor(CoordinatorEntity, SensorEntity):
    """
    EnergySensor will represent the analytics from API
    """
    def __init__(self, coordinator, device_id, device_name, device_model, key, name, unit, device_class, target_api, state_class):
        super().__init__(coordinator)
        self.device_id = device_id
        self.key = key
        self.device_name = device_name
        self.device_model = device_model
        self.target_api = target_api
        self._attr_name = name
        self._attr_unique_id = f"{device_id}_{key}"
        self._attr_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_should_poll = False
        self._attr_state_class = state_class
        self._attr_native_unit_of_measurement = unit

    @property
    def native_value(self):
        """Return the sensor value."""
        device_data = self.coordinator.data.get(self.device_id, {})
        value = device_data.get(self.target_api, {}).get(self.key)
        return value

    @property
    def available(self):
        """Return True if entity is available."""
        return (
                super().available
                and self.device_id in self.coordinator.data
                and self.coordinator.data[self.device_id].get(self.target_api) is not None
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

