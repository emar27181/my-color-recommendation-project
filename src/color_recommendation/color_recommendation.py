import json
from utils.generate_color_scheme_method import generate_all_color_schemes, remove_duplicated_color_from_color_schemes, remove_monochrome_color_from_color_schemes, generate_one_color_schemes, remove_empty_color_scheme_from_color_schemes
from utils.add_variations_color_scheme import get_variations_for_color_schemes
from utils.helpers.color_utils import print_colored_text, print_color_schemes, print_color_scheme, print_color_schemes_info
from utils.helpers.transform_color import hex_to_rgb, transform_color_schemes_rgb_to_hex
from utils.helpers.json_utils import convert_color_schemes_to_color_data, save_json_data, print_tmp, get_json_data
from utils.check_data_is_contained_next_color import check_data_is_contained_next

from utils.estimate_used_color_scheme import generate_json_used_color_scheme, save_estimated_used_colors
from utils.download_instagram_images import download_instagram_images
from utils.sort_color_scheme import sort_color_schemes_by_color_difference, shuffle_color_schemes, sort_color_schemes_by_used_color_count, sort_color_schemes_by_mean_resultant_length, sort_color_schemes_by_custom_v0, sort_color_schemes_by_used_tone
import os

DEBUG = True
DEBUG = False


