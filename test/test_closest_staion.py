import pandas as pd
import numpy as np
from unittest import mock
from sql_cleanup.closest_station import WeatherLinker


# mock for weather df
col = ["lat", "lon", "name", "sid", "days"]
dat = [
    [1, 1.005, "a", "a", 1000],
    [2, 2, "b", "b", 1000],
    [1, 1, "c", "c", 500],
    [2, 2, "d", "d", 500],
    [1, 1.005, "e", "e", 1],
]
weather_df = pd.DataFrame(dat, columns=col)
weather_df["sqrt_days"] = weather_df["days"].apply(np.sqrt)

# mock for cluster df
col = ["clusterid", "lon", "lat", "clustername"]
dat = [
    [1, 1.05, 1.04, "ca"]
]
cluster_df = pd.DataFrame(dat, columns=col)

# mock for station df
col = ["sid", "lon", "lat"]
dat = [
    ["a", 1, 1, ],
    ["b", 2, 2, ],
    ["c", 1, 1, ],
    ["d", 2, 2, ],
    ["e", 1, 1.005, ],
]
station_df = pd.DataFrame(dat, columns=col)


def test_quality_should_select_right():
    with mock.patch.object(WeatherLinker, "__init__", lambda x, y, z: None):
        # this mock is nececary to remove the database calls
        wl = WeatherLinker(2, 2)
        wl.best_station_data = {}
        wl.closest_station_data = {}
        wl.weather_df = weather_df
        wl.cluster_df = cluster_df
        wl.station_df = station_df
        wl.n_closest = 2
        wl.n_best = 2

        wl.generate_best_stations()
        sid_list = wl.best_station_data[1]["sid"].tolist()
        assert "a" in sid_list
        assert "c" in sid_list


def test_closest_should_select_right():
    with mock.patch.object(WeatherLinker, "__init__", lambda x, y, z: None):
        # this mock is nececary to remove the database calls
        wl = WeatherLinker(2, 2)
        wl.best_station_data = {}
        wl.closest_station_data = {}
        wl.weather_df = weather_df
        wl.cluster_df = cluster_df
        wl.station_df = station_df
        wl.n_closest = 2
        wl.n_best = 2

        wl.generate_closest_stations()
        sid_list = wl.closest_station_data[1]["sid"].tolist()
        assert "a" in sid_list
        assert "e" in sid_list
