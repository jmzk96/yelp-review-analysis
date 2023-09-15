import os
import sys
import pandas as pd

module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)
module_path = os.path.abspath(os.path.join('.'))
if module_path not in sys.path:
    sys.path.append(module_path)
from src.database_handler import DatabaseHandler  # wrong-import-position: ignore
from sql_cleanup.closest_station import WeatherLinker  # wrong-import-position: ignore


def aggregate_weather(clusterid: int, station_data: pd.DataFrame):
    """Aggregates data from all given stations into one new avg for the cluster.
    Inserts the data into the database, using sql aggregations.

    Args:
        clusterid (int): Number of the cluster
        station_data (Dataframe): Dataframe with the station data
    """
    db_handler = DatabaseHandler()
    sql_options = {
        "clusterid": clusterid,
        "stationlist": tuple(station_data["sid"].tolist()),
    }
    sql = """INSERT INTO cluster_weather (
            select 
            %(clusterid)s as clusterid,
            date, 
            round(avg(NULLIF(tmax, 'NaN')), 2) as tmax,
            round(avg(NULLIF(tmin, 'NaN')), 2) as tmin,
            round(avg(NULLIF(perception, 'NaN')), 2) as perception,
            round(avg(NULLIF(snow, 'NaN')), 2) as snow,
            round(avg(NULLIF(snowdepth, 'NaN')), 2) as snowdepth
            from weather
            WHERE sid in %(stationlist)s and date >= '2004-01-01'
            GROUP BY date
            ORDER BY date)"""
    db_handler.querry_database(sql, sql_options)


def aggregate_all_cluster(weather_linker: WeatherLinker):
    """Iterates over each station data in the Weather linker and performes the aggregation

    Args:
        weather_linker (WeatherLinker): WeatherLinker class with best clusters
    """
    best_station_data = weather_linker.best_station_data
    for clusterid, station_dataframe in best_station_data.items():
        aggregate_weather(clusterid, station_dataframe)


if __name__ == "__main__":
    wl = WeatherLinker()
    wl.generate_best_stations()
    aggregate_all_cluster(wl)
