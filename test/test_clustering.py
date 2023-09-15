import pandas as pd
from sql_cleanup.clean_and_link import KmeansClusterClass

N_CLUSTER = 2
dat = [
    ["a", 1, 1],
    ["b", 1.2, 1.3],
    ["c", 5, 5],
    ["d", 5.4, 5],
]
col = ["bid", "lat", "lon"]
df_data = pd.DataFrame(dat, columns=col)


def test_should_generate_right_cluster_amount():
    kcc = KmeansClusterClass(df_data, N_CLUSTER)
    assert len(kcc.cluster_centers) == N_CLUSTER


def test_should_cluster_elements_right():
    kcc = KmeansClusterClass(df_data, N_CLUSTER)
    cluster_list = kcc.bid_cluster
    # cluster 1
    assert cluster_list[0][1] == cluster_list[1][1]
    # cluster 2
    assert cluster_list[2][1] == cluster_list[3][1]
