from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000
from PIL import Image
import numpy as np
import math
from utils.helpers.transform_color import rgb_to_hsl, rgb_to_lab, hex_to_rgb

DEBUG = False


def calc_weighted_average_rgb(rgb_a, rgb_b, weight_a, weight_b):
    """
    2つのrbg値の加重平均を計算する関数

    引数:
        rgb_a (tuple): 最初のrgb値を表す整数のタプル (R, G, B)。
        rgb_b (tuple): 2番目のrgb値を表す整数のタプル (R, G, B)。
        weight_a (float): 最初のrgb値に対する重み (0から1の範囲)。
        weight_b (float): 2番目のrgb値に対する重み (0から1の範囲)。

    戻り値:
        tuple: 加重平均されたRGB値を表す整数のタプル (R, G, B)。
    """

    total_weight = weight_a + weight_b
    weight_a_normalized = weight_a / total_weight
    weight_b_normalized = weight_b / total_weight

    r = int(rgb_a[0] * weight_a_normalized + rgb_b[0] * weight_b_normalized)
    g = int(rgb_a[1] * weight_a_normalized + rgb_b[1] * weight_b_normalized)
    b = int(rgb_a[2] * weight_a_normalized + rgb_b[2] * weight_b_normalized)

    print_colored_text('■', rgb_a)
    print(f" × {round(weight_a_normalized*100000)/100000} + ", end="")
    print_colored_text('■', rgb_b)
    print(f" × {round(weight_b_normalized*100000)/100000} = ", end="")
    print_colored_text('■\n', (r, g, b))

    return (r, g, b)


def merge_similar_color_counts(color_counts, same_color_threshold):
    """引数で受け取った配色のうちΔE値が閾値以下の色を結合する関数"""
    merged_color_counts = []  # 結合する色を保存する配列を初期化

    # 配色がある限り色を結合
    while len(color_counts) > 0:
        base_color_count = color_counts[0]  # 先頭の色をベースカラーに代入
        to_merge = [base_color_count]
        color_counts = color_counts[1:]

        # 先頭の色と先頭以外の色でΔEが閾値以下の場合があるかどうかの探索
        for i in range(len(color_counts) - 1, -1, -1):  # 最後尾([len(~)-1])からから先頭([-1])まで検索

            # 先頭の色とi番目の色が同じ色だった場合
            if calculate_color_difference_delta_e_cie2000(base_color_count[0], color_counts[i][0]) <= same_color_threshold:
                to_merge.append(color_counts[i])  # 結合する色を保存するスロットにi番目の色を追加
                color_counts.pop(i)  # 結合されるi番目の色を削除

        # 色の加重平均と合算された出現回数を色を結合する配列に追加
        merge_color_total_count = sum([color[1] for color in to_merge])  # 出現回数の合算
        merge_color_rgb = np.average([color[0] for color in to_merge], axis=0, weights=[color[1] for color in to_merge])
        merge_color_rgb = np.round(merge_color_rgb).astype(int)
        merged_color_counts.append([merge_color_rgb, merge_color_total_count])
    return merged_color_counts


def calculate_dict_value_sum(dict):
    """引数で受け取った辞書型の配列のvalueの合計値を計算する関数"""
    sum = 0
    for key in dict:
        sum += dict[key]
    return sum


