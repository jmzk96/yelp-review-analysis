import os
import sys
import shutil
import re
from pathlib import Path

module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)
module_path = os.path.abspath(os.path.join('.'))
if module_path not in sys.path:
    sys.path.append(module_path)
from sql_setup.populate_db import DataPreparator  # wrong-import-position: ignore
from sql_cleanup.closest_station import WeatherLinker  # wrong-import-position: ignore


def copy_needed_dly(weather_linker: WeatherLinker, source_folder: str, dest_folder: str):
    """Search in the source folder for all data of the closest station from the
    WeatherLinker class and copies them to the dest folder

    Args:
        wl (WeatherLinker): Weather linker Class, with generated closest station
        source_folder (str): Path to source folder
        dest_folder (str): Path to dest folder
    """
    sid_list = []
    for _, value in weather_linker.closest_station_data.items():
        sid_list.extend(value["sid"].tolist())

    # We only need stations which are not into the weather data yet
    # Otherwise we will get a psycopg error (data already exists in db)
    already_existing_sid = set(weather_linker.weather_df["sid"].tolist())
    sid_list = list(set(sid_list).difference(already_existing_sid))

    print("Writing new stations to 'new_sid.txt'")
    with open("new_sid.txt", "w") as txtfile:
        txtfile.write(str(sid_list))

    filelist = Path(source_folder).rglob('*.dly')
    print(f"Copy matches for new stations from {source_folder} to {dest_folder}")
    for path in filelist:
        str_path = str(path)
        find = re.search(r"(\w{11}).dly", str_path)
        # there may be an inconsistency with the naming in very rare occasions, resulting in no group find
        if find is None:
            continue
        station_id = find.group(1)
        if station_id in sid_list:
            shutil.copy(str_path, dest_folder)


def init_weather_linker(n_best: int, n_closest: int, best_plot_name: str) -> WeatherLinker:
    """Initializes the weather linker and generates the station Data

    Args:
        n_best (int): Number of best Station to get
        n_closest (int): Number of closest Station to get
        best_plot_name (str): Name to save the control plot

    Returns:
        WeatherLinker: WeatherLinker: Initialized WeaterLinker class with closest and best station
    """
    weather_linker = WeatherLinker(n_best=n_best, n_closest=n_closest)
    weather_linker.generate_best_stations()
    weather_linker.generate_closest_stations()
    weather_linker.generate_control_plot(best_plot_name)
    return weather_linker


dp = DataPreparator()

if __name__ == "__main__":
    # Change source and dest if needed
    # SOURCE = r"D:\ghcnd_all\ghcnd_all"
    # DESTINATION = r"D:\ghcnd_selected"
    SOURCE = r"/home/gruppe-3/sql_cleanup/ghcnd_all/"
    DESTINATION = r"/home/gruppe-3/sql_cleanup/ghcnd_selected/"
    wl = init_weather_linker(10, 200, "best_station_pre_import")
    wl.generate_closest_station_plot()
    copy_needed_dly(wl, SOURCE, DESTINATION)
    dp = DataPreparator()
    dp.insert_weather(folderpath=DESTINATION)
    wl2 = init_weather_linker(10, 200, "best_station_after_import")
