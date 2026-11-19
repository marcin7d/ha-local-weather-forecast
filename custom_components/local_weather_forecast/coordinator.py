"""Sampling and persistence of local outdoor sensor measurements."""
import logging
import math
from datetime import datetime, timedelta, timezone
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util
from .const import (DOMAIN, CONF_PRESSURE, CONF_TEMPERATURE,
                    CONF_HUMIDITY, SAMPLE_MINUTES, MAX_HOURS)
from .forecast import calculate

_LOGGER = logging.getLogger(__name__)

class LocalForecastCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry):
        super().__init__(hass, _LOGGER, name=DOMAIN)
        self.entry = entry
        self.samples = []
        self.store = Store(hass, 1, f"{DOMAIN}_{entry.entry_id}")
        self._unsub = None
        self._last_save = None

    async def async_initialize(self):
        stored = await self.store.async_load() or {}
        settings = {**self.entry.data, **self.entry.options}
        if stored.get("sources") != settings:
            stored = {}
        for item in stored.get("samples", []):
            try:
                stamp = datetime.fromisoformat(item["time"])
                if stamp.tzinfo is None:
                    stamp = stamp.replace(tzinfo=timezone.utc)
                self.samples.append({"time": stamp, "p": float(item["p"]),
                                     "t": float(item["t"]), "rh": float(item["rh"])})
            except (ValueError, TypeError, KeyError):
                continue
        self.samples.sort(key=lambda s: s["time"])
        self._sample()
        self._unsub = async_track_time_interval(
            self.hass, self._tick, timedelta(minutes=SAMPLE_MINUTES))

    def _read(self, key, minimum, maximum):
        settings = {**self.entry.data, **self.entry.options}
        state = self.hass.states.get(settings[key])
        if state is None or state.state in ("unknown", "unavailable"):
            return None
        now = dt_util.utcnow()
        # A repeated sample is acceptable only when the source measurement is recent.
        if now - state.last_updated > timedelta(minutes=20):
            return None
        try:
            value = float(state.state)
            if not math.isfinite(value):
                return None
            unit = state.attributes.get("unit_of_measurement", "")
            if key == CONF_PRESSURE:
                factors = {"Pa": 0.01, "kPa": 10, "inHg": 33.8639,
                           "hPa": 1, "mbar": 1, "": 1}
                if unit not in factors:
                    return None
                value *= factors[unit]
            elif key == CONF_TEMPERATURE:
                if unit in ("°F", "F"):
                    value = (value - 32) * 5 / 9
                elif unit not in ("°C", "C", ""):
                    return None
            elif unit not in ("%", ""):
                return None
            return value if minimum <= value <= maximum else None
        except (ValueError, TypeError):
            return None

    def _sample(self):
        now = dt_util.utcnow()
        p = self._read(CONF_PRESSURE, 800, 1100)
        t = self._read(CONF_TEMPERATURE, -60, 65)
        rh = self._read(CONF_HUMIDITY, 0, 100)
        cutoff = now - timedelta(hours=MAX_HOURS)
        self.samples = [s for s in self.samples if s["time"] >= cutoff]
        if None not in (p, t, rh) and 800 <= p <= 1100 and -60 <= t <= 65:
            self.samples.append({"time": now, "p": round(p, 3),
                                 "t": round(t, 3), "rh": round(rh, 3)})
        # If inputs are unavailable, do not publish stale forecast values.
        fresh = bool(self.samples and (now - self.samples[-1]["time"]).total_seconds() < 15 * 60)
        self.async_set_updated_data(calculate(self.samples, now) if fresh else {})

    async def _tick(self, _now):
        self._sample()
        now = dt_util.utcnow()
        if self._last_save is None or now - self._last_save >= timedelta(minutes=15):
            await self._save()

    async def _save(self):
        await self.store.async_save({"sources": {**self.entry.data, **self.entry.options}, "samples": [
            {**s, "time": s["time"].isoformat()} for s in self.samples]})
        self._last_save = dt_util.utcnow()

    async def async_shutdown(self):
        if self._unsub:
            self._unsub()
        await self._save()
