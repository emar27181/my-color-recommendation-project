from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import numpy as np
from utils.helpers.color_utils import calc_weighted_average_rgb, print_colored_text


def calc_clusterd_color_counts(color_counts_tuple, colors_array, clusters):
    """
    使用色とその出現回数をクラスタリング結果を基に計算する関数

    引数:
        color_counts_tuple: 量子化されたrgb値とその出現回数を保存する辞書型タプル(例. color_counts_tuple(r,g,b): (r,g,b)の出現回数))
        colors_array: 量子化されたrgb値を保存する配列(例. color_array[i]: i番目のrgb値)
        clusters: クラスタ番号を保存するリスト(例. clusters[i]: i番目のrgbのクラスタ番号)

    戻り値: 
        clusterd_color_counts: クラスタリングされたあとの使用色と出現回数を保存するリスト

    """

    clusterd_color_counts = [
        {"color": [-1, -1, -1], "count": -1, "rate": -1} for _ in range(max(clusters) + 1)
    ]

    # クラスタに分類されている色だった場合，色と出現回数を更新
    for i, cluster_number in enumerate(clusters):
        # クラスタに分類されている場合
        if cluster_number != -1:
            based_color = clusterd_color_counts[cluster_number]["color"]
            based_color_count = clusterd_color_counts[cluster_number]["count"]
            add_color = tuple(colors_array[i])
            add_color_count = color_counts_tuple[tuple(colors_array[i])]

            # 色の出現回数の初期化
            if (clusterd_color_counts[cluster_number]["count"] < 0):
                clusterd_color_counts[cluster_number] = {"color": add_color, "count": add_color_count, "rate": -1}
            # 色の出現回数のインクリメント
            else:
                clusterd_color_counts[cluster_number]["count"] += add_color_count
                clusterd_color_counts[cluster_number]["color"] = calc_weighted_average_rgb(based_color, add_color, based_color_count, add_color_count)
                # 確認用出力
                if (False):
                    print(f"cluster_number =  {cluster_number}:    ", end="")
                    print_colored_text("■■ ", based_color)
                    print(f"{based_color} × {based_color_count}", end=", ")
                    print_colored_text("■■ ", add_color)
                    print(f"{colors_array[i]} × {add_color_count}")

    clusterd_color_counts = sorted(clusterd_color_counts, key=lambda x: x['count'], reverse=True)

    return clusterd_color_counts


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
