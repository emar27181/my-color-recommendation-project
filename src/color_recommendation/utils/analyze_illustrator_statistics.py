from utils.helpers.json_utils import get_json_data
import json
import math

DEBUG = True
DEBUG = False


def _mean_resultant_length(angles_deg):
    """
    角度のリスト（度単位）から、平均結果長を計算して返す関数。
    """

    if len(angles_deg) == 0:
        return 0

    # 角度をラジアンに変換
    angles_rad = [math.radians(angle) for angle in angles_deg]

    # 各角度のcosとsinの合計を計算
    sum_cos = sum(math.cos(angle) for angle in angles_rad)
    sum_sin = sum(math.sin(angle) for angle in angles_rad)

    n = len(angles_rad)
    avg_cos = sum_cos / n
    avg_sin = sum_sin / n

    # 平均結果長の計算
    R = math.sqrt(avg_cos**2 + avg_sin**2)
    return R


def _extract_statistics_by_illustrator(illustrator_name):
    """ イラストレーターの統計データを抽出する関数

    引数:
        illustrator_name: イラストレーターの名前(文字列)

    戻り値:
        statistics: イラストレーターの統計データ
    """

    DIV_NUMBER = 12  # 平均結果長の分布で分割する数

    input_file_path = f"src/color_recommendation/data/input/used_hues/used_hues_{illustrator_name}.json"
    data = get_json_data(input_file_path)

    chromatic_colors_count_sum = 0
    achromatic_colors_count_sum = 0
    chromatic_colors_rate_sum = 0
    achromatic_colors_rate_sum = 0
    used_hues_rate_sum_distribution = [0] * 360
    used_pccs_count_sum_distribution = [0] * 25
    count_one_or_more_colors_used = 0
    mean_resultant_length_sum = 0
    mean_resultant_length_sum_distribution = [0] * (DIV_NUMBER + 1)
    chromatic_colors_count_distribution = [0] * 20

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

        if (len(used_chromatic_hues) >= 1):
            count_one_or_more_colors_used += 1
            # 使用色相の平均結果長の計算
            mean_resultant_length_sum += _mean_resultant_length(used_chromatic_hues)

            # 使用色相の平均結果長の分布の加算
            mean_resultant_index = round(_mean_resultant_length(used_chromatic_hues) * DIV_NUMBER)  # (0.0 ~ 1.0) -> (0 ~ DIV_NUMBER)
            mean_resultant_length_sum_distribution[mean_resultant_index] += 1

        # 使用PCCSの出現回数の分布の加算
        for pccs in used_pccs:
            used_pccs_count_sum_distribution[pccs] += 1

        # 有彩色無彩色の出現回数の加算
        chromatic_colors_count_sum += chromatic_colors_count
        achromatic_colors_count_sum += achromatic_colors_count

        # 有彩色の出現回数の分布の加算
        chromatic_colors_count_distribution[chromatic_colors_count] += 1

        # 無彩色の使用率の加算
        for used_hue_rate in used_hues_rate:
            if (used_hue_rate[0] == -10):  # 黒の場合
                achromatic_colors_rate_sum += used_hue_rate[1]
            elif (used_hue_rate[0] == -11):  # 白の場合
                achromatic_colors_rate_sum += used_hue_rate[1]

    mean_resultant_length_sum_distribution.reverse()  # 0~12(違う角度を使っている順) → 12~0(同じ角度を使っている順)に反転

    statistics = {
        "illustrator_name": illustrator_name,
        "chromatic_colors_count_ave": chromatic_colors_count_sum / len(data),
        "achromatic_colors_count_ave": achromatic_colors_count_sum / len(data),
        "chromatic_colors_rate_ave": 1 - (achromatic_colors_rate_sum / len(data)),
        "achromatic_colors_rate_ave": achromatic_colors_rate_sum / len(data),
        "chromatic_colors_count_distribution": chromatic_colors_count_distribution,
        # "used_hues_rate_ave_distribution": [x / len(data) for x in used_hues_rate_sum_distribution], # 使っていないためコメントアウト(2025/04/06)
        "used_pccs_count_sum_distribution": used_pccs_count_sum_distribution,
        "mean_resultant_length_ave": mean_resultant_length_sum / count_one_or_more_colors_used,
        "mean_resultant_length_distribution": mean_resultant_length_sum_distribution,
    }

    return statistics


