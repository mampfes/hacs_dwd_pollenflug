"""Component for wiffi support."""
import logging
from builtins import property
from datetime import timedelta
from typing import Dict

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.event import async_track_time_interval

from .const import CONF_REGION_ID, DOMAIN
from .DWD import Pollenflug

_LOGGER = logging.getLogger(__name__)


PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up component from a config entry, config_entry contains data from config entry database."""
    # store shell object
    shell = hass.data.setdefault(DOMAIN, PollenflugShell(hass))

    # get first data for setup_platforms
    try:
        await hass.async_add_executor_job(shell._fetch)
    except Exception as exc:
        _LOGGER.error("fetch data from DWD failed")
        raise ConfigEntryNotReady from exc

    # add pollen region to shell
    shell.add_entry(entry)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        shell = hass.data[DOMAIN]
        shell.remove_entry(entry)
        if shell.is_idle():
            # also remove shell if not used by any entry any more
            del hass.data[DOMAIN]

    return unload_ok


class PollenflugShell:
    """Shell object for DWD Pollenflug. Stored in hass.data."""

    def __init__(self, hass: HomeAssistant):
        """Initialize the instance."""
        self._hass = hass
        self._source = Pollenflug.Pollenflug()
        self._regions: Dict[int, Pollenflug.Region] = {}
        self._fetch_callback_listener = None

    @property
    def source(self):
        return self._source

    def add_entry(self, config_entry: ConfigEntry):
        """Add entry."""
        if self.is_idle():
            # This is the first entry, therefore start the timer
            self._fetch_callback_listener = async_track_time_interval(
                self._hass, self._fetch_callback, timedelta(hours=1)
            )

        self._regions[config_entry.data[CONF_REGION_ID]] = config_entry

    def remove_entry(self, config_entry: ConfigEntry):
        """Remove entry."""
        self._regions.pop(config_entry.data[CONF_REGION_ID])

        if self.is_idle():
            # This was the last region, therefore stop the timer
            remove_listener = self._fetch_callback_listener
            if remove_listener is not None:
                remove_listener()

    def is_idle(self) -> bool:
        return not bool(self._regions)

    @callback
    def _fetch_callback(self, *_):
        self._hass.add_job(self._fetch)

    def _fetch(self, *_):
        try:
            self._source.fetch()
        except Exception as error:
            _LOGGER.error(f"fetch data from DWD failed : {error}")
