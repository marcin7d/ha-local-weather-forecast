"""Local weather forecast integration."""
from homeassistant.const import Platform
from .const import DOMAIN
from .coordinator import LocalForecastCoordinator

PLATFORMS = [Platform.SENSOR]

async def async_setup_entry(hass, entry):
    coordinator = LocalForecastCoordinator(hass, entry)
    await coordinator.async_initialize()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_update_options))
    return True

async def async_update_options(hass, entry):
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass, entry):
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if ok:
        coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_shutdown()
    return ok
