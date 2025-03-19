import json
from utils.helpers.color_utils import print_colored_text, is_chromatic_color_by_hsl, print_used_color_and_rate
from utils.helpers.transform_color import hex_to_rgb, rgb_to_hsl, hsl_to_rgb
import numpy as np

DEBUG = False
# (有彩色判定の閾値を緩く設定しすぎると白や肌色が有彩色として判定されてしまう)
SATURATION_THRESHOLD, LIGHTNESS_LOWER_THRESHOLD, LIGHTNESS_UPPER_THRESHOLD = 20, 20, 80  # これが暫定値(2025/03/19)
PRINT_THRESHOLD = 0


def merge_hue_data(data, threshold):
    """
    近い色相同士の加重平均を取って結合する関数（ベクトル加重平均版）

    引数:
    data: List[Tuple[int, float]] - (色相H, 重みW) のリスト
    threshold: int - 近いとみなす色相の閾値

    戻り値: 
    List[Tuple[int, float]] - (統合後の色相H, 重みW) のリスト
    """
    merged = []
    used = set()

    for i, (h1, w1) in enumerate(data):
        if i in used:
            continue
        group = [(h1, w1)]
        used.add(i)

        for j, (h2, w2) in enumerate(data):
            if j in used:
                continue
            # 360度環境を考慮して距離を計算
            if min(abs(h1 - h2), 360 - abs(h1 - h2)) <= threshold:
                group.append((h2, w2))
                used.add(j)

        # ベクトル加重平均で代表Hueを決定
        total_weight = sum(w for _, w in group)
        x_sum = sum(np.cos(np.deg2rad(h)) * w for h, w in group)
        y_sum = sum(np.sin(np.deg2rad(h)) * w for h, w in group)

        if total_weight == 0:
            avg_hue = 0  # すべての重みが0ならデフォルト値
        else:
            avg_hue = np.rad2deg(np.arctan2(y_sum, x_sum))
            if avg_hue < 0:
                avg_hue += 360  # 負の値を補正

        merged.append((round(avg_hue), total_weight))

    return merged


def delete_hue_data_low_rate(data, threshold):
    """
    出現率が一定以下の色相データを削除する関数
    """
    return [(h, w) for h, w in data if w >= threshold]


def print_chromatic_colors_rate(data, threshold):
    """
    有彩色の使用割合を表示させる関数

    引数: 
        data:
        threshold: float - 表示させる使用比率の閾値
    戻り値:
        none
    """
    for hue_data in data:
        if (threshold < hue_data[1]):
            print_colored_text("■", hsl_to_rgb((hue_data[0]) % 360, 100, 50))
            print(f" {hue_data[0]}: {round(hue_data[1]*10000)/100}%")


def print_achromatic_colors_rate(data, threshold):
    """
    無彩色の使用割合を表示させる関数

    引数: 
        data:
        threshold: float - 表示させる使用比率の閾値
    戻り値:
        none
    """
    if (threshold < data[0][1]):
        print_colored_text("■", (10, 10, 10))
        print(f" -: {round(data[0][1]*10000)/100}%")
    if (threshold < data[1][1]):
        print_colored_text("■", (255, 255, 255))
        print(f" -: {round(data[1][1]*10000)/100}%")


def count_chromatic_colors(hues_data, threshold):
    """引数で受け取る使用配色のうち，有彩色の数をカウントする関数"""
    chromatic_count = 0
    for hue_data in hues_data:
        if (hue_data[0] > 0 and threshold < hue_data[1]):
            chromatic_count += 1
    return chromatic_count


def count_achromatic_colors(hues_data, threshold):
    """引数で受け取る使用配色のうち，無彩色の彩色の数をカウントする関数"""
    achromatic_count = 0
    for hue_data in hues_data:
        if (hue_data[0] == -10 and threshold < hue_data[1]):
            achromatic_count += 1
        elif (hue_data[0] == -11 and threshold < hue_data[1]):
            achromatic_count += 1
    return achromatic_count


def estimate_used_color_method(used_hues_data):
    """引数で受け取る使用配色のデータを基に配色技法を推定する関数"""
    chromatic_colors_count = count_chromatic_colors(used_hues_data, 0.01)
    achromatic_colors_count = count_achromatic_colors(used_hues_data, 0.01)

    if (DEBUG):
        print(f"count_chromatic_colors = {chromatic_colors_count}")
        print(f"achromatic_colors = {achromatic_colors_count}")

    """
    # 色の数が1色だった場合
    if (len(used_colors) == 1):
        used_color_scheme_method = ColorScheme.IDENTITY_COLOR

    # 色の数が2色だった場合
    elif (len(used_colors) == 2):
        if (hue_diffs[1] >= 165):
            used_color_scheme_method = ColorScheme.DYAD_COLOR
        elif (is_angle_between_angles(hue_diffs[1], 75, 105)):
            # elif ((75 <= hue_diffs[1]) & (hue_diffs[1] <= 105)):
            used_color_scheme_method = ColorScheme.INTERMEDIATE_COLOR
        elif (is_angle_between_angles(hue_diffs[1], 105, 165)):
            used_color_scheme_method = ColorScheme.OPONENT_COLOR
        elif (is_angle_between_angles(hue_diffs[1], 15, 45)):
            used_color_scheme_method = ColorScheme.ANALOGY_COLOR

    # 色の数が3色だった場合
    elif (len(used_colors) == 3):
        if ((hue_diffs[1] <= 30) & (hue_diffs[2] <= 60)):
            used_color_scheme_method = ColorScheme.DOMINANT_COLOR
        elif (((120 <= hue_diffs[1]) & (hue_diffs[1] <= 150)) & ((120 <= hue_diffs[2]) & (hue_diffs[2] <= 150))):
            used_color_scheme_method = ColorScheme.TRIAD_COLOR_SCHEME
        elif ((hue_diffs[1] >= 150) & (hue_diffs[2] >= 150)):
            used_color_scheme_method = ColorScheme.SPLIT_COMPLEMENTARY_COLOR
        elif (is_angle_between_angles(hue_diffs[1], 15, 60) & is_angle_between_angles(hue_diffs[2], 135, 165)):
            # elif ((hue_diffs[1] <= 45) & (hue_diffs[2] >= 150)):
            used_color_scheme_method = ColorScheme.SPLIT_COMPLEMENTARY_COLOR
        elif (is_angle_between_angles(hue_diffs[2], 15, 60) & is_angle_between_angles(hue_diffs[1], 135, 165)):
            # elif ((hue_diffs[1] >= 150) & (hue_diffs[2] <= 45)):
            used_color_scheme_method = ColorScheme.SPLIT_COMPLEMENTARY_COLOR

    # 色の数が3色だった場合
    elif (len(used_colors) == 4):
        if (is_angle_between_angles(hue_diffs[1], 75, 105) & is_angle_between_angles(hue_diffs[2], 75, 105) & (hue_diffs[3] >= 165)):
            used_color_scheme_method = ColorScheme.TETRADE_COLOR
    elif (len(used_colors) == 5):
        used_color_scheme_method = ColorScheme.PENTAD_COLOR
    elif (len(used_colors) == 6):
        used_color_scheme_method = ColorScheme.HEXAD_COLOR
    else:
        used_color_scheme_method = ColorScheme.ERROR

    print(f"推定された配色技法は {used_color_scheme_method} です．")
    """


