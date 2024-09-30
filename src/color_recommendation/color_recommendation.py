import json


def read_file(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
        return data


def generate_recommend_colors(base_color):

    colors = [
        base_color,
        (0, 0, 0),
        (255, 255, 255)
    ]
    return colors


def main():
    FILE_PATH = "src/color_recommendation/data/input/test_input.json"
    data = read_file(FILE_PATH)
    print(f'data:', data)

    colors = generate_recommend_colors((255, 0, 0))
    print(f'colors:', colors)


if __name__ == '__main__':
    main()
