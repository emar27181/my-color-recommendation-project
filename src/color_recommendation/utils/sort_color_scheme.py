from utils.helpers.color_utils import print_color_scheme, calc_color_scheme_difference_delta_e_cie2000, print_color_schemes, calc_pccs_color_diff
import random
from utils.helpers.json_utils import get_json_data
from utils.analyze_illustrator_statistics import get_statistics_by_illustrator
from utils.helpers.calc_rec_score import calc_same_hue_score

DEBUG = False
# DEBUG = True


def sort_color_schemes_by_color_difference(base_color_scheme, color_schemes):
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


def _is_included_pccs_diff_in_color_scheme(color_scheme, pccs_diff):
    """引数で受け取った配色群に特定の色相差が含まれているか判定する関数
    引数:
        color_scheme: 配色群
        pccs_diff: 判定するpccs_diff

    戻り値:
        True: 含まれている
        False: 含まれていない
    """

    pccs_diffs = calc_pccs_color_diff(color_scheme[0], color_scheme)

    if pccs_diff in pccs_diffs:
        if (DEBUG):
            print(f"True (pccs_diff: {pccs_diff}, pccs_diffs: {pccs_diffs})")
        return True

    else:
        if (DEBUG):
            print(f"False (pccs_diff: {pccs_diff}, pccs_diffs: {pccs_diffs})")
        return False


def sort_color_schemes_by_mean_resultant_length(color_schemes, illustrator_name):
    """引数で受け取った配色群を平均結果長にソートする関数
    引数:
        color_schemes: ソートする配色群

    戻り値:
        color_schemes: 色差の昇順にソートされた配色群

    """
    new_color_schemes = []

    mean_resultant_length_distribution = get_statistics_by_illustrator(illustrator_name, "mean_resultant_length_distribution")
    print(f"mean_resultant_length_distribution: {mean_resultant_length_distribution}")

    pccs_sorted_used_count = sorted(range(len(mean_resultant_length_distribution)),
                                    key=lambda i: mean_resultant_length_distribution[i],
                                    reverse=True)  # 値で降順に並べたときのインデックスを取得

    """
    for color_scheme in color_schemes:
        calc_pccs_color_diff(color_scheme[0], color_scheme)
    """

    print(f"pccs_sorted_use_count {pccs_sorted_used_count}")

    for pccs in pccs_sorted_used_count:
        for color_scheme in color_schemes:
            if _is_included_pccs_diff_in_color_scheme(color_scheme, pccs):
                new_color_schemes.append(color_scheme)
                color_schemes.remove(color_scheme)

    return new_color_schemes


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
            saturation_lightness_count_distribution = illustrator_data["saturation_lightness_count_distribution"]

            return chromatic_colors_count_ave, achromatic_colors_count_ave, chromatic_colors_rate_ave, achromatic_colors_rate_ave, chromatic_colors_count_distribution, used_pccs_count_sum_distribution, mean_resultant_length_ave, saturation_lightness_count_distribution

    print(f"イラストレーター名: {illustrator_name} のデータが見つかりませんでした．")
    return None, None, None, None, None, None, None


def sort_color_schemes_by_used_color_count(color_schemes, illustrator_name):
    """引数で受け取った配色をイラストレーターの使用比率を基にソートする関数
    """

    print(f"=== {illustrator_name} ==================== ")

    chromatic_colors_count_ave, achromatic_colors_count_ave, chromatic_colors_rate_ave, achromatic_colors_rate_ave, chromatic_colors_count_distribution, used_pccs_count_sum_distribution, mean_resultant_length_ave, saturation_lightness_count_distribution = _get_analysis_data(illustrator_name)

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


def _print_rec_color_schemes_info(color_schemes_info):
    """配色群の情報(配色の色やスコア)を表示する関数
    引数:
        color_schemes_info: 配色群の情報
    戻り値:
        None
    """

    for color_scheme_info in color_schemes_info:
        print(f"score = {round(color_scheme_info['score']*1000)/1000} ", end="")
        print_color_scheme(color_scheme_info['rec_color_scheme'])


def _calc_rec_color_scheme_score(used_color_scheme, rec_color_scheme):
    """推薦配色のスコアを計算する関数
    引数:
        used_color_scheme: 使用配色
        rec_color_scheme: 推薦配色

    戻り値:
        score: スコア
    """

    # 同じ色相かどうかでスコアを計算
    same_hue_score = calc_same_hue_score(used_color_scheme, rec_color_scheme)

    return same_hue_score


def sort_color_schemes_by_custom_v0(used_color_scheme, rec_color_schemes, illustrator_name):
    """ カスタムの順序で配色をソートする関数

    Args:
        color_schemes (_type_): 配色群
        illustrator_name (_type_): イラストレーター名
    Returns:
        _type_: _description_
    """

    rec_color_schemes_info = []

    print(f"=== {illustrator_name} ==================== ")

    # 推薦配色ごとにスコアを計算
    for rec_color_scheme in rec_color_schemes:
        score = _calc_rec_color_scheme_score(used_color_scheme, rec_color_scheme)

        rec_color_schemes_info.append({
            "rec_color_scheme": rec_color_scheme,
            "score": score
        })

    # スコアの降順でソート
    rec_color_schemes_info = sorted(rec_color_schemes_info, key=lambda x: x['score'], reverse=True)

    # 確認用出力
    if (DEBUG):
        _print_rec_color_schemes_info(rec_color_schemes_info)

    sorted_rec_color_schemes = []

    for rec_color_scheme_info in rec_color_schemes_info:
        sorted_rec_color_schemes.append(rec_color_scheme_info['rec_color_scheme'])

    return sorted_rec_color_schemes

def sort_color_schemes_by_used_tone(color_schemes, illustrator_name):
    """引数で受け取った配色群をイラストレーターの使用トーン分布に基づいてソートする関数
    引数:
        color_schemes: ソートする配色群
        illustrator_name: イラストレーター名

    戻り値:
        color_schemes: トーン分布に基づいてソートされた配色群
    """

    print(f"=== {illustrator_name} ==================== ")

    chromatic_colors_count_ave, achromatic_colors_count_ave, chromatic_colors_rate_ave, achromatic_colors_rate_ave, chromatic_colors_count_distribution, used_pccs_count_sum_distribution, mean_resultant_length_ave, saturation_lightness_count_distribution = _get_analysis_data(illustrator_name)

    print(f"saturation_lightness_count_distribution:")
    for i in range(len(saturation_lightness_count_distribution)):
        print(f"{i}: {saturation_lightness_count_distribution[i]}")

    # # 使用頻度順にトーン数を並べ替え
    # used_tone_count_list_sorted_by_used_times = sorted(
    #     [i for i in range(len(used_pccs_count_sum_distribution))],
    #     key=lambda i: used_pccs_count_sum_distribution[i],
    #     reverse=True
    # )  # used_tone_count_list_sorted_by_used_times: 使われた回数が多い順でトーン数を並べたリスト

    # new_color_schemes = []

    # # よく使われたトーン数の順で配色を追加
    # for tone_count in used_tone_count_list_sorted_by_used_times:
    #     for color_scheme in color_schemes:
    #         if len(color_scheme) == tone_count:
    #             new_color_schemes.append(color_scheme)
                # color_schemes.remove(color_scheme)

    return []

def shuffle_color_schemes(color_schemes):
    """引数で受け取った配色群をランダムに並び替える関数"""

    random.shuffle(color_schemes)

    return color_schemes

