# from estimate_used_color_scheme import estimate_used_color_scheme, rgb_to_hex
# from config.constants_dev import load_directory_path
import json
import numpy as np
import os
from PIL import Image
from collections import Counter
from .helpers.transform_color import rgb_to_hsl, rgb_to_hex
from utils.helpers.color_utils import print_colored_text, calculate_color_difference_delta_e_cie2000
# from src.color_recommendation.config.constants import SATURATION_LOWER_LIMIT, LIGHTNESS_UPPER_LIMIT, LIGHTNESS_LOWER_LIMIT

# 使用した配色として判定する閾値
SATURATION_LOWER_LIMIT = 10
LIGHTNESS_UPPER_LIMIT = 90
LIGHTNESS_LOWER_LIMIT = 10
IS_PRINT_COLOR_SCHEME_BEFORE_MEREGED = True


# 読み込まれた画像の使用配色を推定する関数
def estimate_used_color_scheme(image_path):
    image = Image.open(image_path)

    width, height = image.size
    pixel_count = width * height

    print("\n")
    print(f"loading {image_path}")

    image = image.convert('RGB')  # 画像をRGBに変換
    pixels = list(image.getdata())  # 画像のピクセルデータを取得
    color_counter = Counter(pixels)  # カラーコードとその出現回数をカウント

    used_color_schemes = []  # 使用した配色を保存する変数の初期化

    # 配色(カラーコードと出現回数)を計測
    for color, count in color_counter.most_common():
        hsl = rgb_to_hsl(color)
        saturation = hsl[1]
        rate = (100 * count / pixel_count)

        if (rate >= 0.3):
            # if (count >= 10000):
            used_color_schemes.append([color, rate])

            # 確認用出力
            if (IS_PRINT_COLOR_SCHEME_BEFORE_MEREGED):
                print_colored_text("■■■■■■■■■■■■", color)
                # print(f'Rate: {round(100*count/pixel_count)}%, Count: {count}, ColorCode: {rgb_to_hex(color)}, RGB: {color}, HSL: {rgb_to_hsl(color)}')
                print(f'Rate: {round(10*rate)/10}%, ColorCode: {rgb_to_hex(color)}, RGB: {color}, HSL: {rgb_to_hsl(color)}')

    # 配色の中で同じ色を結合して保存
    merged_used_color_schemes = merge_similar_color(used_color_schemes, 5)

    # 出現回数が多い順でソート([i][1] の要素で降順にソート)
    merged_used_color_schemes = sorted(merged_used_color_schemes, key=lambda x: x[1], reverse=True)

    # 先頭の色の彩度が20以下であるのを避けて要素を移動
    # merged_used_color_schemes = rotate_avoid_is_head_achromatic(merged_used_color_schemes)

    # 彩度が10以下または明度が10以下，90以上の色を削除
    merged_used_color_schemes = delete_achromatic(merged_used_color_schemes)

    # 確認用出力
    if (IS_PRINT_COLOR_SCHEME_BEFORE_MEREGED):
        print("------ ↓ ------")
    for color, rate in merged_used_color_schemes:
        print_colored_text("■■■■■■■■■■■■", color)
        # print(f'Rate: {round(100*count/pixel_count)}%, Count: {count}, ColorCode: {rgb_to_hex(color)}, RGB: {color}, HSL: {rgb_to_hsl(color)}')
        print(f'Rate: {round(10*rate)/10}%, ColorCode: {rgb_to_hex(color)}, RGB: {color}, HSL: {rgb_to_hsl(color)}')

    return merged_used_color_schemes


# 彩度が閾値以下である色を削除する関数
def delete_achromatic(color_scheme):

    # color[0]: rgb
    color_scheme = [color for color in color_scheme if rgb_to_hsl(color[0])[1] > SATURATION_LOWER_LIMIT]
    color_scheme = [color for color in color_scheme if rgb_to_hsl(color[0])[2] > LIGHTNESS_LOWER_LIMIT]
    color_scheme = [color for color in color_scheme if rgb_to_hsl(color[0])[2] < LIGHTNESS_UPPER_LIMIT]

    return color_scheme


