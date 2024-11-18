from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000
from PIL import Image
import numpy as np


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
        print(dict[key])
    return sum


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


# 色の差をΔEを用いて計算する関数
def calculate_color_difference_delta_e_cie2000(color1, color2):
    """ 
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


# 引数で受け取ったRGB値の文字を表示させる関数
def print_colored_text(text, rgb):
    # RGBから16進数カラーコードに変換
    hex_color = '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])

    # ANSIエスケープシーケンスを使って色を設定
    print(f"\033[38;2;{rgb[0]};{rgb[1]};{rgb[2]}m{text}\033[0m", end="")


# 引数で受け取った配色を表示させる関数
def print_color_scheme(color_scheme):
    for color in color_scheme:
        print_colored_text("■", color)

    print("")


# 引数で受け取った配色群を表示させる関数
def print_color_schemes(color_schemes):
    for color_scheme_method in color_schemes:
        for color_scheme in color_scheme_method:
            print_color_scheme(color_scheme)
