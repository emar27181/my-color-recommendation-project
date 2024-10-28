from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000


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
