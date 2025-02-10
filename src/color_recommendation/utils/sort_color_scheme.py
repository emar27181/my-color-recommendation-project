from utils.helpers.color_utils import print_color_scheme, calc_color_scheme_difference_delta_e_cie2000, print_color_schemes

DEBUG = False


def sort_color_scheme_by_color_difference(base_color_scheme, color_schemes):
    """引数で受け取った配色群を基準の配色との色差の昇順にソートする関数"""

    # print(base_color_scheme)
    # print(color_schemes)

    if (DEBUG):
        for i in range(len(color_schemes)):
            # print(base_color_scheme)
            print(f"[{i}]: ")

            print(f"used color scheme: ", end="")
            print_color_scheme(base_color_scheme)
            print(f"reco color scheme: ", end="")
            print_color_scheme(color_schemes[i])

            delta_e = calc_color_scheme_difference_delta_e_cie2000(base_color_scheme, color_schemes[i])
            print(f"delta_e = {delta_e}")

    color_schemes.sort(key=lambda color_scheme: calc_color_scheme_difference_delta_e_cie2000(base_color_scheme, color_scheme))

    # print_color_schemes(color_schemes)
    return color_schemes
