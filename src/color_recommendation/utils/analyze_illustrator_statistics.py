from utils.helpers.json_utils import get_json_data, get_dir_list
from utils.helpers.color_utils import print_colored_text
from utils.helpers.transform_color import hex_to_rgb, rgb_to_hsl
import json
import math
import os

DEBUG = True
DEBUG = False
DIVIDE_NUM = 4  # 明度と彩度をいくつで区切るか


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


def _get_saturation_lightness_count_distribution(illustrator_name, illust_name, index_num):
    """_summary_

    Args:
        illustrator_name (_type_): _description_
        illust_name (_type_): _description_
        index_num (_type_): _description_

    ## メモ
    - 使用色相(used_hues~.json)と使用色(used_colors~.json)を別々で保存してるからややこしいことになってる(2025/04/27)
        - それぞれのjsonで同じイラスト群を読み込んでいれば，読込んだイラストとそのインデックス番号が一致するためindex_numでused_colorsのインデックスを参照している
    """

    saturation_lightness_count_distribution = [[0 for _ in range(DIVIDE_NUM + 1)] for _ in range(DIVIDE_NUM + 1)]
    input_file_path = f'src/color_recommendation/data/input/used_colors/used_colors_{illustrator_name}.json'
    used_colors_data = get_json_data(input_file_path)

    # print(f"{used_colors_data[index_num][0]['illustName']}") # これがillust_nameと一致していれば同画像を参照できている

    used_colors_info = used_colors_data[index_num]
    saturation_lightness_count_distribution2 = {} # 明度彩度をキーにして出現回数をカウントする辞書（仮実装）
    
    for used_color_info in used_colors_info:
        used_color_hex = used_color_info['color']
        used_color_rgb = hex_to_rgb(used_color_hex)
        used_color_hsl = rgb_to_hsl(used_color_rgb)
        
        saturation_index, lightness_index = round(used_color_hsl[1] / (100 / DIVIDE_NUM)), round(used_color_hsl[2] / (100 / DIVIDE_NUM))
        saturation_lightness_count_distribution[lightness_index][saturation_index] += 1
        
        key = f'{lightness_index},{saturation_index}'
        if key not in saturation_lightness_count_distribution2:
            saturation_lightness_count_distribution2[key] = 1  # 初期化

        else:
            saturation_lightness_count_distribution2[key] += 1
        
        # print_colored_text("■", used_color_rgb)
        # print(f"hsl{used_color_hsl}, (s,l) = ({saturation_index}, {lightness_index})")  

    # print(f"saturation_lightness_count_distribution = {saturation_lightness_count_distribution}")
    # print(f"saturation_lightness_count_distribution2 = {saturation_lightness_count_distribution2}")
    return saturation_lightness_count_distribution


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
    saturation_lightness_count_distribution = [[0 for _ in range(DIVIDE_NUM + 1)] for _ in range(DIVIDE_NUM + 1)]
    index_count = 0

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

        # 明度と彩度の分布を加算
        new_saturation_lightness_count_distribution = _get_saturation_lightness_count_distribution(illustrator_name, illust_name, index_count)
        for i in range(len(saturation_lightness_count_distribution)):
            for j in range(len(saturation_lightness_count_distribution[i])):
                saturation_lightness_count_distribution[i][j] += new_saturation_lightness_count_distribution[i][j]

        index_count += 1

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
        "mean_resultant_length_ave": mean_resultant_length_sum / count_one_or_more_colors_used if count_one_or_more_colors_used > 0 else -1,
        "mean_resultant_length_distribution": mean_resultant_length_sum_distribution,
        "saturation_lightness_count_distribution": saturation_lightness_count_distribution,
    }

    return statistics


