from .generate_color_scheme_method import generate_all_color_schemes
from .helpers.transform_color import rgb_to_hsl, hsl_to_rgb
from .helpers.color_utils import print_color_scheme, print_color_schemes


# 明度によって配色のバリエーションを増やす関数
def add_lightness_variations_color_scheme(color_scheme, ligtness_diff):
    new_color_scheme = []
    for color_rgb in color_scheme:
        color_hsl = rgb_to_hsl(color_rgb)
        new_color = hsl_to_rgb(color_hsl[0], color_hsl[1], color_hsl[2] + ligtness_diff)
        new_color_scheme.append(new_color)

    return new_color_scheme


# バリエーションを増やした配色を返す関数
def add_all_variations_color_schemes(color_schemes):
    # new_color_schemes = color_schemes

    # print(new_color_schemes)

    new_color_schemes = []
    for color_scheme_method in color_schemes:
        for color_scheme in color_scheme_method:

            # 確認用出力
            if False:
                print_color_scheme(color_scheme)
                print_color_scheme(add_lightness_variations_color_scheme(color_scheme, +20))
                print_color_scheme(add_lightness_variations_color_scheme(color_scheme, -20))

            new_color_schemes.append(add_lightness_variations_color_scheme(color_scheme, +20))
            new_color_schemes.append(add_lightness_variations_color_scheme(color_scheme, -20))

    color_schemes.append(new_color_schemes)

    return (color_schemes)


def main():
    test_color_schemes = generate_all_color_schemes([255, 128, 0])
    print_color_schemes(add_all_variations_color_schemes(test_color_schemes))


if __name__ == "__main__":
    main()
