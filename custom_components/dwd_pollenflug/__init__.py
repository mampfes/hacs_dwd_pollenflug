"""Component for DWD Pollenflug support."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .coordinator import PollenflugCoordinator

PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up component from a config entry, config_entry contains data from config entry database."""
    # all entries share one coordinator, as DWD provides all regions at once
    coordinator: PollenflugCoordinator | None = hass.data.get(DOMAIN)
    if coordinator is None:
        coordinator = hass.data[DOMAIN] = PollenflugCoordinator(hass)

    # get first data for setup_platforms
    if coordinator.data is None:
        await coordinator.async_refresh()
        if not coordinator.last_update_success:
            if not coordinator.entry_ids:
                await coordinator.async_shutdown()
                del hass.data[DOMAIN]
            raise ConfigEntryNotReady(
                str(coordinator.last_exception)
            ) from coordinator.last_exception

    coordinator.entry_ids.add(entry.entry_id)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        coordinator: PollenflugCoordinator = hass.data[DOMAIN]
        coordinator.entry_ids.discard(entry.entry_id)
        if not coordinator.entry_ids:
            # also remove coordinator if not used by any entry any more
            await coordinator.async_shutdown()
            del hass.data[DOMAIN]

    return unload_ok
