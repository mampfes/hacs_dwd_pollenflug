import logging
import re
from datetime import datetime, timedelta

import pytz
import requests

_LOGGER = logging.getLogger(__name__)

# maps keynames to day offsets
PREDICTION_LIST = {
    "today": 0,
    "tomorrow": 1,
    "dayafter_to": 2,
}


class Region:
    def __init__(self, id, name, parent_id):
        self._id = id
        self._name = name
        self._parent_id = parent_id

    def __repr__(self):
        return f"{self.__class__.__name__}(id: {self._id}, name: '{self._name}', parent_id: {self._parent_id})"

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def parent_id(self):
        return self._parent_id


class PollenForecast:
    def __init__(self, region_id, name, date, value):
        self._region_id = region_id
        self._name = name
        self._date = date
        self._value = value
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}(region_id: {self._region_id}, name: '{self._name}', date: '{self._date}', value: '{self._value}')"

    @property
    def region_id(self):
        return self._region_id

    @property
    def name(self):
        return self._name

    @property
    def date(self):
        return self._date

    @property
    def value(self):
        return self._value


class Pollenflug:
    URL = "https://opendata.dwd.de/climate_environment/health/alerts/s31fg.json"
    DESC = "https://opendata.dwd.de/climate_environment/health/alerts/Beschreibung_pollen_s31fg.pdf"
    _TIME_FORMAT_STR = "%Y-%m-%d %H:%M Uhr"
    _TIME_ZONE = "Europe/Berlin"

    def __init__(self):
        self._last_update = None
        self._next_update = None
        self._name = None
        self._sender = None
        self._legend = None
        self._regions_with_data = set()
        self._regions_list = []
        self._pollen_list = []

    @property
    def last_update(self):
        return self._last_update

    @property
    def next_update(self):
        return self._next_update

    @property
    def name(self):
        return self._name

    @property
    def sender(self):
        return self._sender

    @property
    def legend(self):
        return self._legend

    @property
    def regions_list(self):
        return self._regions_list

    @property
    def regions_with_data(self):
        return self._regions_with_data

    @property
    def pollen_list(self):
        return self._pollen_list

    def _fetch_data(self, url):
        r = requests.get(url)
        r.raise_for_status()
        return r.json()

    def _extract_legend(self, data):
        legend = {}
        for key, value in data.items():
            if not key.endswith("_desc"):
                legend[_convert_value(value)] = data[f"{key}_desc"]
        return legend

    def _extract_pollen_list(self, data, today):
        pollen_list = []
        for region in data:
            region_id = region["partregion_id"]
            if region_id == -1:
                region_id = region["region_id"]

            for name, prediction in region["Pollen"].items():
                for keyname, dayoffset in PREDICTION_LIST.items():
                    value = _convert_value(prediction[keyname])
                    if value is not None:
                        date = today + timedelta(days=dayoffset)
                        pollen_list.append(PollenForecast(region_id, name, date, value))
        return pollen_list

    def _extract_regions_list(self, data):
        regions = {}
        for entry in data:
            region_id = entry["region_id"]
            if region_id not in regions:
                regions[region_id] = Region(region_id, entry["region_name"], None)

            partregion_id = entry["partregion_id"]
            if partregion_id != -1:
                regions[partregion_id] = Region(
                    partregion_id, entry["partregion_name"], region_id
                )
        return regions

    def _extract_regions_with_data(self, data):
        regions = set()
        for entry in data:
            id = entry["partregion_id"]
            if id == -1:
                id = entry["region_id"]
            regions.add(id)
        return regions

    def _extract_data(self, data):
        # define timezone for DWD data
        tz = pytz.timezone(self._TIME_ZONE)
        self._last_update = tz.localize(
            datetime.strptime(data["last_update"], self._TIME_FORMAT_STR)
        )
        self._next_update = tz.localize(
            datetime.strptime(data["next_update"], self._TIME_FORMAT_STR)
        )
        self._name = data["name"]
        self._sender = data["sender"]

        self._legend = self._extract_legend(data["legend"])
        self._regions_list = self._extract_regions_list(data["content"])
        self._regions_with_data = self._extract_regions_with_data(data["content"])
        self._pollen_list = self._extract_pollen_list(
            data["content"], self._last_update.date()
        )

    def fetch(self):
        data = self._fetch_data(self.URL)
        self._extract_data(data)


def _convert_value(value):
    match = re.fullmatch(r"(\d+)-(\d*)", value)
    if match:
        x1 = int(match.group(1))
        x2 = int(match.group(2))
        if x1 + 1 != x2:
            raise ValueError(f"Invalid legend values: {x1}-{x2}")
        return x1 + 0.5
    else:
        x = int(value)
        return None if x == -1 else x
