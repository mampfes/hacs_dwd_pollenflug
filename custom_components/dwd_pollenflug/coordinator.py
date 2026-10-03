"""Data update coordinator for DWD Pollenflug."""
import logging
from datetime import timedelta

import aiohttp
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_utc_time_change
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .DWD import Pollenflug

_LOGGER = logging.getLogger(__name__)


class PollenflugCoordinator(DataUpdateCoordinator[Pollenflug.Pollenflug]):
    """Fetch DWD data once for all configured regions. Stored in hass.data."""

    def __init__(self, hass: HomeAssistant):
        """Initialize the instance."""
        # shared by all config entries, therefore not bound to a single one
        super().__init__(
            hass,
            _LOGGER,
            config_entry=None,
            name=DOMAIN,
            update_interval=timedelta(hours=1),
        )
        self.source = Pollenflug.Pollenflug()
        self.entry_ids: set[str] = set()

        # Forecasts are selected by date, so sensors must re-evaluate when the
        # day changes even if no new data was fetched. Midnight in Europe/Berlin
        # is always a full UTC hour.
        self._unsub_hourly = async_track_utc_time_change(
            hass, self._async_hourly, minute=0, second=0
        )

    async def _async_update_data(self) -> Pollenflug.Pollenflug:
        try:
            await self.source.fetch(async_get_clientsession(self.hass))
        except (aiohttp.ClientError, TimeoutError, KeyError, ValueError) as err:
            raise UpdateFailed(f"fetch data from DWD failed: {err}") from err
        return self.source

    @callback
    def _async_hourly(self, *_):
        if self.data is not None:
            self.async_update_listeners()

    async def async_shutdown(self) -> None:
        """Cancel all timers."""
        await super().async_shutdown()
        self._unsub_hourly()
