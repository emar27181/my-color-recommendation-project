from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import numpy as np


def clustering_color_counts(color_counts_tuple, EPS, MIN_SAMPLES):
    """引数で受け取る色とその出現回数を閾値を基にクラスタリングする関数
    引数: 
        data: クラスタリング対象の3次元データ
        EPS: 近傍の半径（ある点の近くをどこまで「近い」とみなすか）の閾値
        MIN_SAMPLES: クラスタとして認識するために必要な最小の点数の閾値
    戻り値:
        colors_array: クラスタリングされた色(rgb値)を保存するnumpy配列 (ex. colors_array[k]: k番目の色のrbg値)
        clusters: クラスタ番号を保存する配列 (ex. clusters[k]: k番目の色のクラスタ番号)
    """

    colors_list = []  # color_list: 量子化された後の色のリスト
    for color in color_counts_tuple:
        colors_list.append(color)

    colors_array = np.array(colors_list)  # color_array: 量子化された後の色のnumpy配列
    normalized_colors_array = colors_array / 255.0

    clusters = clustring_dbscan_3d(normalized_colors_array, EPS, MIN_SAMPLES)
    return colors_array, clusters


def clustring_dbscan_3d(data_3d, EPS, MIN_SAMPLES):
    """受け取ったデータをDBSCANクラスタリングでクラスタリングする関数
    data: クラスタリング対象の3次元データ
    EPS: 近傍の半径（ある点の近くをどこまで「近い」とみなすか）の閾値
    MIN_SAMPLES: クラスタとして認識するために必要な最小の点数の閾値
    """

    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(data_3d)

    dbscan = DBSCAN(eps=EPS, min_samples=MIN_SAMPLES)
    clusters = dbscan.fit_predict(data_scaled)

    return clusters
