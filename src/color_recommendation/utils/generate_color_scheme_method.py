from .helpers.transform_color import rgb_to_hsl, hsl_to_rgb, rgb_to_hex, hex_to_rgb
from .helpers.color_utils import print_colored_text, print_color_schemes, print_color_scheme, is_exist_same_color

DEBUG = False


def generate_all_color_schemes(base_color_rgb):
    color_schemes_by_color_scheme_methods = []

    color_schemes_by_color_scheme_methods.append(generate_identity_color_scheme(base_color_rgb))

    color_schemes_by_color_scheme_methods.append(generate_intermediate_color_scheme(base_color_rgb))

    color_schemes_by_color_scheme_methods.append(generate_dyad_color_scheme(base_color_rgb))
    color_schemes_by_color_scheme_methods.append(generate_analogy_color_scheme(base_color_rgb))
    color_schemes_by_color_scheme_methods.append(generate_oponent_color_scheme(base_color_rgb))

    color_schemes_by_color_scheme_methods.append(generate_dominant_color_scheme(base_color_rgb))
    color_schemes_by_color_scheme_methods.append(generate_split_complementary_color_scheme(base_color_rgb))
    color_schemes_by_color_scheme_methods.append(generate_triad_color_scheme(base_color_rgb))

    color_schemes_by_color_scheme_methods.append(generate_tetrad_color_scheme(base_color_rgb))

    color_schemes_by_color_scheme_methods.append(generate_pentad_color_scheme(base_color_rgb))

    color_schemes_by_color_scheme_methods.append(generate_hexad_color_scheme(base_color_rgb))

    color_schemes = []
    # 配色技法ごとの配色群を取り出してcolor_schemesに追加(ドミナントカラー配色などは一つの配色技法に対して複数の配色を生成するため)
    for color_schemes_per_color_scheme_method in color_schemes_by_color_scheme_methods:
        for color_scheme in color_schemes_per_color_scheme_method:
            color_schemes.append(color_scheme)

    return color_schemes


def generate_one_color_schemes(base_color_rgb):
    color_schemes_by_color_scheme_methods = []

    color_schemes_by_color_scheme_methods.append(generate_identity_color_scheme(base_color_rgb))

    color_schemes = []
    # 配色技法ごとの配色群を取り出してcolor_schemesに追加(ドミナントカラー配色などは一つの配色技法に対して複数の配色を生成するため)
    for color_schemes_per_color_scheme_method in color_schemes_by_color_scheme_methods:
        for color_scheme in color_schemes_per_color_scheme_method:
            color_schemes.append(color_scheme)

    return color_schemes


def generate_color_scheme(base_color_rgb, hue_differences):
    base_color_hsl = (rgb_to_hsl(base_color_rgb))
    base_color_hue = base_color_hsl[0]
    base_color_saturation = base_color_hsl[1]
    base_color_lightness = base_color_hsl[2]

    color_scheme = []
    color_scheme.append(base_color_rgb)

    for hue_difference in hue_differences:
        color_scheme.append(hsl_to_rgb((base_color_hue + hue_difference) % 360, base_color_saturation, base_color_lightness))
    return color_scheme


# 1色
def generate_identity_color_scheme(base_color_rgb):
    color_scheme = generate_color_scheme(base_color_rgb, [])
    return color_scheme,


# 2色
def generate_analogy_color_scheme(base_color_rgb):
    color_scheme1 = generate_color_scheme(base_color_rgb, [30])
    color_scheme2 = generate_color_scheme(base_color_rgb, [-30])
    return color_scheme1, color_scheme2


def generate_intermediate_color_scheme(base_color_rgb):
    color_scheme1 = generate_color_scheme(base_color_rgb, [90])
    color_scheme2 = generate_color_scheme(base_color_rgb, [-90])
    return color_scheme1, color_scheme2


def generate_dyad_color_scheme(base_color_rgb):
    color_scheme = generate_color_scheme(base_color_rgb, [180])
    return color_scheme,


