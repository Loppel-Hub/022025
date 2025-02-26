import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import DOMAIN
import asyncio
import logging

_LOGGER = logging.getLogger(__name__)

class MyPvConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return MyPvOptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            # Validate the API data
            valid = await self._validate_api_data(user_input["serialnumber"], user_input["api_token"])
            if valid:
                return self.async_create_entry(title=user_input.get("device_name", "MyPV"), data=user_input)
            else:
                errors["base"] = "invalid_api_data"

        # Define the schema for the user input form
        data_schema = vol.Schema({
            vol.Required("serialnumber"): str,
            vol.Required("api_token"): str,
            vol.Required("device_name", default="MyPV"): str,
            vol.Required("update_interval", default=60): vol.All(vol.Coerce(int), vol.Range(min=10)),
        })

        # Show the form to the user
        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    async def _validate_api_data(self, serialnumber, api_token):
        # Implement the logic to validate the API data
        try:
            async with async_get_clientsession(self.hass).get(
                f'https://api.my-pv.com/api/v1/device/{serialnumber}/data',
                headers={
                    'Authorization': f'Bearer {api_token}',
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                timeout=15  # Set the timeout to 15 seconds
            ) as response:
                return response.status == 200
        except asyncio.TimeoutError:
            return False
        except Exception as e:
            _LOGGER.exception(f"Error validating API data: {e}")
            return False

class MyPvOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Define the schema for the options form
        options_schema = vol.Schema({
            vol.Required("serialnumber", default=self.config_entry.data.get("serialnumber")): str,
            vol.Required("api_token", default=self.config_entry.data.get("api_token")): str,
            vol.Required("device_name", default=self.config_entry.data.get("device_name", "MyPV Device")): str,
            vol.Required("update_interval", default=self.config_entry.options.get("update_interval", self.config_entry.data.get("update_interval", 60))): vol.All(vol.Coerce(int), vol.Range(min=10)),
        })

        # Show the form to the user
        return self.async_show_form(
            step_id="init",
            data_schema=options_schema
        )