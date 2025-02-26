import logging
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import DOMAIN
from .sensor import MyPvSensor  # Import MyPvSensor

_LOGGER = logging.getLogger(__name__)

DEFAULT_UPDATE_INTERVAL = 60  # Seconds
DEFAULT_DEVICE_NAME = "MyPv"

async def async_setup_entry(hass: HomeAssistant, config_entry):
    _LOGGER.info(f"Setting up MyPV entry: {config_entry.entry_id}")
    coordinator = MyPvDataUpdateCoordinator(hass, config_entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[config_entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(config_entry, ["sensor"])
    _LOGGER.info(f"MyPV integration setup complete for entry_id: {config_entry.entry_id}")
    return True

async def async_unload_entry(hass: HomeAssistant, config_entry):
    _LOGGER.info(f"Unloading MyPV entry: {config_entry.entry_id}")
    unload_ok = await hass.config_entries.async_forward_entry_unload(config_entry, "sensor")
    if unload_ok:
        hass.data[DOMAIN].pop(config_entry.entry_id)
    return unload_ok

class MyPvDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, config_entry):
        self.config_entry = config_entry
        # Use options if available, otherwise use data
        self.update_interval = timedelta(seconds=config_entry.options.get("update_interval", config_entry.data.get("update_interval", DEFAULT_UPDATE_INTERVAL)))
        self.device_name = config_entry.options.get("device_name", config_entry.data.get("device_name", DEFAULT_DEVICE_NAME))
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=self.update_interval,
        )
        self.api_url = f'https://api.my-pv.com/api/v1/device/{config_entry.data["serialnumber"]}/data'
        self.headers = {
            'Authorization': f'Bearer {config_entry.data["api_token"]}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        self.created_entities = set()

    def scale_value(self, key, value):
        # Define scaling factors for specific keys
        scale_map = {
            "temp1": 0.1,
            "temp2": 0.1,
            "temp3": 0.1,
            "temp4": 0.1,
            # Add more scaling factors as needed
        }
        return value * scale_map.get(key, 1)

    async def _async_update_data(self):
        try:
            # Fetch data from the API
            async with async_get_clientsession(self.hass).get(self.api_url, headers=self.headers) as response:
                if response.status != 200:
                    raise UpdateFailed(f"Error fetching API data: {response.status}")
                data = await response.json()
                _LOGGER.debug(f"API data received: {data}")

                # Check if 'temp1' is present in the response
                if 'temp1' not in data:
                    _LOGGER.warning("Sensor 'temp1' not found in API response.")

                # Process and scale the data
                for key, value in data.items():
                    if isinstance(value, (int, float, str)) and value is not None:
                        try:
                            float_value = float(value)
                            data[key] = self.scale_value(key, float_value)
                        except ValueError:
                            _LOGGER.warning(f"Invalid value for {key}: {value}")
                            data[key] = None
                    else:
                        _LOGGER.warning(f"Missing or invalid value for {key}: {value}")
                        data[key] = None
                return data

        except Exception as e:
            raise UpdateFailed(f"Error fetching API data: {e}")

    @callback
    def async_add_new_entities(self, async_add_entities):
        new_entities = []
        # Add new entities if they are not already created and have valid values
        for key, value in self.data.items():
            if key not in self.created_entities and value is not None and value != "":
                new_entities.append(MyPvSensor(self, key, self.config_entry))
                self.created_entities.add(key)
        if new_entities:
            async_add_entities(new_entities)