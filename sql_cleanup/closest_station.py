import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

from src.database_handler import DatabaseHandler  # wrong-import-position: ignore
from src.utils import timer  # wrong-import-position: ignore

# Default code for pretty graphs
# Generierung der Allgemeinen Größen für Beschriftung und Diagramme:


def define_plot_styles():
    ls_head = 20  # Überschrift
    ls_axis = 18  # x/y-Beschriftung
    ls_font = 16  # Schrif (zB .text)
    ls_label = 16  # Werte x/y-Achse
    ls_legend = 16  # Schriftgröße der Legende
    figsize = (20, 8)
    alphalegend = 0.9
    s_dpi = 300

    # Übergabe in ein Dict und anschließend aktualisieren der Parameter
    rc = {'figure.figsize': figsize,
          'legend.framealpha': alphalegend,
          'axes.labelsize': ls_axis, 'font.size': ls_font, 'legend.fontsize': ls_legend,
          'axes.titlesize': ls_head, 'xtick.labelsize': ls_label, 'ytick.labelsize': ls_label,
          'grid.color': 'k', 'grid.linestyle': '--',
          "savefig.dpi": s_dpi, "savefig.format": 'svg'}
    plt.rcParams.update(**rc)


define_plot_styles()
COLORS = [
    "deepskyblue",
    "skyblue",
    "steelblue",
    "dodgerblue",
    "royalblue",
    "cornflowerblue",
    "navy",
    "blue",
    "mediumblue",
    "aqua",
]


def calculate_distance(x, lon, lat):
    lon_s = x["lon"]
    lat_s = x["lat"]
    distance = np.sqrt(float((lon_s - lon)**2 + (lat_s - lat)**2))
    return distance


def calculate_quality(x):
    sqrt_days = x["sqrt_days"]
    distance = x["distance"]
    return sqrt_days / distance**2


class WeatherLinker:
    """Class to generate the quality of each station to the clustes

    Args:
        n_closest (int, optional): Number of closest station to get. Defaults to 100.
        n_best (int, optional): Number of ordered best station to get. Defaults to 5.
    """

    def __init__(self, n_closest: int = 100, n_best: int = 5):
        self.__handler = DatabaseHandler()
        self.__query = self.__handler.querry_database
        self.__insert_many = self.__handler.insert_many
        self.best_station_data = {}
        self.closest_station_data = {}
        self.weather_df = self.__get_weather_data()
        self.cluster_df = self.__get_cluster_data()
        self.station_df = self.__get_station_data()
        self.n_closest = n_closest
        self.n_best = n_best
        print("Ready to go!")

    def __get_weather_data(self) -> pd.DataFrame:
        sql = """select lat, lon, name, a.sid, days
                from stationdata as a inner join
                (select sid, count(*) as days from weather where date >= '2004-01-01' group by sid) as b
                on a.sid = b.sid"""
        col = ["lat", "lon", "name", "sid", "days"]
        data = self.__query(sql)
        df_data = pd.DataFrame(data, columns=col)
        df_data["sqrt_days"] = df_data["days"].apply(np.sqrt)
        return df_data

    def __get_cluster_data(self) -> pd.DataFrame:
        sql = "select clusterid, lon, lat, clustername from cluster"
        col = ["clusterid", "lon", "lat", "clustername"]
        data = self.__query(sql)
        return pd.DataFrame(data, columns=col)

    def __get_station_data(self) -> pd.DataFrame:
        sql = "select sid, lon, lat from stationdata"
        col = ["sid", "lon", "lat"]
        data = self.__query(sql)
        return pd.DataFrame(data, columns=col)

    @timer
    def generate_closest_stations(self):
        """Calculate the clostest n station based on n_closest"""
        print(f"Getting the closest {self.n_closest} station for each cluster for all stations")
        for _, row in self.cluster_df.iterrows():
            clusterid = row["clusterid"]
            agg_df = self.station_df.copy()
            agg_df["distance"] = agg_df.apply(calculate_distance, axis=1, args=(row["lon"], row["lat"]))
            result_df = agg_df.sort_values(by=['distance'], ascending=True).iloc[:self.n_closest].copy()
            self.closest_station_data[clusterid] = result_df

    @timer
    def generate_best_stations(self):
        """Calculate the n best station based on n_best"""
        print(f"Getting the best {self.n_best} weather station for each cluster")
        for _, row in self.cluster_df.iterrows():
            clusterid = row["clusterid"]
            agg_df = self.weather_df.copy()
            agg_df["distance"] = agg_df.apply(calculate_distance, axis=1, args=(row["lon"], row["lat"]))
            agg_df["quality"] = agg_df.apply(calculate_quality, axis=1)
            result_df = agg_df.sort_values(by=['quality'], ascending=False).iloc[:self.n_best].copy()
            self.best_station_data[clusterid] = result_df

    def generate_control_plot(self, figname: str = "best_station") -> plt.figure:
        """Generates and saves the control plot (plot of cluster and best station) to a file.

        Args:
            figname (str, optional): Name of the svg to save. Defaults to "closest_station".

        Returns:
            plt.figure: Plot Object
        """

        fig, axes = plt.subplots()
        self.weather_df[["lat", "lon"]].astype(float).plot.scatter(y='lat', x='lon', ax=axes, color="k", s=5)
        for color, (_, value) in zip(COLORS, self.best_station_data.items()):
            value[["lat", "lon"]].astype(float).plot.scatter(y='lat', x='lon', ax=axes,
                                                             s=value["days"] / 50, color=color, alpha=0.8)
        self.cluster_df[["lat", "lon"]].astype(float).plot.scatter(
            y='lat', x='lon', ax=axes, color="red", s=1500, alpha=0.15)
        axes.set_title(f"Best {self.n_best} station for each cluster")
        plt.savefig(f"{figname}.svg")
        return fig

    def generate_closest_station_plot(self, figname: str = "closest_station") -> plt.figure:
        """Generates a plot with the selected n closest station highlighted and all other also small shown

        Args:
            figname (str, optional): Name of the svg to save. Defaults to "closest_station".

        Returns:
            plt.figure: Plot Object
        """
        fig, axes = plt.subplots()
        self.station_df[["lat", "lon"]].astype(float).plot.scatter(y='lat', x='lon', ax=axes, color="k", s=1, alpha=0.2)
        for color, (_, value) in zip(COLORS, self.closest_station_data.items()):
            value[["lat", "lon"]].astype(float).plot.scatter(y='lat', x='lon', ax=axes, s=50, color=color, alpha=0.8)
        self.cluster_df[["lat", "lon"]].astype(float).plot.scatter(
            y='lat', x='lon', ax=axes, color="red", s=1500, alpha=0.15)
        axes.set_xlim([-130, -60])
        axes.set_ylim([22, 53])
        axes.set_title(f"Closest {self.n_closest} station for each cluster")
        plt.savefig(f"{figname}.svg")
        return fig
