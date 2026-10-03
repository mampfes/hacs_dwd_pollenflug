"""Test forecast dates using parsed DWD data without network access."""

import unittest
from types import SimpleNamespace
from datetime import datetime, timedelta
from unittest.mock import patch

from homeassistant.util.dt import get_time_zone

from custom_components.dwd_pollenflug.DWD.Pollenflug import Pollenflug
from custom_components.dwd_pollenflug.sensor import PollenflugSensorEntity


def make_source(last_update, values=("0", "1-2", "3")):
    """Parse a synthetic response with distinct values for each forecast day."""
    next_update = datetime.strptime(last_update, "%Y-%m-%d %H:%M Uhr") + timedelta(
        days=1
    )
    source = Pollenflug()
    source._extract_data(
        {
            "last_update": last_update,
            "next_update": next_update.strftime("%Y-%m-%d %H:%M Uhr"),
            "name": "Synthetic pollen forecast",
            "sender": "Test provider",
            "legend": {
                "id1": "0",
                "id1_desc": "none",
                "id4": "1-2",
                "id4_desc": "low to moderate",
                "id7": "3",
                "id7_desc": "high",
            },
            "content": [
                {
                    "region_id": 10,
                    "region_name": "Test region",
                    "partregion_id": 11,
                    "partregion_name": "Test subregion",
                    "Pollen": {
                        "Birke": dict(
                            zip(("today", "tomorrow", "dayafter_to"), values)
                        ),
                        "Hasel": {"today": "3", "tomorrow": "3", "dayafter_to": "3"},
                    },
                },
                {
                    "region_id": 20,
                    "region_name": "Other test region",
                    "partregion_id": -1,
                    "partregion_name": "",
                    "Pollen": {
                        "Birke": {"today": "3", "tomorrow": "3", "dayafter_to": "3"}
                    },
                },
            ],
        }
    )
    return source


def make_sensor(source):
    """Create the real sensor backed by a coordinator stub holding the source."""
    return PollenflugSensorEntity(SimpleNamespace(data=source), 11, "Birke")


