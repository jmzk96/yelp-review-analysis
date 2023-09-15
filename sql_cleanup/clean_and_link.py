import os
import sys
from typing import List
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans

module_path = os.path.abspath(os.path.join('.'))
if module_path not in sys.path:
    sys.path.append(module_path)
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

from src.database_handler import DatabaseHandler  # wrong-import-position: ignore
from src.utils import timer  # wrong-import-position: ignore


CLUSTER_COUNT = 10


class KmeansClusterClass:
    """Class to fit clusters to the business from location data.
    Uses Kmeans clustering from sklearn

    Args:
        dataframe (pd.DataFrame): Dataframe containing, bid, lon, lat
        number_of_clusters (int): Numbers of clusters to cluster to
    """

    def __init__(self, dataframe: pd.DataFrame, number_of_clusters: int):
        print("Creating Cluster Predictor")
        self.dataframe = dataframe
        self.number_of_clusters = number_of_clusters
        self.cluster_centers: List = []
        self.bid_cluster: List = []
        self.__create_clusters()

    @timer
    def __create_clusters(self):
        """Creates the K-Means clusters by fitting with data from numpy array
        uses lon and lat data, as well as the given cluster amount
        """
        print(f"Fitting Business data to {CLUSTER_COUNT} cluster")
        clusteringk = KMeans(n_clusters=self.number_of_clusters)
        fit_array = np.array(self.dataframe[["lat", "lon"]].values.tolist())
        clusteringk.fit(fit_array)
        cluster_centers = clusteringk.cluster_centers_

        self.dataframe["clusterid"] = clusteringk.labels_
        self.dataframe["clusterid"] += 1
        self.bid_cluster = self.dataframe[["bid", "clusterid"]].values.tolist()
        self.cluster_centers = [[index + 1, x, y] for index, (x, y) in enumerate(cluster_centers)]


class Updater:
    """Class to update data from the initial state in the Database.
    This includes Clustering, linking Clusters and linking to Weatherstations.
    """

    def __init__(self):
        self.__handler = DatabaseHandler()
        self.__querry = self.__handler.querry_database
        self.__insert_many = self.__handler.insert_many
        self.__kmeans_cc: KmeansClusterClass = None
        self.__init_kmeans_cluster_class()
        print("Ready to Update Data!")

    def __get_needed_business_data(self) -> pd.DataFrame:
        sql = """SELECT bid, lat, lon FROM business"""
        col = ["bid", "lat", "lon"]
        df_data = pd.DataFrame(data=self.__querry(sql), columns=col)
        return df_data

    def __init_kmeans_cluster_class(self):
        business_data = self.__get_needed_business_data()
        self.__kmeans_cc = KmeansClusterClass(business_data, CLUSTER_COUNT)

    @timer
    def insert_cluster_data(self):
        """Inserts the cluster data for the estimated cluster
        """
        sql = "INSERT INTO cluster(clusterid, lat, lon) values %s"
        values = self.__kmeans_cc.cluster_centers
        print("Inserting the cluster data")
        self.__insert_many(sql, values)

    @timer
    def update_business_cluster_data(self):
        """Updates the business cluster for the estimated cluster
        """
        sql = """UPDATE business
        set clusterid = data.clusterid
        from (values %s) as data (bid, clusterid)
        where business.bid = data.bid
        """
        values = self.__kmeans_cc.bid_cluster
        print("Updating the clusterids on the business data")
        self.__insert_many(sql, values)


if __name__ == "__main__":
    updater = Updater()
    updater.insert_cluster_data()
    updater.update_business_cluster_data()