def generate_oponent_color_scheme(base_color_rgb):
    color_scheme1 = generate_color_scheme(base_color_rgb, [150])
    color_scheme2 = generate_color_scheme(base_color_rgb, [-150])
    return color_scheme1, color_scheme2


# 3色
def generate_dominant_color_scheme(base_color_rgb):
    color_scheme1 = generate_color_scheme(base_color_rgb, [30, 60])
    color_scheme2 = generate_color_scheme(base_color_rgb, [-30, 30])
    color_scheme3 = generate_color_scheme(base_color_rgb, [-60, -30])
    return color_scheme1, color_scheme2, color_scheme3


def generate_split_complementary_color_scheme(base_color_rgb):
    color_scheme1 = generate_color_scheme(base_color_rgb, [150, -150])
    color_scheme2 = generate_color_scheme(base_color_rgb, [-150, 60])
    color_scheme3 = generate_color_scheme(base_color_rgb, [-60, 150])
    return color_scheme1, color_scheme2, color_scheme3


def generate_triad_color_scheme(base_color_rgb):
    color_scheme = generate_color_scheme(base_color_rgb, [120, 240])
    return color_scheme,


# 4色
def generate_tetrad_color_scheme(base_color_rgb):
    color_scheme = generate_color_scheme(base_color_rgb, [90, 180, 270])
    return color_scheme,


# 5色
def generate_pentad_color_scheme(base_color_rgb):
    color_scheme = generate_color_scheme(base_color_rgb, [72, 144, 216, 288])
    return color_scheme,


# 6色
def generate_hexad_color_scheme(base_color_rgb):
    color_scheme = generate_color_scheme(base_color_rgb, [60, 120, 180, 240, 300])
    return color_scheme,


def remove_duplicated_color_from_color_schemes(color_schemes):
    """ 重複した色を削除する関数

    引数:
        color_schemes: 色の配列のリスト
    戻り値:
        color_schemes: 重複した色を削除した配列のリスト
    """

    SAME_COLOR_THRESHOLD = 0.01  # 色の閾値

    new_colors = []
    for color_scheme in color_schemes:
        unique_colors = []
        for color in color_scheme:
            if (is_exist_same_color(color, new_colors, SAME_COLOR_THRESHOLD)):
                pass
            else:
                new_colors.append(color)

    if (DEBUG):
        print(f"\ncolor_schemes: (重複した色を削除する前の配色群)")
        print_color_schemes(color_schemes)

    new_color_schemes = []
    for color in new_colors:
        new_color_scheme = []
        new_color_scheme.append(color)
        new_color_schemes.append(new_color_scheme)

    if (DEBUG):
        print(f"\nnew_color_schemes: (重複した色を削除した配色群)")
        print_color_schemes(new_color_schemes)

    return new_color_schemes


def remove_monochrome_color_from_color_schemes(color_schemes):
    LOWER_LIMIT = 10  # 彩度の閾値
    UPPER_LIMIT = 90  # 彩度の閾値

    def is_valid_hsl(color_rgb):
        color_hsl = rgb_to_hsl(color_rgb)
        return all(LOWER_LIMIT <= value <= UPPER_LIMIT for value in color_hsl[1:])

    def is_valid_scheme(color_scheme):
        return all(is_valid_hsl(color) for color in color_scheme)

    new_color_schemes = []

    for color_scheme in color_schemes:
        if is_valid_scheme(color_scheme):
            new_color_schemes.append(color_scheme)

    return new_color_schemes


def main():
    recommend_color_schemes = []
    recommend_color_schemes.append(generate_analogy_color_scheme([255, 0, 0]))
    recommend_color_schemes.append(generate_dominant_color_scheme([255, 0, 0]))

    # print_color_schemes(recommend_color_schemes)

    color_schemes = generate_all_color_schemes([255, 0, 0])
    print_color_schemes(color_schemes)


if __name__ == '__main__':
    main()
