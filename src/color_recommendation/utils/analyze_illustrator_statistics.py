from utils.helpers.json_utils import get_json_data

DEBUG = True
DEBUG = False


def _extract_statistics_by_illustrator(illustrator_name):
    """ イラストレーターの統計データを抽出する関数

    引数:
        illustrator_name: イラストレーターの名前(文字列)

    戻り値:
        statistics: イラストレーターの統計データ
    """

    input_file_path = f"src/color_recommendation/data/input/used_hues/used_hues_{illustrator_name}.json"
    data = get_json_data(input_file_path)

    chromatic_colors_count_sum = 0
    achromatic_colors_count_sum = 0
    chromatic_colors_rate_sum = 0
    achromatic_colors_rate_sum = 0
    used_hues_rate_sum_distribution = [0] * 360
    used_pccs_count_sum_distribution = [0] * 25

    for illust_data in data:
        illust_name = illust_data["illust_name"]
        used_hues_rate = illust_data["used_hues_rate"]
        chromatic_colors_count = illust_data["chromatic_colors_count"]
        achromatic_colors_count = illust_data["achromatic_colors_count"]
        used_chromatic_hues = illust_data["used_chromatic_hues"]
        used_pccs = illust_data["used_pccs"]
        hue_diffs = illust_data["hue_diffs"]

        # 確認用出力
        if (DEBUG):
            print(f"=== {illust_name} ================")
            print(f"used_hues_rate = {used_hues_rate}")
            print(f"chromatic_colors_count = {chromatic_colors_count}")
            print(f"achromatic_colors_count = {achromatic_colors_count}")
            print(f"used_chromatic_hues = {used_chromatic_hues}")
            print(f"used_pccs = {used_pccs}")
            print(f"hue_diffs = {hue_diffs}")

        # 統計データの集計
        # 使用色相の出現率の加算
        for used_hue_rate in used_hues_rate:
            if (used_hue_rate[0] >= 0):  # 有彩色の場合
                used_hues_rate_sum_distribution[used_hue_rate[0] % 360] += used_hue_rate[1]

        # 使用PCCSの出現回数の分布の加算
        for pccs in used_pccs:
            used_pccs_count_sum_distribution[pccs] += 1

        # 有彩色無彩色の出現回数の加算
        chromatic_colors_count_sum += chromatic_colors_count
        achromatic_colors_count_sum += achromatic_colors_count

        # 無彩色の使用率の加算
        for used_hue_rate in used_hues_rate:
            if (used_hue_rate[0] == -10):  # 黒の場合
                achromatic_colors_rate_sum += used_hue_rate[1]
            elif (used_hue_rate[0] == -11):  # 白の場合
                achromatic_colors_rate_sum += used_hue_rate[1]

    statistics = {
        "chromatic_colors_count_ave": chromatic_colors_count_sum / len(data),
        "achromatic_colors_count_ave": achromatic_colors_count_sum / len(data),
        "chromatic_colors_rate_ave": 1 - (achromatic_colors_rate_sum / len(data)),
        "achromatic_colors_rate_ave": achromatic_colors_rate_sum / len(data),
        "used_hues_rate_ave_distribution": [x / len(data) for x in used_hues_rate_sum_distribution],
        "used_pccs_count_sum_distribution": used_pccs_count_sum_distribution,
    }

    return statistics


def save_statistics_for_illustrators(illustrator_list):
    """ 引数で受け取るイラストレーターのイラストの統計データを保存する関数

    引数:
        illustrater_list: 推薦配色を生成させたいイラストレーターのリスト(文字列)

    戻り値:
        None
    """

    for illustrator_name in illustrator_list:
        print(f"\n=== {illustrator_name} ========================")
        statistics = _extract_statistics_by_illustrator(illustrator_name)

        print("~~~ statistics ~~~")
        for data in statistics:
            print(f"{data} = {statistics[data]}")
