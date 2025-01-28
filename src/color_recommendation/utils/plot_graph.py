import json
import matplotlib.pyplot as plt
from matplotlib import colormaps
from mpl_toolkits.mplot3d import Axes3D
import os


def plot_graph_3d(data, clusters, output_file_path):
    """三次元のクラスターマップを作成する関数"""
    # カラーマップ設定
    num_clusters = len(set(clusters)) - (1 if -1 in clusters else 0)
    cmap = colormaps.get_cmap('hsv').resampled(num_clusters + 1)

    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')

    for cluster_label in set(clusters):
        clustered_data = data[clusters == cluster_label]
        color = 'k' if cluster_label == -1 else cmap(cluster_label / num_clusters)
        ax.scatter(
            clustered_data[:, 0], clustered_data[:, 1], clustered_data[:, 2],
            color=color, label=f'Cluster {cluster_label}' if cluster_label != -1 else 'Noise'
        )

    ax.set_xlabel('X-axis')
    ax.set_ylabel('Y-axis')
    ax.set_zlabel('Z-axis')
    plt.legend()
    plt.savefig(output_file_path)


def plot_graph(plot_data, graph_name, output_file_path):
    # プロット
    plt.plot(plot_data, label=f'{graph_name}', marker='o')
    plt.title(f'{graph_name}')
    plt.ylim(0, 1)
    plt.xlim(0, 60)
    plt.xlabel('color_scheme')
    plt.ylabel(f'{graph_name}')
    plt.grid(True)

    # ファイルに保存
    plt.savefig(output_file_path)


def calculate_recall(file_path):

    recalls = [0] * 100
    timing_count = 0

    with open(file_path, 'r') as f:
        data = json.load(f)

    # print(len(data))

    for illust_data in data:
        # print(illust_data['recall_at_k'])

        for illust_data_at_timing in illust_data['recall_at_k']:
            timing_count += 1
            # print(illust_data_at_timing)
            if (illust_data_at_timing['is_contained_next_color']):
                # print(illust_data_at_timing["k"])
                for i in range(illust_data_at_timing["k"], len(recalls)):
                    recalls[i] += 1

    for i in range(len(recalls)):
        # print(recalls[i])
        recalls[i] = round(100 * (recalls[i] / timing_count)) / 100

    return recalls


def save_plot_recall_at_k_for_illustrators(illustrator_list):
    """
    引数で受け取るリスト内のイラストレーターのrecall@kグラフを保存する関数

    引数:
        illutrator_list: 使用色を抽出させたいイラストレーターのリスト(文字列)
    戻り値:
        None

    """

    for illustrator_name in illustrator_list:
        IS_CONTAINED_NEXT_COLOR_FILE_PATH = f"src/color_recommendation/data/output/is_contained_next_color_{illustrator_name}.json"
        # GRAPH_PATH = f'src/color_recommendation/data/output/recall_at_k_{illustrator_name}.png'

        recalls = calculate_recall(IS_CONTAINED_NEXT_COLOR_FILE_PATH)
        # plot_graph(recalls, 'recall', output_file_path)

        # プロット
        plt.plot(recalls, label=f'{illustrator_name}', marker='o', markersize=0)

    plt.title("recall@k")
    plt.ylim(0, 1)
    plt.xlim(0, 60)
    plt.xlabel('color_scheme')
    plt.ylabel(f'recall')
    plt.grid(True)
    plt.legend(title="Illustrators", fontsize=10)

    # ファイルに保存
    GRAPH_PATH = f'src/color_recommendation/data/output/recall_at_k.png'
    plt.savefig(GRAPH_PATH)
    print(f"{GRAPH_PATH} が保存されました．(グラフの作成)")


def plot_recall_at_k(input_file_path, output_file_path):

    recalls = calculate_recall(input_file_path)
    plot_graph(recalls, 'recall', output_file_path)
    # print(timing_count)
    # print(recalls)


def plot_scatter(illustrator_name):
    """
    引数で受け取るイラストレーターの使用色の散布図をプロットする関数

    引数:
        illustrator_name: イラストレーター名

    戻り値:
        None
    """
    print(f"=== {illustrator_name} ====================")

    input_file_path = f"src/color_recommendation/data/input/used_colors_{illustrator_name}.json"

    # ファイルの読み込み
    try:
        if not os.path.exists(input_file_path):
            raise FileNotFoundError(f"File not found: {input_file_path}")
            return

        with open(input_file_path, 'r') as f:
            data = json.load(f)
            print(f"{input_file_path} が読み込まれました．")

    except FileNotFoundError as e:
        print(f"エラー: {e}")
        return
    except json.JSONDecodeError as e:
        print(f"JSONデコードエラー: {e}. ファイルの内容を確認してください。")
        return
    except Exception as e:
        print(f"予期しないエラーが発生しました: {e}")
        return

    # 明度と彩度を計算
    lightness_list = []
    saturation_list = []
    color_labels = []
    sizes = []

    for illustration in data:
        for color_info in illustration:
            hex_color = color_info["color"]
            # HexカラーをRGBに変換
            r = int(hex_color[1:3], 16) / 255.0
            g = int(hex_color[3:5], 16) / 255.0
            b = int(hex_color[5:7], 16) / 255.0

            # 明度（Lightness）計算
            lightness = (max(r, g, b) + min(r, g, b)) / 2
            lightness_list.append(lightness)

            # 彩度（Saturation）計算
            if max(r, g, b) == min(r, g, b):  # グレースケール
                saturation = 0
            else:
                saturation = (max(r, g, b) - min(r, g, b)) / (1 - abs(2 * lightness - 1))
            saturation_list.append(saturation)

            # 色ラベルを保存（散布図の色用）
            color_labels.append(hex_color)
            sizes.append(color_info["rate"] * 400)

    # 散布図を作成
    plt.figure(figsize=(8, 6))
    plt.scatter(saturation_list, lightness_list, s=sizes, c=color_labels, edgecolor=None)

    # グラフの設定
    plt.title(f'{illustrator_name}', fontsize=14)
    plt.xlabel('Saturation', fontsize=12)
    plt.ylabel('Lightness', fontsize=12)
    plt.grid(True)
    # plt.show()

    output_file_path = f'src/color_recommendation/data/output/scatter_plot_{illustrator_name}.png'

    plt.savefig(output_file_path)
    print(f"{output_file_path} が保存されました．")
    print(f"イラスト:  src/color_recommendation/data/input/illustration/{illustrator_name}")

    plt.close()


def main():
    plot_recall_at_k("src/color_recommendation/data/output/test_is_contained_next_color_simple_data.json", 'src/color_recommendation/data/output/test_recall_at_k.png')


if __name__ == '__main__':
    main()
