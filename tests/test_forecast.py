import importlib.util
from datetime import datetime, timedelta, timezone
from pathlib import Path

spec = importlib.util.spec_from_file_location('forecast', Path(__file__).resolve().parents[1] / 'custom_components/local_weather_forecast/forecast.py')
forecast = importlib.util.module_from_spec(spec)
spec.loader.exec_module(forecast)


def test_dew_point_at_saturation():
    assert abs(forecast.dew_point(20, 100) - 20) < 0.001


def test_no_history():
    assert forecast.calculate([], datetime.now(timezone.utc)) == {}


def test_trends_and_horizons():
    now = datetime.now(timezone.utc)
    samples = [{'time': now - timedelta(hours=h), 'p': 1010 + h, 't': 12, 'rh': 90} for h in range(30, -1, -1)]
    result = forecast.calculate(samples, now)
    assert result['trend_3h'] == -3
    assert result['trend_12h'] == -12
    assert result['forecast_12_24h'] != 'Zbieranie danych'
    assert result['deterioration_index'] is not None


def test_missing_older_data():
    now = datetime.now(timezone.utc)
    result = forecast.calculate([{'time': now, 'p': 1010, 't': 12, 'rh': 80}], now)
    assert result['forecast_12_24h'] == 'Zbieranie danych'