def calculate_rgb_distance_by_euclidean(rgb1, rgb2):
    """
    RGB形式の2つの色データ間の距離を計算し、最大値1で正規化した値を返す関数
    引数:
        rgb1: タプル (r, g, b)
        param rgb2: タプル (r, g, b)
    戻り値:
        distance / max_distance: 正規化されたユークリッド距離
    """
    r1, g1, b1 = rgb1
    r2, g2, b2 = rgb2
    max_distance = math.sqrt((255 ** 2) * 3)
    distance = math.sqrt((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2)
    return distance / max_distance


def transform_tuple_to_list(color_counts_tuple):
    """tuple型の色の数を保存するデータをlist型に変換する関数"""
    color_counts_list = []
    sum = calculate_dict_value_sum(color_counts_tuple)

    for key in color_counts_tuple:
        color_counts_list.append([key, (color_counts_tuple[key] / sum)])

    return color_counts_list


def update_color_counts(color_counts, color):
    """
    色の出現回数を更新する関数
    既存の色なら出現回数をインクリメントし、未登録の色なら追加して1で初期化する。

    Args:
        color_counts (dict): 色とその出現回数を管理する辞書
        color (tuple): 追加したい色 (R, G, B)

    Returns:
        None
    """
    if color in color_counts:
        color_counts[color] += 1  # 出現回数をインクリメント
    else:
        color_counts[color] = 1  # 新規色を1で初期化


def extract_used_color_count(image_path, quantize_threshold):
    """引数で受け取ったパスの画像の色とその出現回数を抽出する関数"""
    # 画像を読み込み
    image = Image.open(image_path)
    image = image.convert('RGB')  # RGBに変換
    pixels = list(image.getdata())  # 画像のピクセルデータを取得

    color_counts = {}
    for color_rgb in pixels:
        update_color_counts(color_counts, quantize_color_rgb(color_rgb, quantize_threshold))

    return color_counts


def quantize_color_rgb(rgb, threshold):
    """引数で受け取ったRGB値を量子化する関数"""
    return tuple((value // threshold) * threshold if value % threshold < 3 else (value // threshold) * threshold + threshold for value in rgb)


def calculate_color_difference_delta_e_cie2000(color1, color2):
    """二色間の色の差をΔEを用いて計算する関数
    引数:
        color1: 色1 (R, G, B)
        color2: 色2 (R, G, B)
    戻り値:
        delta_e: 色の差 (0-1)

    # メモ
    - この関数を実行するには/(venvディレクトリ)/lib64/python3.10/site-packages/colormath/color_diff.py内の関数delta_e_cie2000()
    の"return numpy.asscalar(delta_e)" を "return delta_e.item()" に変更する必要あり
        - 恐らくnumpyのバージョンと上手く嚙み合ってないのが原因
    """

    # RGBからLab色空間に変換
    color1_rgb = sRGBColor(*color1, is_upscaled=True)
    color2_rgb = sRGBColor(*color2, is_upscaled=True)

    color1_lab = convert_color(color1_rgb, LabColor)
    color2_lab = convert_color(color2_rgb, LabColor)

    # ΔE（CIE 2000）を計算
    delta_e = delta_e_cie2000(color1_lab, color2_lab)
    return float(delta_e)


def calc_color_scheme_difference_delta_e_cie2000(color_scheme1, color_scheme2):
    """配色間の色の差をΔEを用いて計算する関数

    引数:
        color_scheme1: 配色1 (リスト)
        color_scheme2: 配色2 (リスト)
    戻り値:
        delta_e: 色の差 (0-100)
    """

    min_delta_e_list = [101] * len(color_scheme1)
    compared_index = []

    for i in range(len(color_scheme1)):
        min_delta_e_index = 0
        for j in range(len(color_scheme2)):
            if j in compared_index:
                continue

            # ΔEを計算
            delta_e = calculate_color_difference_delta_e_cie2000(color_scheme1[i], color_scheme2[j])
            if delta_e < min_delta_e_list[i]:
                min_delta_e_list[i] = delta_e
                min_delta_e_index = j

            if (DEBUG):
                print(f"[{i}, {j}]: ", end="")
                print("ΔE( ", end="")
                print_colored_text("■", color_scheme1[i])
                print(" , ", end="")
                print_colored_text("■", color_scheme2[j])
                print(f" ) = {delta_e}")

        # print(f"min_delta_e_index = {min_delta_e_index}")
        compared_index.append(min_delta_e_index)

    min_delta_e_list = [x for x in min_delta_e_list if x != 101]

    # print(f"min_delta_e = {min_delta_e_list}")

    ave_delta_e = sum([x for x in min_delta_e_list]) / len(min_delta_e_list)
    # print(f"ave_delta_e = {ave_delta_e}")

    return ave_delta_e


# 引数で受け取ったRGB値の文字を表示させる関数
def print_colored_text(text, rgb):
    # RGBから16進数カラーコードに変換
    hex_color = '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])

    # ANSIエスケープシーケンスを使って色を設定
    print(f"\033[38;2;{rgb[0]};{rgb[1]};{rgb[2]}m{text}\033[0m", end="")


def print_used_color_and_rate(colors_data, print_threshold):
    """使用色とその比率を表示する関数

    引数:
        colors_data: 色とその出現率を保存するデータ
        print_threshold: 表示する出現率の閾値(0-1)
    """
    for color_data in colors_data:
        # print(color_data)
        color_rgb = hex_to_rgb(color_data['color'])
        color_hsl = rgb_to_hsl(color_rgb)
        print_colored_text("■", color_rgb)
        print(f": {round(color_data['rate'] * 10000)/ 100} % ", end="")
        print(f" hsl = {color_hsl}")

# 引数で受け取った配色を表示させる関数


def print_color_scheme(color_scheme):
    for color in color_scheme:
        print_colored_text("■", color)

    print("")


# 引数で受け取った配色群を表示させる関数
def print_color_schemes(color_schemes):
    for color_scheme in color_schemes:
        print_color_scheme(color_scheme)


def test_delta_e_cie2000(color1, color2):
    """ΔEを用いて色の差を計算する関数のテスト"""
    # 色の差を計算
    color_diff = calculate_color_difference_delta_e_cie2000(color1, color2)
    print_colored_text('■', color1)
    print(" と ", end="")
    print_colored_text('■', color2)
    print(f" の色差 = {color_diff}")


def test_color_diff(file_path):
    colors = []
    with open(file_path, 'r') as file:
        for line in file:
            colors.append(tuple(map(int, line.strip().split(','))))

    for i in range(len(colors)):
        print(colors[i])
        for j in range(i + 1, len(colors)):
            test_delta_e_cie2000(colors[i], colors[j])


def is_chromatic_color_by_hsl(color_rgb, SATURATION_THRESHOLD, LIGHTNESS_LOWER_THRESHOLD, LIGHTNESS_UPPER_THRESHOLD):
    """受け取った色が有彩色かどうかをHSL空間を使って判定する関数
    """

    color_hsl = rgb_to_hsl(color_rgb)
    saturation = color_hsl[1]
    lightness = color_hsl[2]

    if (DEBUG):
        print_colored_text("\n■", color_rgb)
        print(f" hsl = {color_hsl}, rgb = {color_rgb}")

    if (saturation <= SATURATION_THRESHOLD):
        return False
    elif (lightness <= LIGHTNESS_LOWER_THRESHOLD or LIGHTNESS_UPPER_THRESHOLD <= lightness):
        return False
    else:
        return True


def is_chromatic_color_by_lab(color_rgb):
    """受け取った色が有彩色かどうかをHSL空間を使って判定する関数
    """

    color_hsl = rgb_to_hsl(color_rgb)
    color_lab = rgb_to_lab(color_rgb)

    if (DEBUG):
        print_colored_text("■ ", color_rgb)
        # print(f" lab = {color_lab}, hsl = {color_hsl}, rgb = {color_rgb}")

    if (color_lab[0] <= 10 or 90 <= color_lab[0]):
        return False

    else:
        return True


def calc_angle_diff(angle1, angle2):
    """角度の差(0°~180°)を計算する関数
    """
    diff = abs(angle1 - angle2)
    return diff if diff <= 180 else 360 - diff


def calc_mean_angle(degrees):
    """
    平均角度を計算する関数

    Args:
        degrees: 角度のリスト

    Returns:
        mean_degree : 角度の平均値
    """
    # ラジアンに変換
    radians = np.radians(degrees)
    # 各角度の単位ベクトルを計算
    sin_sum = np.sum(np.sin(radians))
    cos_sum = np.sum(np.cos(radians))
    # 平均ベクトルの角度を計算
    mean_radian = np.arctan2(sin_sum, cos_sum)
    # ラジアンを度に変換し、0-360度の範囲に調整
    mean_degree = np.degrees(mean_radian) % 360
    return mean_degree


def calc_closest_angle(angles, target):
    """
    angles: 度単位の角度のリスト
    target: ターゲット角度。2π未満ならラジアンとみなし度に変換する。
    ターゲットに最も近い角度（度単位）を返す。
    """
    # ターゲットが2π未満の場合、ラジアンとみなして度に変換
    if target < 2 * math.pi:
        target = math.degrees(target)

    best = None
    min_diff = 360  # 初期値は最大の360度
    for angle in angles:
        # 循環する角度の差を計算（0〜180の最小差）
        diff = abs(angle - target) % 360
        if diff > 180:
            diff = 360 - diff
        if diff < min_diff:
            min_diff = diff
            best = angle
    return best


def bring_element_to_front(list, target):
    """ ターゲットを先頭に持ってくる関数
    """
    # リストに対象の要素が存在するか確認
    if target in list:
        list.remove(target)    # まずリストから削除
        list.insert(0, target)  # 先頭に挿入
    return list


if __name__ == "__main__":
    print("=== color_utils.py =====================")
