from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000
from PIL import Image
import numpy as np


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