def read_file(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
        print(f"{file_path} が読み込まれました．")
        return data

def get_recommendations(used_color_scheme_rgb, recommend_type, sort_type, illustrator_name, diff_values=[-40, -20, 20, 40]):
    """
    引数で受け取るデータを基に推薦群を取得する関数
    """
    print(f"=== get_recommend_recommendations(~, {recommend_type}, {sort_type}, {illustrator_name}, {diff_values}) ===")
    base_color_rgb = used_color_scheme_rgb[0]  
    
    if( recommend_type == "hue"):
        recommend_color_schemes_rgb = generate_all_color_schemes(base_color_rgb)  # 17パターンの配色群を生成
        
    elif( recommend_type == "tone"):
        recommend_base_color_schemes_rgb = generate_one_color_schemes(base_color_rgb)  # 1パターンの配色群を生成
        recommend_color_schemes_rgb = recommend_base_color_schemes_rgb.copy()

        # 重複色を削除
        # recommend_color_schemes_rgb = remove_duplicated_color_from_color_schemes(recommend_color_schemes_rgb)

        # 生成された推薦配色群に明度彩度が異なる色を追加
        for lightness_diff in diff_values:
            for saturation_diff in diff_values:
                recommend_color_schemes_rgb += get_variations_for_color_schemes(recommend_base_color_schemes_rgb, lightness_diff, saturation_diff, "saturation_and_lightness")

        # 空の配色を削除
        recommend_color_schemes_rgb = remove_empty_color_scheme_from_color_schemes(recommend_color_schemes_rgb)

        # 彩度が0になったになった色を削除
        recommend_color_schemes_rgb = remove_monochrome_color_from_color_schemes(recommend_color_schemes_rgb)

    # 推薦配色群の並び替え
    if (sort_type == "color_diff"):
        recommend_color_schemes_rgb = sort_color_schemes_by_color_difference(used_color_scheme_rgb, recommend_color_schemes_rgb)  # 使用配色との類似度順にソート
    elif (sort_type == "random"):
        recommend_color_schemes_rgb = shuffle_color_schemes(recommend_color_schemes_rgb)  # 推薦配色をランダムにシャッフル
    elif (sort_type == "used_color_count"):
        recommend_color_schemes_rgb = sort_color_schemes_by_used_color_count(recommend_color_schemes_rgb, illustrator_name)
    elif (sort_type == "mean_resultant_length"):
        recommend_color_schemes_rgb = sort_color_schemes_by_mean_resultant_length(recommend_color_schemes_rgb, illustrator_name)
    elif (sort_type == "custom_v0"):
        recommend_color_schemes_rgb = sort_color_schemes_by_custom_v0(used_color_scheme_rgb, recommend_color_schemes_rgb, illustrator_name)
    elif (sort_type == "used_tone"):
        recommend_color_schemes_rgb = sort_color_schemes_by_used_tone(recommend_color_schemes_rgb, illustrator_name)
    elif (sort_type == "no_sort"):
        pass
    else:
        print("ソートの種類が間違っているため，推薦配色は並び替えられずに挿入されます．(ソートの種類:  'random', 'color_diff')")
        
    # 確認用出力
    if (DEBUG):
        print_color_schemes_info(recommend_color_schemes_rgb)
        
    return recommend_color_schemes_rgb

def generate_recommend_hues_by_illustrator(data, sort_type, illustrator_name):

    output_data = []
    for illust_data in data:

        # 空のデータを読み飛ばし
        if not illust_data:
            continue

        print(f"=== {illust_data[0]['illustName']} =================== ")
        # 使用配色のRGB形式のリストを取得
        used_color_scheme_rgb = []
        for color_scheme_data in illust_data:
            used_color_scheme_rgb.append(hex_to_rgb(color_scheme_data['color']))

        recommend_color_schemes_rgb =  get_recommendations(used_color_scheme_rgb, "hue", sort_type, illustrator_name)  # 使用配色の最初の色を基に推薦色相を生成
        
        new_illust_data = {
            "illust_name": illust_data[0]['illustName'],
            "color_scheme": illust_data,
            "recommend_color_schemes": convert_color_schemes_to_color_data(transform_color_schemes_rgb_to_hex(recommend_color_schemes_rgb)),
        }

        output_data.append(new_illust_data)



    return output_data

def generate_recommend_hues_exising_apps_by_illustrator(data, sort_type, illustrator_name):
    """既存のカラーパレットアプリの配色を基に推薦色相を生成する関数(現時点ではclipstudioの配色を使用(2025/06/08))

    Args:
        data (_type_): _description_
        sort_type (_type_): _description_
        illustrator_name (_type_): _description_

    Returns:
        _type_: _description_
    """

    # 仮実装として，clipstudioの配色を使用
    input_file_path = "src/color_recommendation/data/output/recommend_colors/sort_by_illust_app/recommend_colors_clipstudio.json"
    json_data = get_json_data(input_file_path)
    recommend_color_schemes_data = json_data[0]['recommend_color_schemes']
    # print(f"recommend_color_schemes_data_re: {recommend_color_schemes_data_re}")

    output_data = []
    for illust_data in data:

        # 空のデータを読み飛ばし
        if not illust_data:
            continue

        print(f"=== {illust_data[0]['illustName']} =================== ")
        # 使用配色のRGB形式のリストを取得
        used_color_scheme_rgb = []
        for color_scheme_data in illust_data:
            used_color_scheme_rgb.append(hex_to_rgb(color_scheme_data['color']))
        
        new_illust_data = {
            "illust_name": illust_data[0]['illustName'],
            "color_scheme": illust_data,
            "recommend_color_schemes": recommend_color_schemes_data
        }

        output_data.append(new_illust_data)



    return output_data


def generate_recommend_tones_by_illustrator(data, sort_type, illustrator_name, diff_values):

    output_data = []
    for illust_data in data:
        if not illust_data:  # 空のデータを読み飛ばし
            continue

        print(f"=== {illust_data[0]['illustName']} =================== ")

        # 使用配色のRGB形式のリストを取得
        used_color_scheme_rgb = []
        for color_scheme_data in illust_data:
            used_color_scheme_rgb.append(hex_to_rgb(color_scheme_data['color']))

        recommend_color_schemes_rgb = get_recommendations(used_color_scheme_rgb, "tone", sort_type, illustrator_name, diff_values)  

        new_illust_data = {
            "illust_name": illust_data[0]['illustName'],
            "color_scheme": illust_data,
            "recommend_color_schemes": convert_color_schemes_to_color_data(transform_color_schemes_rgb_to_hex(recommend_color_schemes_rgb)),
        }

        output_data.append(new_illust_data)

    return output_data


def generate_recommend_colors_by_illustrator(data, sort_type, illustrator_name, diff_values):

    output_data = []
    for illust_data in data:
        if not illust_data:  # 空のデータを読み飛ばし
            continue

        print(f"=== {illust_data[0]['illustName']} =================== ")

        # 使用配色のRGB形式のリストを取得
        used_color_scheme_rgb = []
        for color_scheme_data in illust_data:
            used_color_scheme_rgb.append(hex_to_rgb(color_scheme_data['color']))

        # あるイラストに対して推薦配色群を生成
        base_color_rgb = hex_to_rgb(illust_data[0]['color'])  # 推薦配色の基となる色を取得
        recommend_base_color_schemes_rgb = generate_all_color_schemes(base_color_rgb)  # 17(?)パターンの配色群を生成
        recommend_color_schemes_rgb = recommend_base_color_schemes_rgb.copy()

        # 重複色を削除
        # recommend_color_schemes_rgb = remove_duplicated_color_from_color_schemes(recommend_color_schemes_rgb)

        # 生成された推薦配色群に明度彩度が異なる色を追加
        for lightness_diff in diff_values:
            for saturation_diff in diff_values:
                recommend_color_schemes_rgb += get_variations_for_color_schemes(recommend_base_color_schemes_rgb, lightness_diff, saturation_diff, "saturation_and_lightness")
            # recommend_color_schemes_rgb += get_variations_for_color_schemes(recommend_base_color_schemes_rgb, diff_value, "lightness")
            # recommend_color_schemes_rgb += get_variations_for_color_schemes(recommend_base_color_schemes_rgb, diff_value, "saturation")

        # 無彩色と判定された色を削除
        recommend_color_schemes_rgb = remove_monochrome_color_from_color_schemes(recommend_color_schemes_rgb)

        # 空の配色を削除
        recommend_color_schemes_rgb = remove_empty_color_scheme_from_color_schemes(recommend_color_schemes_rgb)

        # 推薦配色群の並び替え
        if (sort_type == "color_diff"):
            recommend_color_schemes_rgb = sort_color_schemes_by_color_difference(used_color_scheme_rgb, recommend_color_schemes_rgb)  # 使用配色との類似度順にソート
        elif (sort_type == "random"):
            recommend_color_schemes_rgb = shuffle_color_schemes(recommend_color_schemes_rgb)  # 推薦配色をランダムにシャッフル
        elif (sort_type == "used_color_count"):
            recommend_color_schemes_rgb = sort_color_schemes_by_used_color_count(recommend_color_schemes_rgb, illustrator_name)
        elif (sort_type == "mean_resultant_length"):
            recommend_color_schemes_rgb = sort_color_schemes_by_mean_resultant_length(recommend_color_schemes_rgb, illustrator_name)
        elif (sort_type == "custom_v0"):
            recommend_color_schemes_rgb = sort_color_schemes_by_custom_v0(used_color_scheme_rgb, recommend_color_schemes_rgb, illustrator_name)
        elif (sort_type == "no_sort"):
            pass
        else:
            print("ソートの種類が間違っているため，推薦配色は並び替えられずに挿入されます．(ソートの種類:  'random', 'color_diff')")

        new_illust_data = {
            "illust_name": illust_data[0]['illustName'],
            "color_scheme": illust_data,
            # "recommend_color_schemes": convert_color_schemes_to_color_data(transform_color_schemes_rgb_to_hex(recommend_color_schemes_rgb)),
            "recommend_color_schemes": convert_color_schemes_to_color_data(transform_color_schemes_rgb_to_hex(recommend_color_schemes_rgb)),
        }

        # 確認用出力
        if (DEBUG):
            print_color_schemes_info(recommend_color_schemes_rgb)

        output_data.append(new_illust_data)

    return output_data


def save_recommendations_for_illustrators(illutrator_list, recommend_type, sort_type, lightness_diffs):
    """
    引数で受け取るリスト内のイラストレーターのイラストの推薦配色・推薦色相・推薦トーンを保存する関数

    引数:
        illutrater_list: 推薦配色を生成させたいイラストレーターのリスト(文字列)
        recommend_type: 推薦の種類(hue/tone/color/all)
        sort_type: ソートの種類(random/color_diff/...)
        lightness_diffs: 明度の差のリスト(例: [+20, -20, +40, -40])
    戻り値:
        None
    """
    print(f"=== {sort_type} ====================")

    for illustrator_name in illutrator_list:
        print(f"=== {illustrator_name} ====================")

        input_file_path = f"src/color_recommendation/data/input/used_colors/used_colors_{illustrator_name}.json"
        output_dir_path_hues = f"src/color_recommendation/data/output/recommend_hues/sort_by_{sort_type}"
        output_file_path_hues = f"src/color_recommendation/data/output/recommend_hues/sort_by_{sort_type}/recommend_hues_{illustrator_name}.json"
        output_dir_path_colors = f"src/color_recommendation/data/output/recommend_colors/sort_by_{sort_type}"
        output_file_path_colors = f"src/color_recommendation/data/output/recommend_colors/sort_by_{sort_type}/recommend_colors_{illustrator_name}.json"

        diffs_dir_name = '[' + ','.join(str(v) for v in lightness_diffs).replace(' ', '') + ']'
        output_dir_path_tones = f"src/color_recommendation/data/output/recommend_tones/{diffs_dir_name}/sort_by_{sort_type}"
        output_file_path_tones = f"{output_dir_path_tones}/recommend_tones_{illustrator_name}.json"
        used_colors_data = read_file(input_file_path)

        # 推薦の生成と保存
        if recommend_type == "hue":
            recommend_hues_data = generate_recommend_hues_by_illustrator(used_colors_data, sort_type, illustrator_name)
            save_json_data(recommend_hues_data, output_dir_path_hues, output_file_path_hues)

        elif recommend_type == "tone":
            recommend_tones_data = generate_recommend_tones_by_illustrator(used_colors_data, sort_type, illustrator_name, lightness_diffs)
            save_json_data(recommend_tones_data, output_dir_path_tones, output_file_path_tones)

        elif recommend_type == "color":
            recommend_colors_data = generate_recommend_colors_by_illustrator(used_colors_data, sort_type, illustrator_name, lightness_diffs)
            save_json_data(recommend_colors_data, output_dir_path_colors, output_file_path_colors)
        elif recommend_type == "all":
            recommend_hues_data = generate_recommend_hues_by_illustrator(used_colors_data, sort_type, illustrator_name)
            save_json_data(recommend_hues_data, output_dir_path_hues, output_file_path_hues)
            recommend_tones_data = generate_recommend_tones_by_illustrator(used_colors_data, sort_type, illustrator_name, lightness_diffs)
            save_json_data(recommend_tones_data, output_dir_path_tones, output_file_path_tones)
            recommend_colors_data = generate_recommend_colors_by_illustrator(used_colors_data, sort_type, illustrator_name, lightness_diffs)
            save_json_data(recommend_colors_data, output_dir_path_colors, output_file_path_colors)
        elif recommend_type == "hue_existing_apps":
            print("hue_existing_appsは実装中です(2025/06/08)")
            recommend_hues_existing_apps_data = generate_recommend_hues_exising_apps_by_illustrator(used_colors_data, sort_type, illustrator_name)
            
            output_dir_path = f"src/color_recommendation/data/output/recommend_{recommend_type}s/sort_by_{sort_type}"
            output_file_path = f"src/color_recommendation/data/output/recommend_{recommend_type}s/sort_by_{sort_type}/recommend_{recommend_type}s_{illustrator_name}.json"
            save_json_data(recommend_hues_existing_apps_data, output_dir_path, output_file_path)

        else:
            print("recommend_typeの値が不正です")


def main():
    run_all("gaako_instagram", 100)
    run_all("gaako_portfolio", 100)
    run_all("mika_pikazo", 100)
    run_all("mokmok_skd", 100)
    run_all("nest_virgo", 100)
    run_all("no_copyright_girl", 100)
    run_all("omrice4869", 100)
    run_all("oz_yarimasu", 100)
    run_all("sa_ka_na_4", 100)
    run_all("trcoot", 100)


if __name__ == '__main__':
    main()
