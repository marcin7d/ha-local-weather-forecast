# Lokalna Prognoza Pogody — Home Assistant 2026.11

Wersja eksperymentalna 0.1.0. Lokalna integracja prognozowania trendów atmosferycznych z trzech uśrednionych encji zewnętrznych. Nie wymaga chmury ani kluczy API.

## Instalacja ręczna

1. Skopiuj katalog `custom_components/local_weather_forecast` do `/config/custom_components/local_weather_forecast`.
2. Uruchom ponownie Home Assistant.
3. Wejdź w **Ustawienia → Urządzenia i usługi → Dodaj integrację → Lokalna Prognoza Pogody**.
4. Wskaż encje ciśnienia, temperatury i wilgotności. Zmiana encji: **Konfiguruj** przy integracji.

## Marketplace (dawniej HACS)

Repozytorium ma strukturę zgodną z instalacją niestandardowej integracji. Aby instalować je przez Marketplace, umieść cały katalog repozytorium w **publicznym repozytorium GitHub**, a następnie dodaj jego adres jako niestandardowe repozytorium w Marketplace. Sam lokalny ZIP nie jest adresem repozytorium Marketplace.

## Wyniki

- Prognozy na 1–3 h, 6–12 h i 12–24 h
- Zmiany ciśnienia 1/3/6/12 h
- Punkt rosy i różnica temperatury od punktu rosy
- Zmiana temperatury i wilgotności 3 h
- Warunki sprzyjające mgle
- Indeks pogorszenia 0–100 (nie jest procentem ryzyka opadów)
- Długość dostępnej historii

Próbkowanie co 5 minut, zapis historii co 15 minut oraz przy poprawnym wyłączeniu integracji. Historia do 30 godzin w `.storage` Home Assistant. Pierwsze wyniki trendów wymagają odpowiednio 1, 3, 6 i 12 godzin zbierania danych. Przed upływem 12 h prognoza 12–24 h jest niedostępna. Przerwy w pomiarach mogą opóźnić jej pojawienie się.

## Ważne ograniczenia

- Algorytm jest heurystyczny, eksperymentalny, bez kalibracji do lokalnych danych i bez weryfikacji skuteczności. Nie zastępuje ostrzeżeń IMGW.
- Wynik 12–24 h jest szczególnie niepewny. Nie jest to prawdziwa prognoza Zambretti ani numeryczny model meteorologiczny.
- **Ciśnienie musi być sprowadzone do poziomu morza** (QNH / sea-level pressure), a nie surowym ciśnieniem na wysokości stacji. Trend może działać również na ciśnieniu stacyjnym, ale interpretacja ciśnienia absolutnego wymaga poprawnego odniesienia.
- Jednostki: hPa/mbar/Pa/kPa/inHg, °C/°F, % RH. Brak jednostki oznacza odpowiednio hPa, °C, %.
- Bez danych o wietrze, opadach, zachmurzeniu i radarze nie wylicza wiarygodnego prawdopodobieństwa deszczu.
- Zmiana wybranych encji w konfiguracji resetuje zapisaną historię pomiarów po ponownym załadowaniu integracji.

## Testy

Przed produkcyjnym wdrożeniem sprawdź na testowym Home Assistant 2026.11. Pakiet został sprawdzony pod względem składni Pythona i struktury plików, ale nie uruchomiono go w działającej instancji HA 2026.11.

## Reliability and limitations

This is an experimental, locally computed heuristic rather than a calibrated meteorological forecast. The deterioration index is **not** a rain probability. The 12–24 hour output is particularly uncertain without wind, radar, and regional forecast models. The selected pressure sensor should preferably provide sea-level-adjusted pressure (QNH); station pressure at elevation may affect absolute-pressure interpretations. All measurements are normalized to hPa, °C and % before validation. Samples are not accepted if source states have not been updated for more than 20 minutes. Changing source entities resets the persisted history after the integration reloads.

## Development checks

Run `python -m compileall -q custom_components tests` and `python -m pytest -q tests`. These tests exercise calculation logic, but do not replace testing against Home Assistant 2026.11.
