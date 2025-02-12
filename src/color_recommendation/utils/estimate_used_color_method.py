import json
from utils.helpers.color_utils import print_colored_text
from utils.helpers.transform_color import hex_to_rgb, rgb_to_hsl


def print_hues_data(hues):
    for hue_data in hues:
        print(f"{hue_data[0]}: {round(hue_data[1]*100)/100}")


def estimate_used_color_method_by_illustrator(illustrator):
    """あるイラストレーターが使っている配色技法を推定する関数
    """
    print(f"=== {illustrator} =================================")

    with open(f"src/color_recommendation/data/input/used_colors/used_colors_{illustrator}.json", "r") as f:
        data = json.load(f)

    for illust_data in data:
        illust_name = illust_data[0]['illustName']
        print(f"=== {illust_name} ================")

        # 色相とその出現割合の計測
        hues = []  # 色相とその出現割合を保存する変数
        for color_data in illust_data:
            color_hex = color_data['color']
            color_rgb = hex_to_rgb(color_hex)
            color_hsl = rgb_to_hsl(color_rgb)
            used_rate = color_data['rate']

            # print(f"{color_hsl[0]}: {used_rate} ")
            # print_colored_text("■", color_rgb)
            # print(f"({color_hsl[0]}): {used_rate}  {color_hsl}")
            hues.append([color_hsl[0], used_rate])
        print(hues)


if __name__ == '__main__':
    pass
    # estimate_used_color_scheme('test')
