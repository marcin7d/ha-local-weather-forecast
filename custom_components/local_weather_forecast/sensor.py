"""Forecast and derived weather sensors."""
from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.const import UnitOfPressure, UnitOfTemperature, PERCENTAGE
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN

DESCRIPTIONS = (
    ("forecast_1_3h", "Prognoza 1–3 h", None, None),
    ("forecast_6_12h", "Prognoza 6–12 h", None, None),
    ("forecast_12_24h", "Prognoza 12–24 h", None, None),
    ("trend_1h", "Zmiana ciśnienia 1 h", UnitOfPressure.HPA, "measurement"),
    ("trend_3h", "Zmiana ciśnienia 3 h", UnitOfPressure.HPA, "measurement"),
    ("trend_6h", "Zmiana ciśnienia 6 h", UnitOfPressure.HPA, "measurement"),
    ("trend_12h", "Zmiana ciśnienia 12 h", UnitOfPressure.HPA, "measurement"),
    ("dew_point", "Punkt rosy", UnitOfTemperature.CELSIUS, "measurement"),
    ("dew_spread", "Odległość od punktu rosy", UnitOfTemperature.CELSIUS, "measurement"),
    ("temp_trend_3h", "Zmiana temperatury 3 h", UnitOfTemperature.CELSIUS, "measurement"),
    ("humidity_trend_3h", "Zmiana wilgotności 3 h", PERCENTAGE, "measurement"),
    ("fog_risk", "Warunki sprzyjające mgle", None, None),
    ("deterioration_index", "Indeks pogorszenia pogody", None, None),
    ("data_hours", "Długość historii pomiarów", "h", "measurement"),
)

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([LocalWeatherSensor(coordinator, entry, *d) for d in DESCRIPTIONS])

class LocalWeatherSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry, key, name, unit, state_class):
        super().__init__(coordinator)
        self.key = key
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_name = name
        self._attr_native_unit_of_measurement = unit
        self._attr_state_class = state_class
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Lokalna stacja prognostyczna",
            manufacturer="Local Weather Forecast",
            model="Prognoza heurystyczna",
        )

    @property
    def native_value(self):
        return (self.coordinator.data or {}).get(self.key)

    @property
    def available(self):
        return super().available and self.coordinator.data is not None and bool(self.coordinator.data)

    @property
    def extra_state_attributes(self):
        if self.key.startswith("forecast_"):
            return {"metoda": "Lokalna heurystyka trendów, nie prognoza numeryczna",
                    "uwaga": "Wynik orientacyjny; brak danych o wietrze i radarze"}
        if self.key == "deterioration_index":
            return {"uwaga": "Indeks sygnału 0–100, nie prawdopodobieństwo opadów"}
        return None
