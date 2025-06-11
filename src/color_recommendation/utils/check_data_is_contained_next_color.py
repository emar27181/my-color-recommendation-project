from utils.helpers.color_utils import calculate_color_difference_delta_e_cie2000, print_colored_text, calc_angle_diff, calc_distance_diff, print_color_scheme, print_color_schemes
from utils.helpers.transform_color import hex_to_rgb, rgb_to_hsl
from utils.helpers.json_utils import save_json_data, get_json_data
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
                return True, i + 1

    return False, -1


def is_contained_hue(next_color, color_schemes_data):
    """
    次に塗ったとされる色相が推薦配色群に含まれているかどうかを調べる関数
    """
    for i in range(len(color_schemes_data)):

        if (DEBUG):
            print(f"--- {i+1} 番目の推薦配色 (", end="")
            for color_data in color_schemes_data[i]:
                print_colored_text("■", hex_to_rgb(color_data["color"]))
            print(") -------------")

        for j in range(len(color_schemes_data[i])):
            recommend_color = color_schemes_data[i][j]["color"]

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
                return True, i + 1

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
                return True, i + 1 

    if (DEBUG):
        print(f"k = -1")
    return False, -1
    pass


def save_data_is_contained_next_for_illustrators(illutrator_list, sort_type, check_subject, app_name):
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

        # チェックするのがトーンの場合バリエーション毎にチェック
        if (check_subject == "tone"):
            target_dir = f'src/color_recommendation/data/output/recommend_{check_subject}s/'  # 調べたいパスに変更
            dir_names = [d for d in os.listdir(target_dir) if os.path.isdir(os.path.join(target_dir, d))]
            print(dir_names)

            for dir_name in dir_names:
                input_file_path = f"src/color_recommendation/data/output/recommend_{check_subject}s/{dir_name}/sort_by_{sort_type}/recommend_{check_subject}s_{illutrator_name}.json"
                recommended_colors_data = get_json_data(input_file_path)

                is_contained_next_color_data = check_data_is_contained_next(recommended_colors_data, check_subject)
                output_dir_path = f"src/color_recommendation/data/output/is_contained_next_{check_subject}/{dir_name}/{sort_type}"
                output_file_path = f"{output_dir_path}/is_contained_next_{check_subject}_{illutrator_name}.json"
                save_json_data(is_contained_next_color_data, output_dir_path, output_file_path)
        
        elif (check_subject == "hue_existing_apps") or (check_subject == "tone_existing_apps") or (check_subject == "color_existing_apps"):
            input_file_path = f"src/color_recommendation/data/output/recommend_{check_subject}s/sort_by_{sort_type}/recommend_{check_subject}s_{illutrator_name}_{app_name}.json"
            recommended_colors_data = get_json_data(input_file_path)

            is_contained_next_color_data = check_data_is_contained_next(recommended_colors_data, check_subject)
            output_dir_path = f"src/color_recommendation/data/output/is_contained_next_{check_subject}/{sort_type}"
            output_file_path = f"{output_dir_path}/is_contained_next_{check_subject}_{illutrator_name}_{app_name}.json"
            save_json_data(is_contained_next_color_data, output_dir_path, output_file_path)
        else:
            input_file_path = f"src/color_recommendation/data/output/recommend_{check_subject}s/sort_by_{sort_type}/recommend_{check_subject}s_{illutrator_name}.json"
            recommended_colors_data = get_json_data(input_file_path)

            is_contained_next_color_data = check_data_is_contained_next(recommended_colors_data, check_subject)
            output_dir_path = f"src/color_recommendation/data/output/is_contained_next_{check_subject}/{sort_type}"
            output_file_path = f"{output_dir_path}/is_contained_next_{check_subject}_{illutrator_name}.json"
            save_json_data(is_contained_next_color_data, output_dir_path, output_file_path)


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

        used_color_scheme_data = illust_data["color_scheme"]
        recommend_color_schemes = illust_data["recommend_color_schemes"]
        
        if(DEBUG):
            print("used color scheme: ", end="")
            # print_color_scheme(color_scheme)
            for used_color_data in used_color_scheme_data:
                used_color_hex = used_color_data["color"]
                used_color_rgb = hex_to_rgb(used_color_hex)
                print_colored_text("■ ", used_color_rgb)
            print("")
            # print_color_schemes(recommend_color_schemes)

        recall_at_k_per_illust = []

        # 次の色が含まれているかどうかの判定
        for i in range(1, len(used_color_scheme_data)):
            
            next_color = used_color_scheme_data[i]["color"]
            
            if (DEBUG):
                print(f"\n=== {illust_count+1} 枚目のイラストの {i+1} 番目の使用色 (", end="")
                print_colored_text('■', hex_to_rgb(next_color))
                print(") ============")
                

            

            # 次の色が含まれているかどうかを判定
            if (check_subject == "color"):
                is_contained, scheme_index = is_contained_color(next_color, recommend_color_schemes)
            elif (check_subject == "hue"):
                is_contained, scheme_index = is_contained_hue(next_color, recommend_color_schemes)
            elif (check_subject == "hue_existing_apps"):
                is_contained, scheme_index = is_contained_hue(next_color, recommend_color_schemes)
            elif (check_subject == "tone_existing_apps"):
                is_contained, scheme_index = is_contained_next_tone(next_color, recommend_color_schemes)
            elif (check_subject == "color_existing_apps"):
                is_contained, scheme_index = is_contained_color(next_color, recommend_color_schemes)
            elif (check_subject == "tone"):
                is_contained, scheme_index = is_contained_next_tone(next_color, recommend_color_schemes)
            else:
                print(f"check_subjectの値が不正です. check_subject: {check_subject}")

            # recall@kのデータの作成
            is_contained_data = {
                "next_color_index": i + 1,
                "k": scheme_index,
                "is_contained_next_color": is_contained
            }
            recall_at_k_per_illust.append(is_contained_data)

        data_recall_at_k_per_illust = {
            "illust_name": illust_data["illust_name"],
            "recommendations_count": len(recommend_color_schemes),
            "recall_at_k": recall_at_k_per_illust,
        }
        data_recall_at_k.append(data_recall_at_k_per_illust)

        illust_count += 1

    return data_recall_at_k
