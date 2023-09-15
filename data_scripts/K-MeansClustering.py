from SynchroInfoYelp import open_json_file
from sklearn.cluster import KMeans
from scipy.cluster.vq import kmeans,vq
from scipy.spatial.distance import cdist
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeat


class KMeans_Clustering:
    """
    KMeans_Clustering clusters latitude and longitude positions of a dataframe to clusters using K Means.
    This is a preliminary level code for K-Means and is still in development. Improvements to the model is needed.
    For Example:
        a)the distance calculated for within each cluster (see elbow_curve method) uses the cityblock model, where the distance uses cityblocks as a 
        metric for calculating distance.
        b) maximum number of clusters that can be plotted is 16, (a smarter way of generating a random colour for each cluster has not been
        successfully found)

    To plot the map, a wheel file needs to be downloaded. This Python Library is called cartopy. More Details to Download can be found in this Link:
    https://www.youtube.com/watch?v=PGNzs1I6tf0&t=253s
    """
    def __init__(self, Dataframe, number_of_clusters):
        """
        init constructs the class object with necessary attributes.
        """
        self.Dataframe = Dataframe
        self.number_of_clusters = number_of_clusters
        self.array = self.convert_to_array()
        self.km_clusters = None
        self.cluster_centers = self.__create_clusters()
        self.bid_cluster = self.list_bid_cluster()

    def convert_to_array(self):
        """ 
        converts dataframe longitude and latitude column in numpy array
        """
        array_lat_long = np.array(self.Dataframe[["latitude", "longitude"]].values.tolist())
        return array_lat_long

    def create_clusters(self):
        """
        Creates the K-Means clusters by fitting with data from numpy array (see above method) and giving out cluster centers
        """
        clusteringk = KMeans(n_clusters=self.number_of_clusters)
        clusteringk.fit(self.array)
        cluster_centers = clusteringk.cluster_centers_
        self.km_clusters = clusteringk.labels_
        return [[index + 1, x, y] for index, (x, y) in enumerate(cluster_centers)]

    def predict_clusters(self):
        """
        Assigns each location in numpy Array to the created K-Means Clusters
        """
        clusteringk = KMeans(n_clusters=self.number_of_clusters)
        clusteringk.fit(self.array)
        km_clusters = clusteringk.fit_predict(self.array)
        return km_clusters

    def plot_clusters(self, width_map, height_map):

        """
        Plots out locations on a graph without map
        """
        plotfig = plt.figure(figsize=(width_map, height_map))

        list_of_colours = ["blue", "red", "black", "orange", "yellow", "purple", "grey", "green", "lavender", "#e5ae38",
                           "#8dd3c7", "#FBC15E", "#CC79A7", "#8EBA42", "#b3de69", "#cbcbcb"]
        for i in range(0, self.number_of_clusters):
            plt.scatter(self.array[self.km_clusters == i, 1], self.array[self.km_clusters == i, 0],
                        color=list_of_colours[i], label=f"{i + 1}.Cluster")
        plt.legend()
        plt.show()

    def plot_clusters_map(self, width_map, height_map):
        
        """
        Plots out locations on a graph with map (CARTOPY NEEDED!!!)
        The map shows clusters for locations in the US of A only!!
        
        """
        plotfig = plt.figure(figsize=(width_map, height_map))
        earth = plt.axes(projection=ccrs.PlateCarree())
        earth.add_feature(cfeat.LAND)
        earth.add_feature(cfeat.OCEAN)
        earth.add_feature(cfeat.COASTLINE)
        earth.add_feature(cfeat.BORDERS, linestyle=":")
        earth.add_feature(cfeat.STATES)
        earth.set_extent([-162, -68, 19, 65])
        # [-114,-111,33,34] example cluster
        list_of_colours = ["blue", "red", "black", "orange", "yellow", "purple", "grey", "green", "lavender", "#e5ae38",
                           "#8dd3c7", "#FBC15E", "#CC79A7", "#8EBA42", "#b3de69", "#cbcbcb"]
        for i in range(0, self.number_of_clusters):
            earth.scatter(self.array[self.km_clusters == i, 1], self.array[self.km_clusters == i, 0],
                          color=list_of_colours[i], label=f"{i + 1}.Cluster")
        plt.legend()
        plt.show()

    def elbow_curve(self, estimate_number_of_clusters):
        
        """
        Plots out elbow curve with number of clusters to be estimated on X-Axis and the Average within Clusters sum of squares on Y-Axis to 
        investigate the magnitude of Error
        """

        K = range(1, estimate_number_of_clusters)

        # scipy.cluster.vq.kmeans
        KM = [kmeans(self.array, k) for k in K]  # apply kmeans 1 to 10
        centroids = [cent for (cent, var) in KM]  # cluster centroids

        D_k = [cdist(self.array, cent, 'euclidean') for cent in centroids]
        dist = [np.min(D, axis=1) for D in D_k]
        avgWithinSS = [sum(d) / self.array.shape[0] for d in dist]
        fig = plt.figure()
        plt.plot(K, avgWithinSS, 'b*-')

        plt.grid(True)
        plt.xlabel('Number of clusters')
        plt.ylabel('Average within-cluster sum of squares')
        tt = plt.title('Elbow for K-Means clustering')
        plt.show()

    def list_long_lat_cluster(self):
        
        """
        Gives out Latitude, Longitude and Cluster of each location in Dataframe (Database ready)
        """
        list_of_dfs = []
        for i in range(0, self.number_of_clusters):
            x = pd.DataFrame(
                {"Longitude": self.array[self.km_clusters == i, 1], "Latitude": self.array[self.km_clusters == i, 0],
                 "Cluster": i + 1})
            list_of_dfs.append(x)
        df_data = pd.concat(list_of_dfs, ignore_index=True)
        list_of_list = df_data.values.tolist()
        return list_of_list

    def list_bid_cluster(self):
        self.Dataframe["Cluster"] = self.km_clusters
        self.Dataframe["Cluster"] += 1
        return self.Dataframe[["business_id", "Cluster"]].values.tolist()