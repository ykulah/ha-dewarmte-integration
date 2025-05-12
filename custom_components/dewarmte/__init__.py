from homeassistant.helpers import aiohttp_client
from .const import DOMAIN, PLATFORMS
import logging

from .coordinator import DeWarmteUpdateCoordinator
from .dewarmte_api_client import DeWarmteAPIClient

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry):
    hass.data.setdefault(DOMAIN, {})
    session = aiohttp_client.async_get_clientsession(hass)
    api_client = DeWarmteAPIClient(entry.data["username"], entry.data["password"], session)
    _LOGGER.info("DeWarmteAPIClient Client Initialized.")

    # Initialize coordinator with client
    coordinator = DeWarmteUpdateCoordinator(hass, api_client)
    await coordinator.async_config_entry_first_refresh()

    # Store coordinator and client for other platforms
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "client": api_client,
    }

    # Forward setup to sensor platform
    hass.async_create_task(hass.config_entries.async_forward_entry_setup(entry, "sensor"))
    hass.async_create_task(hass.config_entries.async_forward_entry_setup(entry, "binary_sensor"))

    return True

async def async_unload_entry(hass, entry):
    for platform in PLATFORMS:
        await hass.config_entries.async_forward_entry_unload(entry, platform)
    hass.data[DOMAIN].pop(entry.entry_id)
    return True
