import json
import matplotlib.pyplot as plt
from utils.helpers.json_utils import get_json_data
from matplotlib import colormaps
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
import seaborn as sns
import os
import colorsys
import itertools

DEBUG = False


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


def calculate_recall(file_path, recommend_colors_count):
    """
    引数:
        recommend_colors_count: 推薦配色(パターン)の数
    """

    recalls = [0] * recommend_colors_count
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


def _get_recommend_colors_count(illustrator_name, sort_type):
    input_file_path = f"src/color_recommendation/data/output/recommend_colors/sort_by_{sort_type}/recommend_colors_{illustrator_name}.json"
    data = get_json_data(input_file_path)
    return len(data[0]['recommend_color_schemes'])


def save_plot_recall_at_k_for_illustrators(illustrator_list, sort_type):

    recommned_colors_count = _get_recommend_colors_count(illustrator_list[0], sort_type)

    # マーカーと線種の候補リスト
    markers = itertools.cycle(['o', 's', 'v', '^', 'd', '>', '<', 'p', '*', 'h'])
    linestyles = itertools.cycle(['-', '--', '-.', ':'])

    for illustrator_name in illustrator_list:
        IS_CONTAINED_NEXT_COLOR_FILE_PATH = f"src/color_recommendation/data/output/is_contained_next_color/{sort_type}/is_contained_next_color_{illustrator_name}.json"
        recalls = calculate_recall(IS_CONTAINED_NEXT_COLOR_FILE_PATH, recommned_colors_count)

        # マーカーサイズは適度なサイズに設定し、線種も適用
        plt.plot(recalls,
                 label=illustrator_name,
                 marker=next(markers),
                 markersize=0,
                 linestyle=next(linestyles))

    plt.title(f"recall@k sort_type={sort_type}")
    plt.ylim(0, 1)
    plt.xlim(0, recommned_colors_count)
    plt.xlabel('color_scheme')
    plt.ylabel('recall')
    plt.grid(True)

    # 凡例はフォントサイズや位置も調整可能
    plt.legend(title="Illustrators", fontsize=5, loc='upper left')

    GRAPH_PATH = f'src/color_recommendation/data/output/recall_at_k_{sort_type}.png'
    plt.savefig(GRAPH_PATH, bbox_inches="tight")  # bbox_inchesを指定するとレイアウトが崩れにくい
    print(f"{GRAPH_PATH} が保存されました．(グラフの作成)")


"""
def plot_recall_at_k(input_file_path, output_file_path):

    recalls = calculate_recall(input_file_path)
    plot_graph(recalls, 'recall', output_file_path)
    # print(timing_count)
    # print(recalls)
"""


def _extract_used_hues_count_from_json(illustrator_name):
    """
    引数で受け取るイラストレーターの使用色相(有彩色)の数の分布を抽出する関数

    引数:
        illustrator_name: イラストレーター名

    戻り値:
        used_hues_count: 有彩色の数の分布を格納するリスト(ex. used_hues_count[2] = 3 → 有彩色の数が2のイラストが3つある)
    """

    input_file_path = f"src/color_recommendation/data/input/used_hues/used_hues_{illustrator_name}.json"
    used_hues_count = [0] * 20  # 有彩色の数の分布を格納するリスト(ex. used_hues_count[2] = 3 → 有彩色の数が2のイラストが3つある)

    data = get_json_data(input_file_path)

    for illust_data in data:
        illust_name = illust_data["illust_name"]
        used_hues_rate = illust_data["used_hues_rate"]
        chromatic_colors_count = illust_data["chromatic_colors_count"]
        achromatic_colors_count = illust_data["achromatic_colors_count"]
        used_chromatic_hues = illust_data["used_chromatic_hues"]

        if (DEBUG):
            print(f"=== {illust_name} ==========")
            print(f"chromatic_colors_count = {chromatic_colors_count}, achromatic_colors_count = {achromatic_colors_count}")
        used_hues_count[chromatic_colors_count] += 1

    return used_hues_count


def _extract_used_achromatic_colors_average_rate_from_json(illustrator_name):
    """
    引数で受け取るイラストレーターの使用無彩色の平均比率を抽出する関数

    引数:
        illustrator_name: イラストレーター名

    戻り値:
        used_achromatic_colors_average_rate: 使用無彩色の平均比率
    """

    input_file_path = f"src/color_recommendation/data/input/used_hues/used_hues_{illustrator_name}.json"

    data = get_json_data(input_file_path)

    used_achromatic_colors_rate_sum = 0

    for illust_data in data:
        illust_name = illust_data["illust_name"]
        used_hues_rate = illust_data["used_hues_rate"]

        for hue_data in used_hues_rate:
            if (hue_data[0] == -10):  # 白の場合
                used_achromatic_colors_rate_sum += hue_data[1]
            elif (hue_data[0] == -11):  # 黒の場合
                used_achromatic_colors_rate_sum += hue_data[1]

    return used_achromatic_colors_rate_sum / len(data)