class SensorForecastDateTest(unittest.IsolatedAsyncioTestCase):
    """Keep current and future values on the provider's calendar dates."""

    async def check_update(self, source, instant, expected, sensor=None):
        """Update the real sensor and check all forecast attributes."""
        if sensor is None:
            sensor = make_sensor(source)
        with patch(
            "custom_components.dwd_pollenflug.sensor.utcnow",
            return_value=datetime.fromisoformat(instant),
        ):
            sensor._update_from_source()

        today, tomorrow, in_two_days = expected
        descriptions = {0: "none", 1.5: "low to moderate", 3: "high"}
        self.assertEqual(sensor.native_value, today)
        self.assertEqual(sensor.available, today is not None)
        self.assertEqual(
            sensor.extra_state_attributes,
            {
                "state_tomorrow": tomorrow,
                "state_in_2_days": in_two_days,
                "state_today_desc": descriptions.get(today),
                "state_tomorrow_desc": descriptions.get(tomorrow),
                "state_in_2_days_desc": descriptions.get(in_two_days),
                "last_update": source.last_update,
                "next_update": source.next_update,
            },
        )
        self.assertEqual(
            sensor.attribution, f"Last update: {source.last_update.astimezone()}"
        )

    async def test_summer_midnight(self):
        """Roll forecasts forward at 22:00 UTC during summer time."""
        source = make_source("2026-07-01 11:00 Uhr")
        for instant, expected in (
            ("2026-07-01T21:59:59+00:00", (0, 1.5, 3)),
            ("2026-07-01T22:00:00+00:00", (1.5, 3, None)),
            ("2026-07-01T23:59:59+00:00", (1.5, 3, None)),
            ("2026-07-02T00:00:00+00:00", (1.5, 3, None)),
        ):
            with self.subTest(instant=instant):
                await self.check_update(source, instant, expected)

    async def test_winter_midnight(self):
        """Roll forecasts forward at 23:00 UTC during winter time."""
        source = make_source("2026-01-01 11:00 Uhr")
        for instant, expected in (
            ("2026-01-01T22:59:59+00:00", (0, 1.5, 3)),
            ("2026-01-01T23:00:00+00:00", (1.5, 3, None)),
            ("2026-01-01T23:59:59+00:00", (1.5, 3, None)),
            ("2026-01-02T00:00:00+00:00", (1.5, 3, None)),
        ):
            with self.subTest(instant=instant):
                await self.check_update(source, instant, expected)

    async def test_home_assistant_timezone_does_not_change_forecast_dates(self):
        """Follow DWD's timezone even when Home Assistant is configured elsewhere."""
        source = make_source("2026-07-01 11:00 Uhr")
        for timezone in ("UTC", "Europe/Berlin", "America/New_York", "Asia/Tokyo"):
            for instant, expected in (
                ("2026-07-01T21:30:00+00:00", (0, 1.5, 3)),
                ("2026-07-01T22:30:00+00:00", (1.5, 3, None)),
            ):
                with self.subTest(timezone=timezone, instant=instant), patch(
                    "homeassistant.util.dt.DEFAULT_TIME_ZONE", get_time_zone(timezone)
                ):
                    await self.check_update(source, instant, expected)

    async def test_day_after_dst_change(self):
        """Use the current UTC offset even when the response predates a DST change."""
        for last_update, before_midnight, midnight in (
            (
                "2026-03-28 11:00 Uhr",
                "2026-03-29T21:59:59+00:00",
                "2026-03-29T22:00:00+00:00",
            ),
            (
                "2026-10-24 11:00 Uhr",
                "2026-10-25T22:59:59+00:00",
                "2026-10-25T23:00:00+00:00",
            ),
        ):
            source = make_source(last_update)
            for instant, expected in (
                (before_midnight, (1.5, 3, None)),
                (midnight, (3, None, None)),
            ):
                with self.subTest(last_update=last_update, instant=instant):
                    await self.check_update(source, instant, expected)

    async def test_dst_clock_change_does_not_change_forecast_day(self):
        """Skipping or repeating an hour must not advance the calendar date."""
        for last_update, date in (
            ("2026-03-28 11:00 Uhr", "2026-03-29"),
            ("2026-10-24 11:00 Uhr", "2026-10-25"),
        ):
            source = make_source(last_update)
            for time in ("00:59:59", "01:00:00"):
                with self.subTest(date=date, time=time):
                    await self.check_update(
                        source, f"{date}T{time}+00:00", (1.5, 3, None)
                    )

    async def test_response_dated_today_before_utc_midnight(self):
        """A response dated on the new local day must not appear unavailable."""
        for last_update, instant in (
            ("2026-07-02 00:05 Uhr", "2026-07-01T22:30:00+00:00"),
            ("2026-01-02 00:05 Uhr", "2026-01-01T23:30:00+00:00"),
        ):
            with self.subTest(last_update=last_update):
                await self.check_update(make_source(last_update), instant, (0, 1.5, 3))

    async def test_missing_today_forecast_remains_unavailable(self):
        """Do not reuse yesterday's value when today's forecast is missing."""
        source = make_source("2026-07-01 11:00 Uhr", ("0", "-1", "3"))
        await self.check_update(source, "2026-07-01T22:00:00+00:00", (None, 3, None))

    async def test_repeated_updates_clear_expired_forecasts(self):
        """Advance one sensor through the forecast horizon without fetching again."""
        source = make_source("2026-07-01 11:00 Uhr")
        sensor = make_sensor(source)
        for instant, expected in (
            ("2026-07-01T21:59:59+00:00", (0, 1.5, 3)),
            ("2026-07-01T22:00:00+00:00", (1.5, 3, None)),
            ("2026-07-02T22:00:00+00:00", (3, None, None)),
            ("2026-07-03T22:00:00+00:00", (None, None, None)),
        ):
            with self.subTest(instant=instant):
                await self.check_update(source, instant, expected, sensor)
