from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler


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
