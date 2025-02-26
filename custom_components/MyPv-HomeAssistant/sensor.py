from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Add initial entities
    sensors = []
    for key, value in coordinator.data.items():
        if value is not None and value != "":
            sensors.append(MyPvSensor(coordinator, key, config_entry))
            coordinator.created_entities.add(key)

    async_add_entities(sensors)

    # Register callback to add new entities dynamically
    coordinator.async_add_listener(lambda: coordinator.async_add_new_entities(async_add_entities))

class MyPvSensor(CoordinatorEntity, Entity):
    def __init__(self, coordinator, key, config_entry):
        super().__init__(coordinator)
        self._key = key
        self._config_entry = config_entry

    @property
    def name(self):
        # Return the name of the sensor
        return f"MyPV {self._key}"

    @property
    def state(self):
        # Return the state of the sensor
        value = self.coordinator.data.get(self._key)
        return self.format_value(value)

    @property
    def unit_of_measurement(self):
        # Define the unit of measurement for each sensor key
        unit_map = {
            "temp1": "°C",
            "temp2": "°C",
            "temp3": "°C",
            "temp4": "°C",
            "power_solar": "W",
            "power_grid": "W",
            "volt_mains": "V",
            "wifi_signal": "dBm",
            "curr_L2": "A",
            "curr_L3": "A",
            "curr_mains": "A",
            "freq": "Hz",
            "m0bat": "V",
            "m0l1": "A",
            "m0l2": "A",
            "m0l3": "A",
            "m0sum": "A",
            "m1l1": "A",
            "m1l2": "A",
            "m1l3": "A",
            "m1sum": "A",
            "m2l1": "A",
            "m2l2": "A",
            "m2l3": "A",
            "m2sum": "A",
            "m3l1": "A",
            "m3l2": "A",
            "m3l3": "A",
            "m3sum": "A",
            "m4l1": "A",
            "m4l2": "A",
            "m4l3": "A",
            "m4sum": "A",
            "volt_L2": "V",
            "volt_L3": "V",
            "volt_out": "V",
            "uptime": "days",
            "freq": "Hz",
            "power_elwa2": "W",
            "power_max": "W",
            "power_nominal": "W",
            "power_system": "W",
            "temp_ps": "°C",
            "unixtime": "s",
            "volt_aux": "V",
            "warnings": "",
            "wifi_signal": "dBm",
            # Add more units as needed
        }
        return unit_map.get(self._key, None)

    @property
    def icon(self):
        # Define the icon for each sensor key
        icon_map = {
            "temp1": "mdi:thermometer",
            "temp2": "mdi:thermometer",
            "temp3": "mdi:thermometer",
            "temp4": "mdi:thermometer",
            "power_solar": "mdi:flash",
            "power_grid": "mdi:flash",
            "volt_mains": "mdi:flash",
            "wifi_signal": "mdi:wifi",
            "curr_L2": "mdi:current-ac",
            "curr_L3": "mdi:current-ac",
            "curr_mains": "mdi:current-ac",
            "freq": "mdi:wave",
            "m0bat": "mdi:battery",
            "m0l1": "mdi:current-ac",
            "m0l2": "mdi:current-ac",
            "m0l3": "mdi:current-ac",
            "m0sum": "mdi:current-ac",
            "m1l1": "mdi:current-ac",
            "m1l2": "mdi:current-ac",
            "m1l3": "mdi:current-ac",
            "m1sum": "mdi:current-ac",
            "m2l1": "mdi:current-ac",
            "m2l2": "mdi:current-ac",
            "m2l3": "mdi:current-ac",
            "m2sum": "mdi:current-ac",
            "m3l1": "mdi:current-ac",
            "m3l2": "mdi:current-ac",
            "m3l3": "mdi:current-ac",
            "m3sum": "mdi:current-ac",
            "m4l1": "mdi:current-ac",
            "m4l2": "mdi:current-ac",
            "m4l3": "mdi:current-ac",
            "m4sum": "mdi:current-ac",
            "volt_L2": "mdi:flash",
            "volt_L3": "mdi:flash",
            "volt_out": "mdi:flash",
            # Add more icons as needed
        }
        return icon_map.get(self._key, "mdi:information")

    @property
    def device_info(self):
        # Return device information
        return {
            "identifiers": {(DOMAIN, self._config_entry.entry_id)},
            "name": "MyPV Device",
            "manufacturer": "MyPV",
            "model": "MyPV Model",
            "sw_version": self.coordinator.data.get("psversion"),
        }

    @property
    def device_class(self):
        # Return the device class
        return "sensor"

    @property
    def unique_id(self):
        # Return a unique ID for the sensor
        return f"{self._config_entry.entry_id}_{self._key}"

    def format_value(self, value):
        # Format the value based on the sensor key
        if self._key == "uptime":
            return int(value)  # Convert uptime to integer days
        elif self._key in ["freq", "power_grid", "power_solar", "volt_mains", "temp1", "temp2"]:
            return float(value)  # Convert to float
        return value

    async def async_update(self):
        # Request a refresh of the data
        await self.coordinator.async_request_refresh()