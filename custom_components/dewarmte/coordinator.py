import asyncio
import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .dewarmte_api_client import DeWarmteAPIClient
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(minutes=1)  # Adjust as needed

class DeWarmteUpdateCoordinator(DataUpdateCoordinator):

    def __init__(self, hass: HomeAssistant, client: DeWarmteAPIClient):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )
        self.client = client

    async def _async_update_data(self):
        """Fetch data from API endpoint."""
        try:
            async with asyncio.timeout(30):
                # Refresh token if needed
                await self.client.async_ensure_authenticated()

                # Fetch and return structured device data
                devices = await self.client.async_get_devices()
                outdoor_temp = await self.client.async_get_outdoor_temp()

                devices_return = {device["id"]: device for device in devices}
                for device in devices_return.keys():
                    devices_return[device]["outdoor_temp"] = outdoor_temp
                return devices_return
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
