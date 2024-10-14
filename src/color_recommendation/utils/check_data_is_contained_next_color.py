from utils.helpers.color_utils import calculate_color_difference_delta_e_cie2000, print_colored_text
from utils.helpers.transform_color import hex_to_rgb

IS_PRINT_CONTAINED_NEXT_COLOR_INFO = False


def is_contained_color(next_color, color_schemes):
    for i in range(len(color_schemes)):
        # print(color_schemes[i])

        if (IS_PRINT_CONTAINED_NEXT_COLOR_INFO):
            print(f"--- {i+1} 配色目 -------------")

        for j in range(len(color_schemes[i])):
            recommend_color = color_schemes[i][j]["color"]
            # print(recommend_color)

            diff = calculate_color_difference_delta_e_cie2000(hex_to_rgb(next_color), hex_to_rgb(recommend_color))

            if (IS_PRINT_CONTAINED_NEXT_COLOR_INFO):
                print("next_color: ", end="")
                print_colored_text("■ ", hex_to_rgb(next_color))
                print(", recommend_color: ", end="")
                print_colored_text("■", hex_to_rgb(recommend_color))
                print(f", delta_e = {diff}")

            if (diff <= 20):
                return True, i

    return False, -1


def check_data_is_contained_next_color(data):
    illust_count = 0
    for illust_data in data:

        # 空のデータを読み飛ばし
        if not illust_data:
            continue

        color_scheme = illust_data["color_scheme"]
        recommend_color_schemes = illust_data["recommend_color_schemes"]

        # 次の色が含まれているかどうかの判定
        for i in range(len(color_scheme) - 1):

            if (IS_PRINT_CONTAINED_NEXY_COLOR_INFO):
                print(f"\n=== {illust_count+1} 枚目のイラストの {i+1} 色目 ============")

            # corrent_color = color_scheme[i]["color"]
            next_color = color_scheme[i + 1]["color"]

            # print(f"corrent_color: {corrent_color}, next_color: {next_color}")
            is_contained, scheme_index = is_contained_color(next_color, recommend_color_schemes)
            print(f"is_contained: {is_contained}, scheme_index: {scheme_index}")

        # print(illust_data)
        illust_count += 1
