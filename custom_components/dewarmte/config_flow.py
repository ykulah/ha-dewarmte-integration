from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN
from .const import API_TOKEN_URL
import aiohttp
import logging
from homeassistant.exceptions import ConfigEntryAuthFailed

class MyIntegrationConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for My Integration."""

    VERSION = 1
    _LOGGER = logging.getLogger(__name__)

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        session = aiohttp.ClientSession()
        if user_input is not None:
            # Here you could test the connection, e.g., login
            try:
                user_details = {
                    "email": user_input["username"],
                    "password": user_input["password"]
                }

                logging.info(user_details)
                async with session.post(f"{API_TOKEN_URL}", json=user_details) as resp:

                    data = await resp.json()
                    if resp.status == 200:
                        logging.info("Tokens fetched.")
                        return self.async_create_entry(
                            title=user_input["username"],
                            data=user_input,
                        )
                    else:
                        logging.error(data)
                        errors["base"] = "Authentication failed."

            except ConfigEntryAuthFailed:
                logging.error("Tokens cannot be fetched.")
                logging.error("Failed to refresh tokens. Please check your credentials.")
                errors["base"] = "Authentication failed."
                raise  # Re-raise to let HA handle it cleanly
            except Exception as e:
                logging.error(f"Error during initialization: {e}")
                errors["base"] = "Authentication failed."

        await session.close()
        # Form schema
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("username"): str,
                vol.Required("password"): str,
            }),
            errors=errors,
        )