def estimate_used_color_method_by_illustrator(illustrator):
    """あるイラストレーターが使っている配色技法を推定する関数
    """
    print(f"=== {illustrator} =======================")

    with open(f"src/color_recommendation/data/input/used_colors/used_colors_{illustrator}.json", "r") as f:
        data = json.load(f)

    for illust_data in data:
        illust_name = illust_data[0]['illustName']
        print(f"=== {illust_name} ===")

        if (DEBUG):
            # print(illust_data)
            print_used_color_and_rate(illust_data, PRINT_THRESHOLD)

            print("\n=== ↓ === (↑ 基となる使用色とその比率, ↓ 抽出された色相(有彩色のみ)とその比率)")

        # 色相とその出現割合の計測
        chromatic_colors_rate = []  # 有彩色の色相とその出現割合を保存する変数
        achromatic_colors_rate = [[-10, 0], [-11, 0]]  # 無彩色とその出現割合を保存する変数

        for color_data in illust_data:
            color_hex = color_data['color']
            color_rgb = hex_to_rgb(color_hex)
            color_hsl = rgb_to_hsl(color_rgb)
            used_rate = color_data['rate']

            # 使用比率の追加(有彩色と無彩色を分けて保存)
            # 有彩色の場合
            if (is_chromatic_color_by_hsl(color_rgb, SATURATION_THRESHOLD, LIGHTNESS_LOWER_THRESHOLD, LIGHTNESS_UPPER_THRESHOLD)):
                chromatic_colors_rate.append([color_hsl[0], used_rate])
            # 無彩色の場合
            else:
                # 黒色の使用比率の追加
                if (color_hsl[2] <= 50):
                    # print_colored_text("■", color_rgb)
                    # print(f": {used_rate}")
                    achromatic_colors_rate[0][1] += used_rate
                # 白色の使用比率の追加
                else:
                    # print_colored_text("■", color_rgb)
                    # print(f": {used_rate}")
                    achromatic_colors_rate[1][1] += used_rate
        # 確認用出力1
        if (DEBUG):

            print_chromatic_colors_rate(chromatic_colors_rate, PRINT_THRESHOLD)
            print("\n=== ↓ === ( ↓ 色相が近いデータ同士で加重平均を取って結合)")

        # 色相が近いデータ同士で加重平均を取って結合
        chromatic_colors_rate = merge_hue_data(chromatic_colors_rate, 15)

        """
        # データの時点では出現率を削除せずに表示させるときに変更する方針に変更(2025/03/13)に
        if (DEBUG):
            print_chromatic_colors_rate(chromatic_colors_rate, 0.01)
            print("=== ↓ === ")

        # 出現率が一定以下の色相データを削除
        chromatic_colors_rate = delete_hue_data_low_rate(chromatic_colors_rate, 0.01)
        """

        # 確認用出力2
        print_chromatic_colors_rate(chromatic_colors_rate, PRINT_THRESHOLD)
        print_achromatic_colors_rate(achromatic_colors_rate, PRINT_THRESHOLD)

        used_hues_rate = []
        for chromatic_color_rate in chromatic_colors_rate:
            used_hues_rate.append(chromatic_color_rate)
        for achromatic_color_rate in achromatic_colors_rate:
            used_hues_rate.append((achromatic_color_rate[0], achromatic_color_rate[1]))
        # print(f"used_hues_rate = {used_hues_rate}")

        # 使用配色技法の推定
        estimate_used_color_method(used_hues_rate)


def save_estimate_used_color_method_for_illustrators(illutrater_list):
    """
    引数で受け取るリスト内のイラストレーターのイラストの配色技法を保存する関数

    引数:
        illutrater_list: 推薦配色を生成させたいイラストレーターのリスト(文字列)
    戻り値:
        None
    """

    print("*** 使用色相の抽出 ************")
    for illustrater_name in illutrater_list:
        estimate_used_color_method_by_illustrator(illustrater_name)


if __name__ == '__main__':
    pass
    # estimate_used_color_scheme('test')