def save_plot_bar_from_used_achromatic_colors_average_rate_for_illustrators(illustrator_list):
    """
    引数で受け取るリスト内のイラストレーターの使用無彩色の平均比率を
    棒グラフ（積み上げ棒グラフ）にプロットする関数

    引数:
        illustrator_list: 使用色を抽出させたいイラストレーターのリスト(文字列)

    戻り値:
        None
    """

    used_achromatic_colors_average_rate_for_illustrators = {}

    # 各イラストレーターの使用無彩色の平均比率を取得
    for illustrator_name in illustrator_list:
        used_achromatic_colors_average_rate = _extract_used_achromatic_colors_average_rate_from_json(illustrator_name)
        print(f"=== {illustrator_name} ====================")
        print(f"used_achromatic_colors_average_rate = {used_achromatic_colors_average_rate}")
        used_achromatic_colors_average_rate_for_illustrators[illustrator_name] = used_achromatic_colors_average_rate

    # イラストレーター名と無彩色の比率をリスト化
    illustrators = list(used_achromatic_colors_average_rate_for_illustrators.keys())
    achromatic_rates = list(used_achromatic_colors_average_rate_for_illustrators.values())

    # 積み上げ棒グラフの描画
    plt.figure(figsize=(20, 10))
    # 無彩色部分（灰色）を描画
    plt.bar(illustrators, achromatic_rates, color='#AAAAAA', label='achromatic_rate')
    # 有彩色部分（赤色）：高さは (1 - 無彩色の割合) で、bottom を無彩色の割合に指定
    plt.bar(illustrators, [1 - rate for rate in achromatic_rates], bottom=achromatic_rates, color='#990000', label='choromatic_rate')

    plt.title("Used Achromatic Colors Average Rate by Illustrator")
    plt.xlabel("Illustrator")
    plt.ylabel("achromatic rate vs chromatic rate")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()

    output_file_path = 'src/color_recommendation/data/output/bar_from_used_achromatic_colors_average_rate.png'
    plt.savefig(output_file_path)
    print(f"{output_file_path} が保存されました．")


def _extract_mean_resultant_length_from_json(illstrator_name):
    """ jsonファイルからイラストレーターの平均結果長の分布を抽出する関数
    """

    input_file_path = f"src/color_recommendation/data/input/statistics_for_illustrators.json"
    data = get_json_data(input_file_path)

    for illstrator_data in data:
        if (illstrator_name == illstrator_data["illustrator_name"]):
            mean_resultant_length_distribution = illstrator_data["mean_resultant_length_distribution"]
            return mean_resultant_length_distribution
    return None


def save_plot_violin_from_mean_resultant_length_count_for_illustrators(illustrator_list):
    """
    引数で受け取るリスト内のイラストレーターの平均結果長の分布をヴァイオリン図にプロットする関数

    引数:
        illustrator_list: 使用色を抽出させたいイラストレーターのリスト(文字列)

    戻り値:
        None
    """

    mean_resultant_length_distribution_for_illustrators = {}

    # 各イラストレーターの使用色相(有彩色)の数の分布を取得
    for illustrator_name in illustrator_list:
        mean_resultant_length_distribution = _extract_mean_resultant_length_from_json(illustrator_name)
        print(f"=== {illustrator_name} ====================")
        mean_resultant_length_distribution_for_illustrators[illustrator_name] = mean_resultant_length_distribution

    # データを「イラストレータ」「要素番号」の形に“出現回数ぶん”展開
    records = []
    for illustrator, counts in mean_resultant_length_distribution_for_illustrators.items():
        for element_idx, count in enumerate(counts):
            # その要素が count 回出てくるとみなし，countぶんだけ同じ行を追加
            records.extend([{"Illustrator": illustrator, "Element": element_idx}] * count)

    df = pd.DataFrame(records)

    # ヴァイオリン図を描画（横軸がElement、縦軸がIllustrator）
    plt.figure(figsize=(10, 12))
    sns.violinplot(x="Element", y="Illustrator", data=df, inner="quartile", cut=0, scale="count")
    plt.title("Violin Plot of Mean resultant length distribution by Illustrator")
    plt.xlabel("Mean resultant length(0~12)")
    plt.ylabel("Illustrator")
    plt.tight_layout()

    output_file_path = f'src/color_recommendation/data/output/violin_from_mean_resultant_length.png'
    plt.savefig(output_file_path)
    print(f"{output_file_path} が保存されました．")


