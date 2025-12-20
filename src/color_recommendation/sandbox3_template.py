# ========================================
# 📝 このファイルについて
# ========================================
# このファイルはテンプレートファイルです。
# 使用する際は、ファイル名から「_template」を削除してください。
#
# 【使用方法】
# 1. このファイルをコピーして「sandbox3_template.py」→「sandbox3.py」にリネーム
# 2. モジュール化された最新の実験コード実行に使用
# 3. このファイル(sandbox3.py)はgitの追跡対象外なので、個人的な実験コードを安心して記述できます
#
# 【特徴】
# - エラーバー付きグラフ生成機能
# - モジュール化された処理フロー
# - 複数パラメータの組み合わせ実験
# ========================================

# 自作関数などをテスト実行を行うファイル(gitの追跡対象外)

import json
from PIL import Image
import numpy as np

from utils.download_instagram_images import download_instagram_images, download_instagram_images_for_illustrators
from utils.estimate_used_color_scheme import (
    save_estimated_used_colors, save_estimated_used_colors_for_illustrates,
    print_estimated_used_colors_for_illustrators
)
from utils.estimate_used_color_method import (
    save_estimate_used_color_method_for_illustrators
)
from utils.analyze_illustrator_statistics import (
    save_statistics_for_illustrators, get_not_monochrome_illustrator_list,
    print_statistics_for_illustrators, get_excluded_small_number_illustrator_list
)
from utils.check_data_is_contained_next_color import (
    check_data_is_contained_next, save_data_is_contained_next_for_illustrators
)
from utils.plot_graph import (
    plot_graph_3d, save_plot_recall_at_k_for_illustrators,
    save_plot_recall_at_k_with_eroor_bar_for_illustrators,
    plot_used_colors_scatter, save_plot_violin_from_used_hues_count_for_illustrators,
    save_plot_bar_from_used_achromatic_colors_average_rate_for_illustrators,
    save_plot_violin_from_used_pccs_distribution_for_illustrators,
    save_plot_violin_from_mean_resultant_length_count_for_illustrators,
    save_plot_scatter_for_illustrators, save_plot_tone_heatmap_for_illustrators,
    save_plot_recall_at_k_sort_types,
    save_plot_recall_at_k_diff_values,
    save_plot_recall_at_k_sort_types_fixed_subjects,
    PROPOSED_METHOD
)
from color_recommendation import (
    read_file, generate_recommend_colors_by_illustrator,
    save_recommendations_for_illustrators
)

def run_all(file_name, illust_count_limit):
    """単一イラストレーターの全処理実行（ダウンロード→抽出→推薦→評価→グラフ）"""
    print(f"=== {file_name} ====================")

    download_instagram_images(file_name, illust_count_limit)
    print(f"@{file_name} の投稿がダウンロードされました．")

    save_estimated_used_colors(file_name, illust_count_limit)
    print("使用色が抽出されました．")

    used_colors_data = read_file(f"src/color_recommendation/data/input/used_colors_{file_name}.json")
    recommend_colors_data = generate_recommend_colors_by_illustrator(used_colors_data)

    with open(f"src/color_recommendation/data/output/recommend_colors_{file_name}.json", 'w', encoding='utf-8') as f:
        json.dump(recommend_colors_data, f, ensure_ascii=False, indent=4)
        print("推薦配色群が保存されました．")

    is_contained_data = check_data_is_contained_next(recommend_colors_data)
    with open(f"src/color_recommendation/data/output/is_contained_next_color_{file_name}.json", 'w', encoding='utf-8') as f:
        json.dump(is_contained_data, f, ensure_ascii=False, indent=4)
        print("次の色が含まれているかの判定結果を保存しました．")

    print("recall@k グラフを保存しました．\n")

def save_and_plot_all(illustrator_list, sort_type, lightness_diffs, recommend_type, app_name, legend_location):
    """推薦配色生成・評価・グラフ描画を一括実行"""
    save_recommendations_for_illustrators(illustrator_list, recommend_type, sort_type, lightness_diffs, app_name)
    save_data_is_contained_next_for_illustrators(illustrator_list, sort_type, recommend_type, app_name)
    save_plot_recall_at_k_for_illustrators(illustrator_list, sort_type, recommend_type, app_name, legend_location)

def setup_illustrator_list(illustrator_list):
    """イラストレーターリストの前処理（モノクロ除外・少数データ除外）"""
    illustrator_list = get_not_monochrome_illustrator_list(illustrator_list)
    illustrator_list = get_excluded_small_number_illustrator_list(illustrator_list, 10)
    return illustrator_list

def main():
    DEBUG = True
    print("=== sandbox3.py ====================")

    # イラストレーターリスト定義
    illustrator_list = [
        "mika_pikazo_mpz", "harunonioikaze", "gaako_illust", "mokmok_skd",
        "nest_virgo", "omrice4869", "oz_yarimasu", "sa_ka_na_4", "trcoot",
        "birdstory_pic", "amao_1015", "meeesuke_", "shirokumaai", "tsumugitopan",
        "sexygirl.jp", "obungu_mofumofu", "skt2ing", "iina.gram", "chi_bee.official",
        "harupeipei", "bj00100", "jerome_trez_oudot", "deppa_53"
    ]
    illustrator_list = setup_illustrator_list(illustrator_list)
    # illustrator_list = ["mika_pikazo_mpz"]  # テスト用

    print(f"illustrator_list: {illustrator_list}")

    # 実験パラメータ設定
    sort_types = [
        "random",
        # "color_diff",
        "used_color_count",
        # "no_sort",
        "mean_resultant_length",
        # "custom_v0"
    ]

    recommend_types = [
        "hue",
        # "tone",
        # "color",
        # "color_existing_apps",
    ]

    diff_values = [20, -20, 40, -40, 60, -60, 80, -80]
    diff_values_list = [
        [20, -20, 40, -40],
        [20, -20, 40, -40, 60, -60, 80, -80],
        [-10, 10, -20, 20, -30, 30, -40, 40, -50, 50, -60, 60, -70, 70, -80, 80, -90, 90]
    ]

    app_names = [
        "clipstudio",
        "ibispaint",
        "medibang",
        "pixivsketch",
        "powerpoint",
        PROPOSED_METHOD
    ]
    legend_location = "lower right"

    # ===============================================================
    # 実験実行（必要に応じてコメントを外す）
    # ===============================================================

    # グラフ描画例
    # save_plot_recall_at_k_sort_types(illustrator_list, sort_types, "hue", legend_location)

    # バリエーション別グラフ
    # save_plot_recall_at_k_diff_values(illustrator_list, "random", diff_values_list, legend_location)

    # 推薦段階別グラフ
    # save_plot_recall_at_k_sort_types_fixed_subjects(illustrator_list, "random", legend_location)

    print("実験実行準備完了")


if __name__ == "__main__":
    main()
