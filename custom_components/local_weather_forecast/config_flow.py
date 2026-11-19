"""Configuration flow for local weather forecast."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.selector import EntitySelector, EntitySelectorConfig
from .const import DOMAIN, CONF_PRESSURE, CONF_TEMPERATURE, CONF_HUMIDITY


def schema(defaults=None):
    defaults = defaults or {}
    fields = {}
    for key in (CONF_PRESSURE, CONF_TEMPERATURE, CONF_HUMIDITY):
        marker = (vol.Required(key, default=defaults[key])
                  if key in defaults else vol.Required(key))
        fields[marker] = EntitySelector(EntitySelectorConfig(domain="sensor"))
    return vol.Schema(fields)


class LocalWeatherForecastFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            await self.async_set_unique_id("local_station")
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title="Lokalna stacja pogodowa", data=user_input)
        return self.async_show_form(step_id="user", data_schema=schema())

    @staticmethod
    def async_get_options_flow(config_entry):
        return LocalWeatherOptionsFlow()


class LocalWeatherOptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        current = {**self.config_entry.data, **self.config_entry.options}
        return self.async_show_form(step_id="init", data_schema=schema(current))
