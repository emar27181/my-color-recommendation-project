from helpers.transform_color import rgb_to_hsl, hsl_to_rgb, rgb_to_hex, hex_to_rgb
from helpers.color_utils import print_colored_text, print_color_schemes


def generate_all_color_schemes(base_color_rgb):
    color_schemes = []

    color_schemes.append(generate_identity_color_scheme(base_color_rgb))

    color_schemes.append(generate_intermediate_color_scheme(base_color_rgb))

    color_schemes.append(generate_dyad_color_scheme(base_color_rgb))
    color_schemes.append(generate_analogy_color_scheme(base_color_rgb))
    color_schemes.append(generate_oponent_color_scheme(base_color_rgb))

    color_schemes.append(generate_dominant_color_scheme(base_color_rgb))
    color_schemes.append(generate_split_complementary_color_scheme(base_color_rgb))
    color_schemes.append(generate_triad_color_scheme(base_color_rgb))

    color_schemes.append(generate_tetrad_color_scheme(base_color_rgb))

    color_schemes.append(generate_pentad_color_scheme(base_color_rgb))

    color_schemes.append(generate_hexad_color_scheme(base_color_rgb))

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


def main():
    recommend_color_schemes = []
    recommend_color_schemes.append(generate_analogy_color_scheme([255, 0, 0]))
    recommend_color_schemes.append(generate_dominant_color_scheme([255, 0, 0]))

    # print_color_schemes(recommend_color_schemes)

    color_schemes = generate_all_color_schemes([255, 0, 0])
    print_color_schemes(color_schemes)


if __name__ == '__main__':
    main()
