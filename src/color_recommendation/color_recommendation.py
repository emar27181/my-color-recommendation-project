import json
from utils.generate_color_scheme_method import generate_all_color_schemes
from utils.add_variations_color_scheme import add_all_variations_color_schemes
from utils.helpers.color_utils import print_colored_text, print_color_schemes
from utils.helpers.transform_color import hex_to_rgb


def read_file(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
        return data


def generate_recommend_colors(data):

    # print(data)
    for illust_data in data:
        print(illust_data)
        base_color_rgb = hex_to_rgb(illust_data[0]['color'])
        recommend_color_schemes = generate_all_color_schemes(base_color_rgb)
        recommend_color_schemes = add_all_variations_color_schemes(recommend_color_schemes)
        print_color_schemes(recommend_color_schemes)

        """
        for color_data in illust_data:
            color = color_data['color']
            print_colored_text("■ ", hex_to_rgb(color))
            print(color)
        """

    return ("test output")


def main():
    FILE_PATH = "src/color_recommendation/data/input/test_input_simple_data.json"
    data = read_file(FILE_PATH)
    # print(f'data:', data)

    generate_recommend_colors(data)

    # colors = generate_recommend_colors((255, 0, 0))
    # print(f'colors:', colors)


if __name__ == '__main__':
    main()