def save_plot_violin_from_used_hues_count_for_illustrators(illustrator_list):
    """
    引数で受け取るリスト内のイラストレーターの使用色相(有彩色)の数の分布をヴァイオリン図にプロットする関数

    引数:
        illustrator_list: 使用色を抽出させたいイラストレーターのリスト(文字列)

    戻り値:
        None
    """

    used_hues_counts_for_illustrators = {}

    # 各イラストレーターの使用色相(有彩色)の数の分布を取得
    for illustrator_name in illustrator_list:
        used_hues_count = _extract_used_hues_count_from_json(illustrator_name)
        print(f"=== {illustrator_name} ====================")
        print(f"used_hues_count = {used_hues_count}")
        used_hues_counts_for_illustrators[illustrator_name] = used_hues_count

    # データを「イラストレータ」「要素番号」の形に“出現回数ぶん”展開
    records = []
    for illustrator, counts in used_hues_counts_for_illustrators.items():
        for element_idx, count in enumerate(counts):
            # その要素が count 回出てくるとみなし，countぶんだけ同じ行を追加
            records.extend([{"Illustrator": illustrator, "Element": element_idx}] * count)

    df = pd.DataFrame(records)

    # ヴァイオリン図を描画（横軸がElement、縦軸がIllustrator）
    plt.figure(figsize=(10, 12))
    sns.violinplot(x="Element", y="Illustrator", data=df, inner="quartile", cut=0, scale="count")
    plt.title("Violin Plot of Used hues count by Illustrator")
    plt.xlabel("Used hues count")
    plt.ylabel("Illustrator")
    plt.tight_layout()

    output_file_path = f'src/color_recommendation/data/output/violin_from_used_hues_count.png'
    plt.savefig(output_file_path)
    print(f"{output_file_path} が保存されました．")


def _extract_used_pccs_count_sum_distribution_from_json():
    input_file_path = "src/color_recommendation/data/input/statistics_for_illustrators.json"

    with open(input_file_path, 'r') as f:
        data = json.load(f)
        print(f"{input_file_path} が読み込まれました．")

    used_pccs_count_sum_distributions_for_illustrators = {}

    # 各イラストレーターの使用色相(有彩色)の分布を取得
    for illustrator_data in data:
        illustrator_name = illustrator_data["illustrator_name"]
        used_pccs_count_sum_distribution = illustrator_data["used_pccs_count_sum_distribution"]

        print(f"=== {illustrator_name} ====================")
        print(f"used_pccs_count_sum_distribution = {used_pccs_count_sum_distribution}")
        used_pccs_count_sum_distributions_for_illustrators[illustrator_name] = used_pccs_count_sum_distribution

        # used_hues_counts_for_illustrators[illustrator_name] = used_hues_count

    return used_pccs_count_sum_distributions_for_illustrators


def save_plot_violin_from_used_pccs_distribution_for_illustrators():
    """
    イラストレーターの使用PCCS(1~24)の分布をヴァイオリン図にプロットする関数。
    横軸の背景に色相のグラデーションを表示する。
    """
    # ダミーデータまたは既存の関数からデータを取得
    used_pccs_count_sum_distributions_for_illustrators = _extract_used_pccs_count_sum_distribution_from_json()

    # データを「Illustrator」「Element」の形に展開
    records = []
    for illustrator, counts in used_pccs_count_sum_distributions_for_illustrators.items():
        for element_idx, count in enumerate(counts):
            records.extend([{"Illustrator": illustrator, "Element": element_idx}] * count)
    df = pd.DataFrame(records)

    # 図の準備
    fig, ax = plt.subplots(figsize=(10, 12))

    # 横軸に沿って 24 個の区間で色相360度のグラデーションを作成
    n_elements = 24
    colors = []
    for i in range(n_elements):
        hue = i * (360 / n_elements)         # 0〜360の範囲
        # colorsys.hls_to_rgb() は引数 (h, l, s) を受け取る（hは0～1に正規化）
        # CSSの HSL(hue, saturation, lightness) に対応させるため、lightness と saturation をそれぞれ設定
        rgb = colorsys.hls_to_rgb(hue / 360, 0.75, 1)  # lightness=0.75, saturation=1
        colors.append(rgb)

    # 各区間ごとに背景の縦帯を描画
    for i in range(n_elements):
        ax.axvspan((i + 1) - 0.5, (i + 1) + 0.5, color=colors[i], alpha=0.3, zorder=0)

    # ヴァイオリンプロットの描画
    sns.violinplot(x="Element", y="Illustrator", data=df, inner="quartile", cut=0, scale="count", ax=ax)

    ax.set_title("Violin Plot of Used PCCS count by Illustrator")
    ax.set_xlabel("Used PCCS (1~24)")
    ax.set_ylabel("Illustrator")

    plt.tight_layout()
    output_file_path = 'src/color_recommendation/data/output/violin_from_used_pccs_count.png'
    plt.savefig(output_file_path)
    print(f"{output_file_path} が保存されました．")


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
    # plot_recall_at_k("src/color_recommendation/data/output/test_is_contained_next_color_simple_data.json", 'src/color_recommendation/data/output/test_recall_at_k.png')
    pass


if __name__ == '__main__':
    main()
