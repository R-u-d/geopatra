"""The network is not exercised here — only the wording layer that turns
numbers into something a synthetic voice can read out."""

import pytest

from geopatra import weather


@pytest.mark.parametrize(
    ("millimetres", "expected"),
    [(0, "no rain"), (0.5, "barely any rain"), (3, "mild rain"),
     (10, "moderate rain"), (20, "heavy rain"), (40, "very heavy rain"), (80, "basically a flood")],
)
def test_rain_thresholds(millimetres, expected):
    assert weather.classify_rain(millimetres) == expected


@pytest.mark.parametrize(
    ("cover", "expected"),
    [(0, "a clear sky"), (30, "partly cloudy"), (70, "mostly cloudy"), (95, "overcast")],
)
def test_cloud_thresholds(cover, expected):
    assert weather.classify_cloud(cover) == expected


def test_report_does_not_raise_when_the_service_is_unreachable(monkeypatch):
    def explode(*_args, **_kwargs):
        raise weather.requests.ConnectionError("no network")

    monkeypatch.setattr(weather.requests, "get", explode)
    reply = weather.report("Lisbon")
    assert "did not answer" in reply


def test_report_handles_an_unknown_place(monkeypatch):
    monkeypatch.setattr(weather, "geocode", lambda place, language="en": None)
    assert weather.report("Atlantis") == "I could not find a place called Atlantis."
