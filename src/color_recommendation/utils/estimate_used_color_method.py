import json


def estimate_used_color_scheme(illustrator):
    """あるイラストレーターが使っている配色技法を推定する関数
    """
    print(f"=== {illustrator} =================================")

    with open(f"src/color_recommendation/data/input/used_colors/used_colors_{illustrator}.json", "r") as f:
        data = json.load(f)

    print(data)


if __name__ == '__main__':
    estimate_used_color_scheme('test')
