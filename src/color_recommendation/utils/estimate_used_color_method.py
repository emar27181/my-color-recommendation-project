import json
from utils.helpers.color_utils import print_colored_text, is_chromatic_color_by_hsl
from utils.helpers.transform_color import hex_to_rgb, rgb_to_hsl, hsl_to_rgb
import numpy as np

DEBUG = False


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


def print_chromatic_colors_rate(hues):
    for hue_data in hues:
        print_colored_text("■", hsl_to_rgb((hue_data[0]) % 360, 100, 50))
        print(f" {hue_data[0]}: {round(hue_data[1]*100)/100}")


def estimate_used_color_method_by_illustrator(illustrator):
    """あるイラストレーターが使っている配色技法を推定する関数
    """
    print(f"=== {illustrator} =======================")

    with open(f"src/color_recommendation/data/input/used_colors/used_colors_{illustrator}.json", "r") as f:
        data = json.load(f)

    for illust_data in data:
        illust_name = illust_data[0]['illustName']
        print(f"=== {illust_name} ===")

        # 色相とその出現割合の計測
        chromatic_colors_rate = []  # 有彩色の色相とその出現割合を保存する変数
        achromatic_colors_rate = [[-10, 0], [-11, 0]]  # 無彩色とその出現割合を保存する変数

        for color_data in illust_data:
            color_hex = color_data['color']
            color_rgb = hex_to_rgb(color_hex)
            color_hsl = rgb_to_hsl(color_rgb)
            used_rate = color_data['rate']

            # 使用比率の追加(有彩色と無彩色を分けて保存)
            if (is_chromatic_color_by_hsl(color_rgb, 5, 5, 95)):
                chromatic_colors_rate.append([color_hsl[0], used_rate])
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

        if (DEBUG):
            print_chromatic_colors_rate(chromatic_colors_rate)
            print("=== ↓ ===")

        # 色相が近いデータ同士で加重平均を取って結合
        chromatic_colors_rate = merge_hue_data(chromatic_colors_rate, 15)
        if (DEBUG):
            print_chromatic_colors_rate(chromatic_colors_rate)
            print("=== ↓ ===")

        # 出現率が一定以下の色相データを削除
        chromatic_colors_rate = delete_hue_data_low_rate(chromatic_colors_rate, 0.01)

        # 確認用出力
        print_chromatic_colors_rate(chromatic_colors_rate)


def save_estimate_used_color_method_for_illustrators(illutrater_list):
    """
    引数で受け取るリスト内のイラストレーターのイラストの配色技法を保存する関数

    引数:
        illutrater_list: 推薦配色を生成させたいイラストレーターのリスト(文字列)
    戻り値:
        None
    """

    for illustrater_name in illutrater_list:
        estimate_used_color_method_by_illustrator(illustrater_name)


if __name__ == '__main__':
    pass
    # estimate_used_color_scheme('test')
