from .generate_color_scheme_method import generate_all_color_schemes
from .helpers.transform_color import rgb_to_hsl, hsl_to_rgb
from .helpers.color_utils import print_color_scheme, print_color_schemes, print_colored_text

DEBUG = False
DEBUG = True


def add_lightness_variations_color_scheme(color_scheme, ligtness_diff):
    """明度による配色のバリエーションを増やす関数
    """
    new_color_scheme = []
    for color_rgb in color_scheme:
        color_hsl = rgb_to_hsl(color_rgb)
        new_color = hsl_to_rgb(color_hsl[0], color_hsl[1], color_hsl[2] + ligtness_diff)
        new_color_scheme.append(new_color)

    return new_color_scheme


def add_lightness_variations_color_scheme(color_scheme, saturation_diff):
    """ 彩度による配色のバリエーションを増やす関数
    """
    new_color_scheme = []
    for color_rgb in color_scheme:
        color_hsl = rgb_to_hsl(color_rgb)
        new_color = hsl_to_rgb(color_hsl[0], color_hsl[1] + saturation_diff, color_hsl[2])
        new_color_scheme.append(new_color)

    return new_color_scheme


def add_saturation_and_lightness_variations_color_scheme(color_scheme, saturation_diff, ligtness_diff):
    """明度と彩度による配色のバリエーションを増やす関数
    """

    new_color_scheme = []
    for color_rgb in color_scheme:
        color_hsl = rgb_to_hsl(color_rgb)
        new_color = hsl_to_rgb(color_hsl[0], color_hsl[1] + saturation_diff, color_hsl[2] + ligtness_diff)
        new_color_scheme.append(new_color)

    return new_color_scheme


def get_variations_for_color_schemes(color_schemes, saturation_diff, lightness_diff, variation_type):
    """ 
    引数で受け取る，要素の配色のバリエーションを増やす関数

    引数:
        color_schemes: 配色群
        lightness_diff: 明度の差(-100 ~ +100)

    戻り値:
        new_color_schemes: 明度の差を加えた配色群(基の配色群に明度の差を加えたもの)
    """

    new_color_schemes = []

    for i in range(len(color_schemes)):
        color_scheme = color_schemes[i]

        # 確認用出力
        if False:
            print_color_scheme(color_scheme)
            # print_color_scheme(add_lightness_variations_color_scheme(color_scheme, saturation_diff))

        if variation_type == "lightness":
            new_color_schemes.append(add_lightness_variations_color_scheme(color_scheme, lightness_diff))
        elif variation_type == "saturation":
            new_color_schemes.append(add_lightness_variations_color_scheme(color_scheme, saturation_diff))
        elif variation_type == "saturation_and_lightness":
            new_color_schemes.append(add_saturation_and_lightness_variations_color_scheme(color_scheme, saturation_diff, lightness_diff))
        else:
            raise ValueError("Invalid variation type. Use 'lightness' or 'saturation'.")

    return (new_color_schemes)


def main():
    test_color_schemes = generate_all_color_schemes([255, 128, 0])
    print_color_schemes(get_variations_for_color_schemes(test_color_schemes))


if __name__ == "__main__":
    main()
