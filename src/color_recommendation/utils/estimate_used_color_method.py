import json
from utils.helpers.color_utils import print_colored_text, is_chromatic_color_by_hsl, print_used_color_and_rate, calc_angle_diff, calc_mean_angle, calc_closest_angle, bring_element_to_front
from utils.helpers.transform_color import hex_to_rgb, rgb_to_hsl, hsl_to_rgb, transform_hues_to_pccs, hue_diffs_to_color_method, chromatic_hues_to_hue_diffs
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


def extract_used_chromatic_hues(used_hues_data, used_rate_threshold):
    """ 使用された色相のデータのうち有彩色のみを抽出し，その角度を保存するリストを返す関数

    引数:
        used_hues_data:  使用された色相と使用比率のリスト(白黒を含む)
        used_rate_threshold: 使用されたと判定する閾値(0-1)

    戻り値:
        used_chromatic_hues:  使用された有彩色の色相のリスト
    """

    used_chromatic_hues = []
    for hue_data in used_hues_data:
        if (hue_data[0] >= 0 and hue_data[1] > used_rate_threshold):
            used_chromatic_hues.append(hue_data[0])
            # print(hue_data[0])

    used_chromatic_hues.sort()

    return used_chromatic_hues


def estimate_used_color_method(used_hues_data):
    """引数で受け取る使用配色のデータを基に配色技法を推定する関数

    引数: 
        used_hues_data: 使用された色相と使用比率のリスト(白黒を含む)

    戻り値:
        chromatic_colors_count: 使用された有彩色の数
        achromatic_colors_count: 使用された無彩色の数
        used_chromatic_hues: 使用された有彩色の色相(0~360)のリスト
        used_pccs: 使用されたPCCS色相(1~24)のリスト
        hue_diffs: 色相差(0~180)のリスト
    """

    USED_RATE_THRESHOLD = 0.01

    # 使用された色相の数のカウント
    chromatic_colors_count = count_chromatic_colors(used_hues_data, USED_RATE_THRESHOLD)
    achromatic_colors_count = count_achromatic_colors(used_hues_data, USED_RATE_THRESHOLD)
    if (DEBUG):
        print(f"count_chromatic_colors = {chromatic_colors_count}")
        print(f"achromatic_colors = {achromatic_colors_count}")

    # 使用された色相(0~360)の抽出
    used_chromatic_hues = extract_used_chromatic_hues(used_hues_data, USED_RATE_THRESHOLD)
    mean_hue = calc_mean_angle(used_chromatic_hues)  # 使用色相の平均
    opposite_mean_hue = (mean_hue + 180) % 360  # 平均色相の反対側の色相
    used_chromatic_hues = bring_element_to_front(used_chromatic_hues, calc_closest_angle(used_chromatic_hues, opposite_mean_hue))  # 平均色相の反対側の色相をリストの先頭に移動

    # 使用されたPCCS色相(1~24)の抽出
    used_pccs = transform_hues_to_pccs(used_chromatic_hues)

    # 色相差(0~12)の抽出
    hue_diffs = chromatic_hues_to_hue_diffs(used_chromatic_hues)

    # 確認用出力
    print(f"used_chromatic_hues = {used_chromatic_hues} (使用率1％以上のみ)")
    print(f"used_pccs = {used_pccs}")
    print(f"hue_diffs: {hue_diffs}")
    hue_diffs_to_color_method(hue_diffs)  # ←現在はコンソール表示のみ

    return chromatic_colors_count, achromatic_colors_count, used_chromatic_hues, used_pccs, hue_diffs


def estimate_used_hue(illust_data):
    """
    引数で受け取るイラストデータを基に使用色相を推定する関数

    引数: 
        illust_data: 使用色のデータ(色と使用比率のリスト)

    戻り値:
        used_hues_rate: 使用色相とその使用比率のリスト
    """

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

    # 色相(有彩色)が近いデータ同士で加重平均を取って結合
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

    # 使用色相を無彩色もまとめて保存
    used_hues_rate = []
    # 有彩色の保存
    for chromatic_color_rate in chromatic_colors_rate:
        used_hues_rate.append(chromatic_color_rate)
    # 無彩色の保存
    for achromatic_color_rate in achromatic_colors_rate:
        used_hues_rate.append((achromatic_color_rate[0], achromatic_color_rate[1]))

    return used_hues_rate


def estimate_used_color_method_by_illustrator(illustrator):
    """あるイラストレーターが使っている配色技法を推定する関数
    """
    print(f"=== {illustrator} =======================")

    with open(f"src/color_recommendation/data/input/used_colors/used_colors_{illustrator}.json", "r") as f:
        data = json.load(f)

    used_hues_data_by_illustrator = []

    for illust_data in data:
        illust_name = illust_data[0]['illustName']
        print(f"\n=== {illust_name} ===")
        print("*** 使用色相の抽出 ************")
        used_hues_rate = estimate_used_hue(illust_data)

        # 使用配色技法の推定
        print("*** 使用配色技法の推定 ************")
        chromatic_colors_count, achromatic_colors_count, used_chromatic_hues, used_pccs, hue_diffs = estimate_used_color_method(used_hues_rate)

        if (DEBUG):
            print("___ debug _________")
            print(f"used_hues_rate = {used_hues_rate}")
            print(f"chromatic_colors_count = {chromatic_colors_count}")
            print(f"achromatic_colors_count = {achromatic_colors_count}")
            print(f"used_chromatic_hues = {used_chromatic_hues}")
            print(f"used_pccs = {used_pccs}")
            print(f"hue_diffs = {hue_diffs}")

        used_hue_data_by_illust = {
            "illust_name": illust_name,
            "comment": "used_hues_rateにおいて, -10: black, -11: white. 有彩色の使用比率の閾値は1%(0.01)に設定．",
            "used_hues_rate": used_hues_rate,
            "chromatic_colors_count": chromatic_colors_count,
            "achromatic_colors_count": achromatic_colors_count,
            "used_chromatic_hues": used_chromatic_hues,
            "used_pccs": used_pccs,
            "hue_diffs": hue_diffs
        }

        used_hues_data_by_illustrator.append(used_hue_data_by_illust)

    return used_hues_data_by_illustrator


def save_estimate_used_color_method_for_illustrators(illutrater_list):
    """
    引数で受け取るリスト内のイラストレーターのイラストの配色技法を保存する関数

    引数:
        illutrater_list: 推薦配色を生成させたいイラストレーターのリスト(文字列)
    戻り値:
        None
    """

    for illustrater_name in illutrater_list:
        used_hues_data_by_illustrator = estimate_used_color_method_by_illustrator(illustrater_name)

        print(f"=== {illustrater_name} の使用色相の抽出が完了しました．")
        # print(f"used_hues_data_by_illustrator = {used_hues_data_by_illustrator}")

        output_file_path = f"src/color_recommendation/data/input/used_hues/used_hues_{illustrater_name}.json"

        with open(output_file_path, "w", encoding="utf-8") as f:
            # json.dump(used_hues_data_by_illustrator, f, ensure_ascii=False, indent=4)
            json.dump(used_hues_data_by_illustrator, f, ensure_ascii=False, indent=4,)
            print(f"{output_file_path} が保存されました．")


if __name__ == '__main__':
    pass
    # estimate_used_color_scheme('test')
