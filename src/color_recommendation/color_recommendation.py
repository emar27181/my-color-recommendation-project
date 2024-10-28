import json
from utils.generate_color_scheme_method import generate_all_color_schemes
from utils.add_variations_color_scheme import add_all_variations_color_schemes
from utils.helpers.color_utils import print_colored_text, print_color_schemes
from utils.helpers.transform_color import hex_to_rgb, transform_color_schemes_rgb_to_hex
from utils.helpers.json_utils import convert_color_schemes_to_color_data
from utils.check_data_is_contained_next_color import check_data_is_contained_next_color
from utils.plot_graph import plot_recall_at_k
from utils.estimate_used_color_scheme import generate_json_used_color_scheme, save_estimated_used_colors
from utils.download_instagram_images import download_instagram_images


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


def run_all(file_name, illust_count_limit):
    print(f"=== {file_name} ====================")

    download_instagram_images(file_name, illust_count_limit)
    print(f"@{file_name} の投稿がダウンロードされました．")

    # 使用色の抽出と保存
    save_estimated_used_colors(file_name, illust_count_limit)
    print("使用色が抽出されました．")

    # イラストデータの読み込み
    USED_COLORS_FILE_PATH = f"src/color_recommendation/data/input/used_colors_{file_name}.json"
    used_colors_data = read_file(USED_COLORS_FILE_PATH)

    # 推薦配色群の生成
    recommend_colors_data = generate_recommend_colors(used_colors_data)
    RECOMMEND_COLORS_FILE_PATH = f"src/color_recommendation/data/output/recommend_colors_{file_name}.json"
    with open(RECOMMEND_COLORS_FILE_PATH, 'w', encoding='utf-8') as file:
        json.dump(recommend_colors_data, file, ensure_ascii=False, indent=4)
        print(f"{RECOMMEND_COLORS_FILE_PATH} が保存されました．(推薦配色群の生成)")

    # 次の色が含まれているかどうかの判定とデータの作成
    is_contained_next_color_data = check_data_is_contained_next_color(recommend_colors_data)
    IS_CONTAINED_NEXT_COLOR_FILE_PATH = f"src/color_recommendation/data/output/is_contained_next_color_{file_name}.json"
    with open(IS_CONTAINED_NEXT_COLOR_FILE_PATH, 'w', encoding='utf-8') as file:
        json.dump(is_contained_next_color_data, file, ensure_ascii=False, indent=4)
        print(f"{IS_CONTAINED_NEXT_COLOR_FILE_PATH} が保存されました．(次の色が含まれているかどうかを保存するデータの作成)")

    # グラフの生成
    GRAPH_PATH = f'src/color_recommendation/data/output/recall_at_k_{file_name}.png'
    print(f"{IS_CONTAINED_NEXT_COLOR_FILE_PATH} が読み込まれました．")
    plot_recall_at_k(IS_CONTAINED_NEXT_COLOR_FILE_PATH, GRAPH_PATH)
    print(f"{GRAPH_PATH} が保存されました．(グラフの作成)")

    print("")


def main():
    # all_run("src/color_recommendation/data/input/test_input_real_data.json", 'src/color_recommendation/data/output/test_recall_at_k.png')
    # all_run("sample")
    # run_all("gaako")
    # run_all("no_copyright_girl")
    # run_all("yoshi_mi_yoshi")

    # save_json_used_color_scheme("sample")
    # generate_json_used_color_scheme("src/color_recommendation/data/input/illustration/sample/sample_input.jpg")
    # download_instagram_images("sa_ka_na_4")
    # run_all("trcoot", 100)
    # run_all("mokmok_skd", 100)
    # run_all("nest_virgo", 100)
    # run_all("oz_yarimasu", 100)

    save_estimated_used_colors("mokmok_skd", 100)


if __name__ == '__main__':
    main()
