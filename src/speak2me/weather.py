"""Weather report from Open-Meteo.

Two calls: geocode the place name, then pull a one-day hourly forecast and
reduce it to something a text-to-speech voice can read out. Raw hourly arrays
are useless spoken aloud, so the numbers get collapsed to ranges and the
thresholds get turned into words ("mild rain", "mostly cloudy").

No API key needed — that is why this provider was picked.
"""

from __future__ import annotations

import requests

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
HOURLY = "temperature_2m,rain,relative_humidity_2m,wind_speed_10m,visibility,cloud_cover"
TIMEOUT = 10


def classify_rain(total_mm: float) -> str:
    if total_mm == 0:
        return "no rain"
    if total_mm < 1:
        return "barely any rain"
    if total_mm < 5:
        return "mild rain"
    if total_mm < 15:
        return "moderate rain"
    if total_mm < 30:
        return "heavy rain"
    if total_mm < 50:
        return "very heavy rain"
    return "basically a flood"


def classify_cloud(cover_percent: float) -> str:
    if cover_percent < 20:
        return "a clear sky"
    if cover_percent < 60:
        return "partly cloudy"
    if cover_percent < 85:
        return "mostly cloudy"
    return "overcast"


def geocode(place: str, language: str = "en") -> dict | None:
    params = {"name": place, "count": 1, "language": language}
    response = requests.get(GEOCODE_URL, params=params, timeout=TIMEOUT)
    response.raise_for_status()
    results = response.json().get("results")
    return results[0] if results else None


def forecast(location: dict) -> str:
    params = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "hourly": HOURLY,
        "forecast_days": 1,
    }
    response = requests.get(FORECAST_URL, params=params, timeout=TIMEOUT)
    response.raise_for_status()
    data = response.json()
    hourly, units = data["hourly"], data["hourly_units"]

    temps = hourly["temperature_2m"]
    rain_total = sum(hourly["rain"])
    humidity = sum(hourly["relative_humidity_2m"]) / len(hourly["relative_humidity_2m"])
    wind_peak = max(hourly["wind_speed_10m"])
    visibility = sum(hourly["visibility"]) / len(hourly["visibility"])
    cloud = sum(hourly["cloud_cover"]) / len(hourly["cloud_cover"])

    parts = (location.get("name"), location.get("admin1"), location.get("country"))
    where = ", ".join(part for part in parts if part)
    rain_detail = (
        f" Precipitation totals {rain_total:.1f} {units['rain']}." if rain_total > 0 else ""
    )

    return (
        f"Weather for {where}. It is {classify_cloud(cloud)}. "
        f"Temperatures range from {min(temps)} to {max(temps)} {units['temperature_2m']}, "
        f"averaging {sum(temps) / len(temps):.1f}. "
        f"Wind peaks at {wind_peak} {units['wind_speed_10m']}. "
        f"There is {classify_rain(rain_total)} today.{rain_detail} "
        f"Average humidity is {humidity:.1f} {units['relative_humidity_2m']}, "
        f"visibility around {int(visibility)} {units['visibility']}."
    )


def report(place: str) -> str:
    """Full report for a place name, or a spoken-friendly failure line."""
    try:
        location = geocode(place)
        if location is None:
            return f"I could not find a place called {place}."
        return forecast(location)
    except (requests.RequestException, KeyError, ValueError) as error:
        return f"The weather service did not answer ({type(error).__name__})."