def get_statistics_by_illustrator(illustrator_name, keyword):
    """ 引数で受け取るイラストレーターのイラストのキーワードの統計データを取得する関数

    引数:
        illustrator_name: イラストレーター名(文字列)
        keyword: 統計データのキーワード(文字列)

    戻り値:
        statistics: イラストレーターの統計データ
    """
    statistics = _extract_statistics_by_illustrator(illustrator_name)

    if (keyword == "all"):
        return statistics
    else:
        return statistics[keyword]


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

        if (DEBUG):
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
        if (DEBUG):
            print(f"=== {illustrator_name} ========================")
        for illustrator_data in data:
            illustrator_data_name = illustrator_data["illustrator_name"]
            if (illustrator_name == illustrator_data_name):

                chromatic_colors_count_distribution = illustrator_data["chromatic_colors_count_distribution"]
                # print(f"chromatic_colors_count_distribution = {chromatic_colors_count_distribution}")
                monochrome_rate = chromatic_colors_count_distribution[0] / sum(chromatic_colors_count_distribution)
                if (monochrome_rate < MONOCHROME_THRESHOLD):
                    not_monochrome_illustrator_list.append(illustrator_name)
                    if (DEBUG):
                        print(f"モノクロ率 = {(round(monochrome_rate * 10000) / 100 )}%: モノクロイラストのイラストレーターではないため，リストに追加します．")
                else:
                    if (DEBUG):
                        print(f"モノクロ率 = {(round(monochrome_rate * 10000) / 100 )}%: モノクロイラストのイラストレーターのため，リストに追加しません．")

    print("モノクロイラストを含むイラストレーターが除外されました．")

    return not_monochrome_illustrator_list


def _get_illust_count_by_illustrator(illustrator_name):

    input_dir_path = f"src/color_recommendation/data/input/illustration/{illustrator_name}"

    count = 0
    for filename in os.listdir(input_dir_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            count += 1

    if DEBUG:
        print(f"イラストの枚数: {count:5d} ({illustrator_name})")

    return count


def get_excluded_small_number_illustrator_list(illustrator_list, threshold):
    """ イラストの枚数が少ないイラストレーターを除外する関数
    """

    new_illustrator_list = []

    for illustrator in illustrator_list:
        illust_count = _get_illust_count_by_illustrator(illustrator)
        if illust_count >= threshold:
            new_illustrator_list.append(illustrator)

    print(f"イラストの枚数が{threshold}枚未満のイラストレーターが除外されました．")

    return new_illustrator_list


def save_recall_at_k(input_file_path, output_file_path):
    """ recall@kを保存する関数

    Args:
        input_file_path (str): 入力ファイルパス
        output_file_path (str): 出力ファイルパス
    """
    data = get_json_data(input_file_path)
    # print(f"data = {data}")


def save_recall_at_k_for_illustrators(illustrator_list, sort_type, check_subject):
    """ 引数で受け取るイラストレーターリストのrecall@kを保存する関数

    Args:
        illustrator_list (list): イラストレーターのリスト
    """
    recall_at_k_data = []

    for illustrator_name in illustrator_list:
        print(f"\n=== {illustrator_name} ========================")
        if (check_subject == "tone"):
            dir_name_list = get_dir_list(f"src/color_recommendation/data/output/is_contained_next_{check_subject}")
            for dir_name in dir_name_list:
                input_file_path = f"src/color_recommendation/data/output/is_contained_next_{check_subject}/{dir_name}/{sort_type}/is_contained_next_{check_subject}_{illustrator_name}.json"
                output_file_path = f"src/color_recommendation/data/output/recall_at_k/recall_at_k_{check_subject}_{dir_name}_{illustrator_name}.json"
                save_recall_at_k(input_file_path, output_file_path)
        else:
            input_file_path = f"src/color_recommendation/data/output/is_contained_next_{check_subject}/{sort_type}/is_contained_next_{check_subject}_{illustrator_name}.json"
            output_file_path = f"src/color_recommendation/data/output/recall_at_k/recall_at_k_{check_subject}_{sort_type}_{illustrator_name}.json"
            save_recall_at_k(input_file_path, output_file_path)
