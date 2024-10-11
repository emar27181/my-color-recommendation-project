from utils.helpers.color_utils import calculate_color_difference_delta_e_cie2000, print_colored_text
from utils.helpers.transform_color import hex_to_rgb


def is_contained_color(next_color, color_schemes):
    for i in range(len(color_schemes)):
        # print(color_schemes[i])

        for j in range(len(color_schemes[i])):
            recommend_color = color_schemes[i][j]["color"]
            # print(recommend_color)

            print("next_color: ", end="")
            print_colored_text("■ ", hex_to_rgb(next_color))
            print(", recommend_color: ", end="")
            print_colored_text("■", hex_to_rgb(recommend_color))

            print(", delta_e = ", end="")
            print(calculate_color_difference_delta_e_cie2000(hex_to_rgb(next_color), hex_to_rgb(recommend_color)))


def check_data_is_contained_next_color(data):
    for illust_data in data:

        # 空のデータを読み飛ばし
        if not illust_data:
            continue

        color_scheme = illust_data["color_scheme"]
        recommend_color_schemes = illust_data["recommend_color_schemes"]

        # 次の色が含まれているかどうかの判定
        for i in range(len(color_scheme) - 1):
            corrent_color = color_scheme[i]["color"]
            next_color = color_scheme[i + 1]["color"]

            print(f"corrent_color: {corrent_color}, next_color: {next_color}")
            is_contained_color(next_color, recommend_color_schemes)
