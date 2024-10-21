import json
from utils.generate_color_scheme_method import generate_all_color_schemes
from utils.add_variations_color_scheme import add_all_variations_color_schemes
from utils.helpers.color_utils import print_colored_text, print_color_schemes
from utils.helpers.transform_color import hex_to_rgb, transform_color_schemes_rgb_to_hex
from utils.helpers.json_utils import convert_color_schemes_to_color_data
from utils.check_data_is_contained_next_color import check_data_is_contained_next_color
from utils.plot_graph import plot_recall_at_k


def read_file(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
        print(f"{file_path} が読み込まれました．")
        return data


def generate_recommend_colors(data):

    output_data = []

    # print(data)
    for illust_data in data:

        # 空のデータを読み飛ばし
        if not illust_data:
            continue

        # あるイラストに対して推薦配色群を生成
        # print(illust_data[0]["illustName"])
        base_color_rgb = hex_to_rgb(illust_data[0]['color'])
        recommend_color_schemes = generate_all_color_schemes(base_color_rgb)
        recommend_color_schemes = add_all_variations_color_schemes(recommend_color_schemes)
        # print_color_schemes(recommend_color_schemes)

        # recommend_color_schemes_hex = transform_color_schemes_rgb_to_hex(recommend_color_schemes)
        # print(recommend_color_schemes_hex)recommend_color_schemes_hex, recommendations

        new_illust_data = {
            "illust_name": illust_data[0]['illustName'],
            "color_scheme": illust_data,
            # "recommend_color_schemes_rgb": recommend_color_schemes,
            "recommend_color_schemes": convert_color_schemes_to_color_data(transform_color_schemes_rgb_to_hex(recommend_color_schemes)),
        }

        # print(new_illust_data)
        output_data.append(new_illust_data)

    # print(output_data)

    return output_data


def run_all(file_name):
    print(f"=== {file_name} ====================")

    # イラストデータの読み込み
    USED_COLORS_FILE_PATH = f"src/color_recommendation/data/input/used_colors_{file_name}.json"
    used_colors_data = read_file(USED_COLORS_FILE_PATH)

    # 推薦配色群の生成
    recommend_colors_data = generate_recommend_colors(used_colors_data)
    RECOMMEND_COLORS_FILE_PATH = f"src/color_recommendation/data/output/recommend_colors_{file_name}.json"
    with open(RECOMMEND_COLORS_FILE_PATH, 'w', encoding='utf-8') as file:
        json.dump(recommend_colors_data, file, ensure_ascii=False, indent=4)
        print(f"{RECOMMEND_COLORS_FILE_PATH} が保存されました．")

    # 次の色が含まれているかどうかの判定とデータの作成
    is_contained_next_color_data = check_data_is_contained_next_color(recommend_colors_data)
    IS_CONTAINED_NEXT_COLOR_FILE_PATH = f"src/color_recommendation/data/output/is_contained_next_color_{file_name}.json"
    with open(IS_CONTAINED_NEXT_COLOR_FILE_PATH, 'w', encoding='utf-8') as file:
        json.dump(is_contained_next_color_data, file, ensure_ascii=False, indent=4)
        print(f"{IS_CONTAINED_NEXT_COLOR_FILE_PATH} が保存されました．")

    # グラフの生成
    GRAPH_PATH = f'src/color_recommendation/data/output/recall_at_k_{file_name}.png'
    plot_recall_at_k(IS_CONTAINED_NEXT_COLOR_FILE_PATH, GRAPH_PATH)

    print("")


def main():
    # all_run("src/color_recommendation/data/input/test_input_real_data.json", 'src/color_recommendation/data/output/test_recall_at_k.png')
    # all_run("sample")
    run_all("gaako")
    run_all("no_copyright_girl")
    run_all("yoshi_mi_yoshi")


if __name__ == '__main__':
    main()