def print_statistics_for_illustrators(illustrator_list, keyword):
    """ 引数で受け取るイラストレーターのイラストのキーワードの統計データを表示する関数

    引数:
        illustrater_list: 推薦配色を生成させたいイラストレーターのリスト(文字列)

    戻り値:
        None
    """
    for illustrator_name in illustrator_list:
        print(f"\n=== {illustrator_name} ========================")
        statistics = _extract_statistics_by_illustrator(illustrator_name)

        for data in statistics:
            if (data == keyword or keyword == "all"):
                print(f"{data} = {statistics[data]}")


def get_statistics_by_illustrator(illustrator_name, keyword):
    """ 引数で受け取るイラストレーターのイラストのキーワードの統計データを取得する関数

    引数:
        illustrator_name: イラストレーター名(文字列)

    戻り値:
        statistics: イラストレーターの統計データ
    """
    statistics = _extract_statistics_by_illustrator(illustrator_name)

    if (keyword == "all"):
        return statistics
    else:
        return statistics[keyword]


def save_statistics_for_illustrators(illustrator_list):
    """ 引数で受け取るイラストレーターのイラストの統計データを保存する関数

    引数:
        illustrater_list: 推薦配色を生成させたいイラストレーターのリスト(文字列)

    戻り値:
        None
    """
    statistics_data = []

    for illustrator_name in illustrator_list:
        print(f"\n=== {illustrator_name} ========================")
        statistics = _extract_statistics_by_illustrator(illustrator_name)

        print("~~~ statistics ~~~")
        for data in statistics:
            print(f"{data} = {statistics[data]}")

        statistics_data.append(statistics)

    # print(f"statistics_data = {statistics_data}")

    output_file_path = "src/color_recommendation/data/input/statistics_for_illustrators.json"
    with open(output_file_path, 'w', encoding='utf-8') as file:
        json.dump(statistics_data, file, ensure_ascii=False, indent=4)
        print(f"{output_file_path} が保存されました．")


def get_not_monochrome_illustrator_list(illustrator_list):
    """モノクロイラストを除くイラストレーターのリストを取得する関数

    引数:
        illustrator_list: 推薦配色を生成させたいイラストレーターのリスト(文字列)
    """
    MONOCHROME_THRESHOLD = 0.5  # モノクロ率の閾値

    input_file_path = "src/color_recommendation/data/input/statistics_for_illustrators.json"
    data = get_json_data(input_file_path)
    not_monochrome_illustrator_list = []

    for illustrator_name in illustrator_list:
        print(f"=== {illustrator_name} ========================")
        for illustrator_data in data:
            illustrator_data_name = illustrator_data["illustrator_name"]
            if (illustrator_name == illustrator_data_name):

                chromatic_colors_count_distribution = illustrator_data["chromatic_colors_count_distribution"]
                # print(f"chromatic_colors_count_distribution = {chromatic_colors_count_distribution}")
                monochrome_rate = chromatic_colors_count_distribution[0] / sum(chromatic_colors_count_distribution)

                if (monochrome_rate < MONOCHROME_THRESHOLD):
                    not_monochrome_illustrator_list.append(illustrator_name)
                    print(f"モノクロ率 = {(round(monochrome_rate * 10000) / 100 )}%: モノクロイラストのイラストレーターではないため，リストに追加します．")
                else:
                    print(f"モノクロ率 = {(round(monochrome_rate * 10000) / 100 )}%: モノクロイラストのイラストレーターのため，リストに追加しません．")

    return not_monochrome_illustrator_list
