import json
from utils.generate_color_scheme_method import generate_all_color_schemes
from utils.add_variations_color_scheme import add_all_variations_color_schemes
from utils.helpers.color_utils import print_colored_text, print_color_schemes, print_color_scheme
from utils.helpers.transform_color import hex_to_rgb, transform_color_schemes_rgb_to_hex
from utils.helpers.json_utils import convert_color_schemes_to_color_data
from utils.check_data_is_contained_next_color import check_data_is_contained_next_color
from utils.plot_graph import plot_recall_at_k
from utils.estimate_used_color_scheme import generate_json_used_color_scheme, save_estimated_used_colors
from utils.download_instagram_images import download_instagram_images
from utils.sort_color_scheme import sort_color_scheme_by_color_difference, shuffle_color_schemes, sort_color_scheme_by_used_trend
import os


def read_file(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
        print(f"{file_path} が読み込まれました．")
        return data


def generate_recommend_colors(data, sort_type, illustrator_name):

    output_data = []

    # print(data)
    for illust_data in data:

        # 空のデータを読み飛ばし
        if not illust_data:
            continue

        print(f"=== {illust_data[0]['illustName']} =================== ")

        # 使用配色のRGB形式のリストを取得
        used_color_scheme_rgb = []
        for color_scheme_data in illust_data:
            used_color_scheme_rgb.append(hex_to_rgb(color_scheme_data['color']))

        # あるイラストに対して推薦配色群を生成
        base_color_rgb = hex_to_rgb(illust_data[0]['color'])  # 推薦配色の基となる色を取得
        recommend_color_schemes_rgb = generate_all_color_schemes(base_color_rgb)  # 17(?)パターンの配色群を生成
        recommend_color_schemes_rgb = add_all_variations_color_schemes(recommend_color_schemes_rgb)  # 明度の異なる2パターンの配色群を追加

        if (sort_type == "color_diff"):
            recommend_color_schemes_rgb = sort_color_scheme_by_color_difference(used_color_scheme_rgb, recommend_color_schemes_rgb)  # 使用配色との類似度順にソート
        elif (sort_type == "random"):
            recommend_color_schemes_rgb = shuffle_color_schemes(recommend_color_schemes_rgb)  # 推薦配色をランダムにシャッフル
        elif (sort_type == "used_trend"):
            recommend_color_schemes_rgb = sort_color_scheme_by_used_trend(recommend_color_schemes_rgb, illustrator_name)
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
        for i in range(len(recommend_color_schemes_rgb)):
            print(f"[{i}]: ", end="")
            print_color_scheme(recommend_color_schemes_rgb[i])

        # print(new_illust_data)
        output_data.append(new_illust_data)

    # print(output_data)

    return output_data


def save_recommend_colors_for_illustrators(illutrator_list, sort_type):
    """
    引数で受け取るリスト内のイラストレーターのイラストの推薦配色を保存する関数

    引数:
        illutrater_list: 推薦配色を生成させたいイラストレーターのリスト(文字列)
        sort_type: ソートの種類(random/color_diff)
    戻り値:
        None
    """

    for illustrator_name in illutrator_list:
        print(f"=== {illustrator_name} ====================")

        input_file_path = f"src/color_recommendation/data/input/used_colors/used_colors_{illustrator_name}.json"
        used_colors_data = read_file(input_file_path)

        recommend_colors_data = generate_recommend_colors(used_colors_data, sort_type, illustrator_name)
        # 推薦配色の生成と推薦配色のソートを別処理にした方が分かりやすいかも
        output_file_path = f"src/color_recommendation/data/output/recommend_colors/sort_by_{sort_type}/recommend_colors_{illustrator_name}.json"

        with open(output_file_path, 'w', encoding='utf-8') as file:
            json.dump(recommend_colors_data, file, ensure_ascii=False, indent=4)
            print(f"{output_file_path} が保存されました．(推薦配色群の生成)")


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
