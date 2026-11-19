"""Heuristic forecast calculations, with no third-party packages."""
import math
from datetime import timedelta


def dew_point(temp, rh):
    rh = max(1.0, min(100.0, rh))
    gamma = math.log(rh / 100.0) + 17.62 * temp / (243.12 + temp)
    return 243.12 * gamma / (17.62 - gamma)


def change(samples, now, hours, field):
    """Difference between latest value and value nearest target time (within tolerance)."""
    if not samples:
        return None
    target = now - timedelta(hours=hours)
    candidates = [s for s in samples if s.get(field) is not None]
    if not candidates:
        return None
    old = min(candidates, key=lambda s: abs(s["time"] - target))
    if abs((old["time"] - target).total_seconds()) > 20 * 60:
        return None
    latest = candidates[-1]
    if (now - latest["time"]).total_seconds() > 20 * 60:
        return None
    return round(latest[field] - old[field], 2)


def calculate(samples, now):
    if not samples:
        return {}
    latest = samples[-1]
    p, t, rh = latest["p"], latest["t"], latest["rh"]
    trends = {h: change(samples, now, h, "p") for h in (1, 3, 6, 12)}
    dt = change(samples, now, 3, "t")
    drh = change(samples, now, 3, "rh")
    dew = dew_point(t, rh)
    spread = t - dew
    # Atmospheric pressure is assumed to be sea-level corrected (QNH).
    # A falling pressure is a risk indicator, NOT a calibrated rain probability.
    def label(delta, threshold):
        if delta is None:
            return "Zbieranie danych"
        if delta <= -2 * threshold:
            return "Gwałtowne pogorszenie"
        if delta <= -threshold:
            return "Tendencja do pogorszenia"
        if delta >= 2 * threshold:
            return "Wyraźna poprawa"
        if delta >= threshold:
            return "Tendencja do poprawy"
        return "Bez wyraźnej zmiany"

    short = label(trends[1], 0.8)
    medium = label(trends[3], 1.5)
    long = label(trends[6], 2.0)
    if trends[12] is None:
        long = "Zbieranie danych"
    else:
        long = label(trends[12], 3.0)
    # Signal strength is not a probability of rain.
    score = None
    if trends[3] is not None:
        score = round(min(100, max(0, 40 - trends[3] * 11
                      + (10 if rh >= 85 else 0)
                      + (8 if drh is not None and drh >= 10 else 0))))
    fog = "Brak danych"
    if spread is not None:
        fog = ("Wysokie" if spread <= 1.0 and rh >= 95
               else "Umiarkowane" if spread <= 2.5 and rh >= 85
               else "Niskie")
    return {
        "pressure": p, "temperature": t, "humidity": rh,
        "dew_point": round(dew, 1), "dew_spread": round(spread, 1),
        "trend_1h": trends[1], "trend_3h": trends[3],
        "trend_6h": trends[6], "trend_12h": trends[12],
        "temp_trend_3h": dt, "humidity_trend_3h": drh,
        "forecast_1_3h": short, "forecast_6_12h": medium,
        "forecast_12_24h": long, "fog_risk": fog,
        "deterioration_index": score,
        "data_hours": round((now - samples[0]["time"]).total_seconds() / 3600, 1),
    }