# 先頭の色の彩度が20以下であるのを避けて要素を移動させる関数
def rotate_avoid_is_head_achromatic(color_scheme):
    is_all_achromatic = True
    for color in color_scheme:
        color_hsl = rgb_to_hsl(color[0])
        if (color_hsl[1] > 20):
            is_all_achromatic = False
    # すべての色が無彩色と判定された場合
    if (is_all_achromatic):
        return color_scheme

    head_color = rgb_to_hsl(color_scheme[0][0])
    head_saturation = head_color[1]

    while (head_saturation <= 20):
        print(f"saturation: {head_saturation}")
        color_scheme.append(color_scheme.pop(0))
        head_color = rgb_to_hsl(color_scheme[0][0])
        head_saturation = head_color[1]

    # print(f"color_scheme = {color_scheme}")
    return color_scheme


# 使用配色のうちΔE値が5以下の色を結合する関数
def merge_similar_color(color_scheme, threshold):
    merged_colors = []  # 結合する色を保存する配列を初期化

    # 配色がある限り色を結合
    while len(color_scheme) > 0:
        base_color = color_scheme[0]  # 先頭の色をベースカラーに代入
        to_merge = [base_color]
        color_scheme = color_scheme[1:]

        # 先頭の色と先頭以外の色でΔEが閾値以下の場合があるかどうかの探索
        for i in range(len(color_scheme) - 1, -1, -1):  # 最後尾([len(~)-1])からから先頭([-1])まで検索

            # 先頭の色とi番目の色が同じ色だった場合
            if calculate_color_difference_delta_e_cie2000(base_color[0], color_scheme[i][0]) <= threshold:
                to_merge.append(color_scheme[i])  # 結合する色を保存するスロットにi番目の色を追加
                color_scheme.pop(i)  # 結合されるi番目の色を削除

        # 色の加重平均と合算された出現回数を色を結合する配列に追加
        merge_color_total_count = sum([color[1] for color in to_merge])  # 出現回数の合算
        merge_color_rgb = np.average([color[0] for color in to_merge], axis=0, weights=[color[1] for color in to_merge])
        merge_color_rgb = np.round(merge_color_rgb).astype(int)
        merged_colors.append([merge_color_rgb, merge_color_total_count])
    return merged_colors


# 読込んだイラストの使用配色をjson形式で保存する関数
def generate_json_used_color_scheme(image_path):
    used_color_schemes = estimate_used_color_scheme(image_path)
    # print(f"used_color_schemes = { used_color_schemes}")

    # JSON用のリストを作成
    json_data = []
    for color_scheme in used_color_schemes:
        hex = rgb_to_hex(color_scheme[0].tolist())
        color_dict = {
            "color": hex,  # NumPy配列をリストに変換
            "rate": round(10 * color_scheme[1]) / 1000,
            "amount": -1
        }
        json_data.append(color_dict)

    if (len(json_data) >= 1):
        first_element = {
            "illustName": image_path,
            "color": json_data[0]["color"],
            "rate": json_data[0]["rate"],
            "amount": -1
        }

        json_data = [first_element] + json_data[1:]

    json_string = json.dumps(json_data, indent=4)  # JSON文字列に変換
    # print(json_string)  # 結果のJSON文字列を表示
    # print(json_data)  # 結果のJSON文字列を表示
    return json_data


def save_json_used_color_scheme(illustrater_name):
    json_data = []

    load_directory_path = f'src/color_recommendation/data/input/illustration/{illustrater_name}'
    # directory_path = 'tmp/estimate_used_color_scheme/data/input/gaako/'
    # jpg_files = [file for file in os.listdir(directory_path) if file.endswith('.jpg')]  # .jpgファイルの名前をすべて配列に保存
    # .jpgファイルと.pngファイルの名前を同じ配列に保存
    image_files = [file for file in os.listdir(load_directory_path) if file.endswith('.jpg')] + [file for file in os.listdir(load_directory_path) if file.endswith('.png')]

    print(image_files)

    for file_name in image_files:
        add_json_data = generate_json_used_color_scheme(f"{load_directory_path}/{file_name}")
        json_data.append(add_json_data)

    # print(json_data)

    file_path = f'src/color_recommendation/data/input/used_colors_{illustrater_name}.json'
    with open(file_path, 'w') as json_file:
        json.dump(json_data, json_file, indent=4)

    print(f"JSONデータが '{file_path}' に保存されました。")
    return json_data


def main():
    print("hello world")
    # generate_json_used_color_scheme("src/color_recommendation/data/input/illustration/sample/sample_input.jpg")


if __name__ == "__main__":
    main()
