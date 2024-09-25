import json


def read_file(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
        return data


def main():
    FILE_PATH = "src/color_recommendation/data/input/test_input.json"
    data = read_file(FILE_PATH)
    print(f'data:', data)


if __name__ == '__main__':
    main()
