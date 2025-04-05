from utils.helpers.json_utils import get_json_data


def _extract_statistics_by_illustrator(illustrator_name):
    """ イラストレーターの統計データを抽出する関数

    引数:
        illustrator_name: イラストレーターの名前(文字列)

    戻り値:
        statistics: イラストレーターの統計データ
    """

    input_file_path = f"src/color_recommendation/data/input/used_hues/used_hues_{illustrator_name}.json"
    data = get_json_data(input_file_path)

    print(f"data = {data}")
    statistics = []

    return statistics


def save_statistics_for_illustrators(illustrator_list):
    """ 引数で受け取るイラストレーターのイラストの統計データを保存する関数

    引数:
        illustrater_list: 推薦配色を生成させたいイラストレーターのリスト(文字列)

    戻り値:
        None
    """

    for illustrator_name in illustrator_list:
        print(f"=== {illustrator_name} ========================")

        statistics = _extract_statistics_by_illustrator(illustrator_name)
