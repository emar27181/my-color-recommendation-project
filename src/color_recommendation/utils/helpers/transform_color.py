import numpy as np
from skimage.color import rgb2lab


def _calc_angle_diff(angle1, angle2):
    """角度の差(0°~180°)を計算する関数
    """
    diff = abs(angle1 - angle2)
    return diff if diff <= 180 else 360 - diff


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    rgb = tuple(max(0, min(255, x)) for x in rgb)
    return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])


def rgb_to_hsl(rgb):
    r = rgb[0] / 255.0
    g = rgb[1] / 255.0
    b = rgb[2] / 255.0

    max_val = max(r, g, b)
    min_val = min(r, g, b)
    l = (max_val + min_val) / 2

    if max_val == min_val:
        h = s = 0  # achromatic
    else:
        d = max_val - min_val
        s = d / (2.0 - max_val - min_val) if l > 0.5 else d / (max_val + min_val)

        if max_val == r:
            h = (g - b) / d + (6 if g < b else 0)
        elif max_val == g:
            h = (b - r) / d + 2
        else:
            h = (r - g) / d + 4
        h /= 6

    return int(h * 360), int(s * 100), int(l * 100)


def hsl_to_rgb(h, s, l):
    s /= 100
    l /= 100

    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = l - c / 2

    if 0 <= h < 60:
        r, g, b = c, x, 0
    elif 60 <= h < 120:
        r, g, b = x, c, 0
    elif 120 <= h < 180:
        r, g, b = 0, c, x
    elif 180 <= h < 240:
        r, g, b = 0, x, c
    elif 240 <= h < 300:
        r, g, b = x, 0, c
    elif 300 <= h < 360:
        r, g, b = c, 0, x
    else:
        r, g, b = 0, 0, 0

    r = (r + m) * 255
    g = (g + m) * 255
    b = (b + m) * 255

    return [int(r), int(g), int(b)]


def rgb_to_lab(rgb):
    r, g, b = rgb[0], rgb[1], rgb[2]

    # RGB値を0〜1の範囲に正規化
    rgb = np.array([[[r / 255, g / 255, b / 255]]])

    # RGBからLabに変換
    lab = rgb2lab(rgb)

    # L, a, b を通常の float に変換して返す
    return float(lab[0, 0, 0]), float(lab[0, 0, 1]), float(lab[0, 0, 2])


def transform_color_scheme_rgb_to_hex(color_scheme_rgb):
    color_scheme_hex = []
    # print(color_scheme_rgb)

    for color_rgb in color_scheme_rgb:
        color_scheme_hex.append(rgb_to_hex(color_rgb))
    return color_scheme_hex


def transform_color_schemes_rgb_to_hex(color_schemes_rgb):
    color_schemes_hex = []
    for color_scheme_rgb in color_schemes_rgb:
        # print("color_scheme_rgb: ", color_scheme_rgb)
        color_schemes_hex.append(transform_color_scheme_rgb_to_hex(color_scheme_rgb))
    return color_schemes_hex


def transform_hues_to_pccs(hues):
    pccs = []
    for hue in hues:
        pccs.append(hue_to_pccs(hue))
    pccs.sort()
    return pccs


def hue_to_pccs(hue_angle):
    """
    HSLの色相角度（0°〜360°）をPCCSの色相番号（1〜24）に変換する関数
    ※PCCSの黄色は8だが，この関数では5になってしまっている(2025/04/02)

    引数:
        hue_angle (float): HSLの色相角度（0°〜360°）

    戻り値:
        pccs_number (int): PCCSの色相番号（1〜24）

    """
    # HSLの色相角度をPCCSの色相番号にマッピング
    pccs_number = round((hue_angle / 360) * 24) + 1

    if (pccs_number > 24):
        pccs_number = 1

    return pccs_number


def _is_angle_between_angles(angle, angle_start, angle_end):
    """ ある角度同士の間にあるかどうかを判定する関数
    """
    return ((angle_start <= angle) & (angle <= angle_end))


def hue_diffs_to_color_method(hue_diffs):
    """ 色相差から配色方法を推定する関数
    ※現時点では推定された配色技法をコンソールに出力するだけ(2025/04/02)

    引数:
        hue_diffs (list): 色相差のリスト

    戻り値:
        None: なし
    """

    print("推定結果 => ", end="")
    if (len(hue_diffs) == 0):
        print("0色相: モノクロ配色")

    # 色相の数が1色だった場合
    elif (len(hue_diffs) == 1):
        print("1色相: アイデンティティ配色")

    # 色相の数が2色だった場合
    elif (len(hue_diffs) == 2):
        if (hue_diffs[1] >= 165):
            # used_color_scheme_method ColorScheme.DYAD_COLOR
            print("2色相: ダイアード配色")
        elif (_is_angle_between_angles(hue_diffs[1], 75, 105)):
            print("2色相: インターミディエート配色")
        elif (_is_angle_between_angles(hue_diffs[1], 105, 165)):
            print("2色相: オポーネント配色")
        elif (_is_angle_between_angles(hue_diffs[1], 15, 45)):
            print("2色相: アナロジー配色")
        else:
            print("2色相: エラー")

    # 色相の数が3色だった場合
    elif (len(hue_diffs) == 3):
        if ((hue_diffs[1] <= 30) & (hue_diffs[2] <= 60)):
            print("3色相: ドミナント配色")
        elif (((120 <= hue_diffs[1]) & (hue_diffs[1] <= 150)) & ((120 <= hue_diffs[2]) & (hue_diffs[2] <= 150))):
            print("3色相: トライアド配色")
        elif ((hue_diffs[1] >= 150) & (hue_diffs[2] >= 150)):
            print("3色相: スプリットコンプリメンタリー配色")
        elif (_is_angle_between_angles(hue_diffs[1], 15, 60) & _is_angle_between_angles(hue_diffs[2], 135, 165)):
            print("3色相: スプリットコンプリメンタリー配色")
        elif (_is_angle_between_angles(hue_diffs[2], 15, 60) & _is_angle_between_angles(hue_diffs[1], 135, 165)):
            print("3色相: スプリットコンプリメンタリー配色")
        else:
            print("3色相: エラー")

    # 色相の数が4色だった場合
    elif (len(hue_diffs) == 4):
        if (_is_angle_between_angles(hue_diffs[1], 75, 105) & _is_angle_between_angles(hue_diffs[2], 75, 105) & (hue_diffs[3] >= 165)):
            print("4色相: テトラード配色")
        else:
            print("4色相: エラー")

    # 色相の数が5色だった場合
    elif (len(hue_diffs) == 5):
        print("5色相: ペンタード配色")

    # 色相の数が6色だった場合
    elif (len(hue_diffs) == 6):
        print("6色相: ヘキサード配色")

    # 色相の数が7色だった場合
    else:
        print("7色相以上: エラー")


def chromatic_hues_to_hue_diffs(chromatic_hues):
    """
    有彩色の色相のリストから色相差のリストを生成する関数
    """

    hue_diffs = []

    # 色相差の計算
    for i in range(0, len(chromatic_hues)):
        hue_diff = _calc_angle_diff(chromatic_hues[0], chromatic_hues[i])
        hue_diffs.append(hue_diff)

    hue_diffs.sort()

    return hue_diffs


def main():
    """
      print(rgb_to_hex((255, 0, 0)))
      print(hex_to_rgb("#FF0000"))
      print(rgb_to_hsl((255, 0, 0)))
      print(hsl_to_rgb(0, 100, 50))
      """


if __name__ == "__main__":
    main()
