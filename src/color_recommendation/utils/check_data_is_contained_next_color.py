from utils.helpers.color_utils import calculate_color_difference_delta_e_cie2000, print_colored_text, calc_angle_diff, calc_distance_diff
from utils.helpers.transform_color import hex_to_rgb, rgb_to_hsl
import json
import os

DEBUG = True
DEBUG = False


def is_contained_color(next_color, color_schemes):
    for i in range(len(color_schemes)):

        if (DEBUG):
            print(f"--- {i+1} 配色目 -------------")

        for j in range(len(color_schemes[i])):
            recommend_color = color_schemes[i][j]["color"]

            diff = calculate_color_difference_delta_e_cie2000(hex_to_rgb(next_color), hex_to_rgb(recommend_color))

            if (DEBUG):
                print("next_color: ", end="")
                print_colored_text("■ ", hex_to_rgb(next_color))
                print(", recommend_color: ", end="")
                print_colored_text("■", hex_to_rgb(recommend_color))
                print(f", delta_e = {diff}")

            if (diff <= 10):
                return True, i

    return False, -1


def is_contained_hue(next_color, color_schemes):
    """
    次に塗ったとされる色相が推薦配色群に含まれているかどうかを調べる関数
    """
    for i in range(len(color_schemes)):

        if (DEBUG):
            print(f"--- {i+1} 番目の推薦配色 -------------")

        for j in range(len(color_schemes[i])):
            recommend_color = color_schemes[i][j]["color"]

            next_color_rgb = hex_to_rgb(next_color)
            recommend_color_rgb = hex_to_rgb(recommend_color)
            next_color_hsl = rgb_to_hsl(next_color_rgb)
            recommend_color_hsl = rgb_to_hsl(recommend_color_rgb)

            # diff = calculate_color_difference_delta_e_cie2000(hex_to_rgb(next_color), hex_to_rgb(recommend_color))
            hue_diff = calc_angle_diff(next_color_hsl[0], recommend_color_hsl[0])

            if (DEBUG):
                print(f"[{j}]", end="")
                print("next_color: ", end="")
                print_colored_text("■ ", next_color_rgb)
                print(f"({next_color_hsl[0]}), recommend_color: ", end="")
                print_colored_text("■", recommend_color_rgb)
                print(f" ({recommend_color_hsl[0]}), diff = {hue_diff}")

            if (hue_diff <= 15):
                if (DEBUG):
                    print(f"k = {i+1}")
                return True, i

    if (DEBUG):
        print(f"k = -1")
    return False, -1


def is_contained_next_tone(next_color, color_schemes):
    """
    次に塗ったとされるトーンが推薦配色群に含まれているかどうかを調べる関数
    """
    for i in range(len(color_schemes)):

        if (DEBUG):
            print(f"--- {i+1} 番目の推薦配色 -------------")

        for j in range(len(color_schemes[i])):
            recommend_color = color_schemes[i][j]["color"]

            next_color_rgb = hex_to_rgb(next_color)
            recommend_color_rgb = hex_to_rgb(recommend_color)
            next_color_hsl = rgb_to_hsl(next_color_rgb)
            recommend_color_hsl = rgb_to_hsl(recommend_color_rgb)

            tone_diff = calc_distance_diff(next_color_hsl[1], next_color_hsl[2], recommend_color_hsl[1], recommend_color_hsl[2])

            if (DEBUG):
                print(f"[{j}]", end="")
                print("next_color: ", end="")
                print_colored_text("■ ", next_color_rgb)
                print(f"({next_color_hsl[0]}), recommend_color: ", end="")
                print_colored_text("■", recommend_color_rgb)
                print(f" ({recommend_color_hsl[0]}), diff = {tone_diff}")

            if (tone_diff <= 15):
                if (DEBUG):
                    print(f"k = {i+1}")
                return True, i

    if (DEBUG):
        print(f"k = -1")
    return False, -1
    pass


def save_data_is_contained_next_for_illustrators(illutrator_list, sort_type, check_subject):
    """
    引数で受け取るリスト内のイラストレーターの推薦配色群に次に塗ったとされる色があるかを保存する関数

    引数:
        illutrater_list: 評価したいイラストレーターのリスト(文字列)
        sort_type: ソートの種類(random/color_diff)
        check_subject: チェックされる対象(color/hue)
    戻り値:
        None
    """

    for illutrator_name in illutrator_list:
        print(f"=== {illutrator_name} ========================")

        input_file_path = ""
        if (check_subject == "tone"):
            input_file_path = f"src/color_recommendation/data/output/recommend_colors/sort_by_{sort_type}/recommend_colors_{illutrator_name}.json"
        else:
            input_file_path = f"src/color_recommendation/data/output/recommend_{check_subject}s/sort_by_{sort_type}/recommend_{check_subject}s_{illutrator_name}.json"

        with open(input_file_path, 'r', encoding='utf-8') as file:
            recommended_colors_data = json.load(file)

        is_contained_next_color_data = check_data_is_contained_next(recommended_colors_data, check_subject)

        output_file_path = f"src/color_recommendation/data/output/is_contained_next_{check_subject}/{sort_type}/is_contained_next_{check_subject}_{illutrator_name}.json"

        if not os.path.exists(os.path.dirname(output_file_path)):
            output_dir_path = f"src/color_recommendation/data/output/is_contained_next_{check_subject}/{sort_type}"
            os.makedirs(output_dir_path)
            print(f"{output_dir_path} ディレクトリが作成されました．")

        with open(output_file_path, 'w', encoding='utf-8') as file:
            json.dump(is_contained_next_color_data, file, ensure_ascii=False, indent=4)
            print(f"{output_file_path} が保存されました．(次の色が含まれているかどうかを保存するデータの作成)")


def check_data_is_contained_next(data, check_subject):
    """ 引数で受け取る対象が次の色が含まれているかどうかを調べる関数

    引数:
        data (_type_): データ
        check_subject (_type_): チェックされる対象(color/hue)

    戻り値:
        data_recall_at_k (_type_): 次の色が含まれているかどうかのデータ
    """

    data_recall_at_k = []

    illust_count = 0
    for illust_data in data:

        # 空のデータを読み飛ばし
        if not illust_data:
            continue

        color_scheme = illust_data["color_scheme"]
        recommend_color_schemes = illust_data["recommend_color_schemes"]

        recall_at_k_per_illust = []

        # 次の色が含まれているかどうかの判定
        for i in range(len(color_scheme) - 1):

            if (DEBUG):
                print(f"\n=== {illust_count+1} 枚目のイラストの {i+1} 番目の使用色  ============")

            next_color = color_scheme[i + 1]["color"]

            # 次の色が含まれているかどうかを判定
            if (check_subject == "color"):
                is_contained, scheme_index = is_contained_color(next_color, recommend_color_schemes)
            elif (check_subject == "hue"):
                is_contained, scheme_index = is_contained_hue(next_color, recommend_color_schemes)
            elif (check_subject == "tone"):
                is_contained, scheme_index = is_contained_next_tone(next_color, recommend_color_schemes)
            else:
                print("check_subjectの値が不正です")

            # recall@kのデータの作成
            is_contained_data = {
                "next_color_index": i + 1,
                "k": scheme_index,
                "is_contained_next_color": is_contained
            }
            recall_at_k_per_illust.append(is_contained_data)

        data_recall_at_k_per_illust = {
            "illust_name": illust_data["illust_name"],
            "recall_at_k": recall_at_k_per_illust,
        }
        data_recall_at_k.append(data_recall_at_k_per_illust)

        illust_count += 1

    return data_recall_at_k
