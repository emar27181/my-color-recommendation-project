import json
from utils.generate_color_scheme_method import generate_all_color_schemes
from utils.add_variations_color_scheme import add_all_variations_color_schemes
from utils.helpers.color_utils import print_colored_text, print_color_schemes
from utils.helpers.transform_color import hex_to_rgb, transform_color_schemes_rgb_to_hex
from utils.helpers.json_utils import convert_color_schemes_to_color_data
from utils.check_data_is_contained_next_color import check_data_is_contained_next_color


def read_file(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
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


def main():
    # イラストデータの読み込み
    INPUT_FILE_PATH = "src/color_recommendation/data/input/test_input_simple_data.json"
    # INPUT_FILE_PATH = "src/color_recommendation/data/input/test_input_real_data.json"
    input_data = read_file(INPUT_FILE_PATH)

    # 推薦配色群の生成
    output_data = generate_recommend_colors(input_data)
    OUTPUT_FILE_PATH = "src/color_recommendation/data/output/test_output_simple_data.json"
    with open(OUTPUT_FILE_PATH, 'w', encoding='utf-8') as file:
        json.dump(output_data, file, ensure_ascii=False, indent=4)

    # 推薦配色群の読み込み
    RECOMMENDED_FILE_PATH = "src/color_recommendation/data/output/test_output_simple_data.json"
    recommended_data = read_file(RECOMMENDED_FILE_PATH)

    # 次の色が含まれているかどうかの判定
    is_contained_next_color_data = check_data_is_contained_next_color(recommended_data)
    IS_CONTAINED_NEXT_COLOR_FILE_PATH = "src/color_recommendation/data/output/test_is_contained_next_color_simple_data.json"
    with open(IS_CONTAINED_NEXT_COLOR_FILE_PATH, 'w', encoding='utf-8') as file:
        json.dump(is_contained_next_color_data, file, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    main()
