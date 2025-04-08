from utils.helpers.color_utils import print_color_scheme, calc_color_scheme_difference_delta_e_cie2000, print_color_schemes
import random
from utils.helpers.json_utils import get_json_data

DEBUG = False


def sort_color_scheme_by_color_difference(base_color_scheme, color_schemes):
    """引数で受け取った配色群を基準の配色との色差の昇順にソートする関数
    引数:
        base_color_scheme: 基準の配色
        color_schemes: ソートする配色群

    戻り値:
        color_schemes: 色差の昇順にソートされた配色群

    """

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


def _get_analysis_data(illustrator_name):
    """イラストレーターの統計データを取得する関数
    引数:
        illustrator_name: イラストレーター名

    戻り値:
        illustrator_data: イラストレーターの統計データ
    """

    data = get_json_data("src/color_recommendation/data/input/statistics_for_illustrators.json")

    for illustrator_data in data:
        if illustrator_data["illustrator_name"] == illustrator_name:
            chromatic_colors_count_ave = illustrator_data["chromatic_colors_count_ave"]
            achromatic_colors_count_ave = illustrator_data["achromatic_colors_count_ave"]
            chromatic_colors_rate_ave = illustrator_data["chromatic_colors_rate_ave"]
            achromatic_colors_rate_ave = illustrator_data["achromatic_colors_rate_ave"]
            chromatic_colors_count_distribution = illustrator_data["chromatic_colors_count_distribution"]
            used_pccs_count_sum_distribution = illustrator_data["used_pccs_count_sum_distribution"]
            mean_resultant_length_ave = illustrator_data["mean_resultant_length_ave"]

            return chromatic_colors_count_ave, achromatic_colors_count_ave, chromatic_colors_rate_ave, achromatic_colors_rate_ave, chromatic_colors_count_distribution, used_pccs_count_sum_distribution, mean_resultant_length_ave

    print(f"イラストレーター名: {illustrator_name} のデータが見つかりませんでした．")
    return None, None, None, None, None, None, None


def sort_color_scheme_by_used_trend(color_schemes, illustrator_name):
    """引数で受け取った配色をイラストレーターの使用比率を基にソートする関数
    """

    print(f"=== {illustrator_name} ==================== ")

    chromatic_colors_count_ave, achromatic_colors_count_ave, chromatic_colors_rate_ave, achromatic_colors_rate_ave, chromatic_colors_count_distribution, used_pccs_count_sum_distribution, mean_resultant_length_ave = _get_analysis_data(illustrator_name)

    # 使用頻度順に色相数を並べ替え
    chromatic_colors_count_list_sorted_by_used_times = sorted(
        [i for i in range(len(chromatic_colors_count_distribution))],
        key=lambda i: chromatic_colors_count_distribution[i],
        reverse=True
    )  # chromatic_colors_count_list_sorted_by_used_times: 使われた回数が多い順で色相数を並べたリスト

    new_color_schemes = []

    # よく使われた色相数の順で配色を追加
    for colors_count in chromatic_colors_count_list_sorted_by_used_times:
        for color_scheme in color_schemes:
            if len(color_scheme) == colors_count:
                new_color_schemes.append(color_scheme)
                # color_schemes.remove(color_scheme)

    return new_color_schemes


def shuffle_color_schemes(color_schemes):
    """引数で受け取った配色群をランダムに並び替える関数"""

    random.shuffle(color_schemes)

    return color_schemes
