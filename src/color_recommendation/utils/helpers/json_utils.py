import json
import os


def convert_color_schemes_to_color_data(color_schemes):
    output_color_data = []

    for color_scheme in color_schemes:
        # print(color_scheme)
        new_color_scheme = []

        for color in color_scheme:
            new_color_data = {
                "color": color,
                "rate": -1
            }
            # print(new_color_data)
            new_color_scheme.append(new_color_data)
            # print(color_scheme_methods)

        output_color_data.append(new_color_scheme)

    # print(output_color_data)

    return (output_color_data)


def get_json_length(file_path):
    with open(file_path, 'r') as json_file:
        json_data = json.load(json_file)

    return (len(json_data))


def get_json_data(file_path):
    """ 引数で受け取るパスのjsonファイルを読み込み，データを返す関数

    引数:
        file_path: jsonファイルのパス

    戻り値:
        data: jsonファイルのデータ
    """

    # ファイルの読み込み
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            return []

        with open(file_path, 'r') as f:
            data = json.load(f)
            print(f"{file_path} が正常に読み込まれました．")
            return data
    except FileNotFoundError as e:
        print(f"エラー: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"JSONデコードエラー: {e}. ファイルの内容を確認してください。")
        return []
    except Exception as e:
        print(f"予期しないエラーが発生しました: {e}")
        return []


def save_json_data(data, output_dir_path, output_file_path):
    """ 引数で受け取るパスにjsonファイルを保存する関数

    引数:
        output_dir_path:
        output_file_path: jsonファイルのパス
        data: 保存するデータ
    """

    # 推薦配色群の保存
    if not os.path.exists(os.path.dirname(output_file_path)):
        os.makedirs(output_dir_path)
        print(f"{output_dir_path} ディレクトリが作成されました．")

    with open(output_file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"{output_file_path} が保存されました．")


def get_dir_list(dir_path):
    """ 引数で受け取るパスのディレクトリ下のディレクトリ名をリストで返す関数
    """
    dir_list = [d for d in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, d))]
    return dir_list
