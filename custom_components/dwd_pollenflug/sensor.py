import logging
from datetime import timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import (ATTR_IDENTIFIERS, ATTR_MANUFACTURER,
                                 ATTR_MODEL, ATTR_NAME)
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.util.dt import utcnow

from .const import CONF_REGION_ID, DOMAIN

ATTR_VAL_TOMORROW = "state_tomorrow"
ATTR_VAL_IN_2_DAYS = "state_in_2_days"
ATTR_DESC_TODAY = "state_today_desc"
ATTR_DESC_TOMORROW = "state_tomorrow_desc"
ATTR_DESC_IN_2_DAYS = "state_in_2_days_desc"
ATTR_LAST_UPDATE = "last_update"
ATTR_NEXT_UPDATE = "next_update"

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up platform for a new integration.

    Called by the HA framework after async_setup_platforms has been called
    during initialization of a new integration.
    """
    region_id = config_entry.data[CONF_REGION_ID]
    source = hass.data[DOMAIN].source

    entities = []
    names = set()

    for pollen in source.pollen_list:
        if pollen.region_id == region_id and pollen.name not in names:
            names.add(pollen.name)
            entities.append(
                PollenflugSensorEntity(hass, source, region_id, pollen.name)
            )

    async_add_entities(entities)


class PollenflugSensorEntity(SensorEntity):
    """Common functionality for all pollenflug entities."""

    def __init__(self, hass, source, region_id, pollen_name):
        self._source = source
        self._region_id = region_id
        self._pollen_name = pollen_name
        self._value = None
        self._update_sensor_listener = None

        # set HA instance attributes directly (don't use property)
        self._attr_unique_id = f"{DOMAIN}_{pollen_name}_{region_id}"
        self._attr_name = f"Pollenflug {pollen_name} {region_id}"
        self._attr_icon = "mdi:flower-pollen"
        self._attr_device_info = {
            ATTR_IDENTIFIERS: {(DOMAIN, region_id)},
            ATTR_NAME: "Pollenflug-Gefahrenindex",
            ATTR_MANUFACTURER: source.sender,
            ATTR_MODEL: source.regions_list[region_id].name,
            "entry_type": DeviceEntryType.SERVICE,
        }

    async def async_update(self):
        """Update the value of the entity."""
        today = utcnow().date()

        # reset value and extra_state_attributes
        val_today = None
        val_tomorrow = None
        val_in_2_days = None

        for pollen in self._source.pollen_list:
            if pollen.region_id == self._region_id and pollen.name == self._pollen_name:
                if pollen.date == today:
                    val_today = pollen.value
                elif pollen.date == today + timedelta(days=1):
                    val_tomorrow = pollen.value
                elif pollen.date == today + timedelta(days=2):
                    val_in_2_days = pollen.value

        self._value = val_today
        attributes = {
            ATTR_VAL_TOMORROW: val_tomorrow,
            ATTR_VAL_IN_2_DAYS: val_in_2_days,
            ATTR_DESC_TODAY: self._source.legend.get(val_today),
            ATTR_DESC_TOMORROW: self._source.legend.get(val_tomorrow),
            ATTR_DESC_IN_2_DAYS: self._source.legend.get(val_in_2_days),
            ATTR_LAST_UPDATE: self._source.last_update,
            ATTR_NEXT_UPDATE: self._source.next_update,
        }
        self._attr_extra_state_attributes = attributes

        # return last update in local timezone
        self._attr_attribution = f"Last update: {self._source.last_update.astimezone()}"

    @property
    def available(self):
        """Return true if value is valid."""
        return self._value is not None

    @property
    def native_value(self):
        """Return the value of the entity."""
        return self._value
