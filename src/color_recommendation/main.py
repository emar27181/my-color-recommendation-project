"""
メイン実行スクリプト

config.py の設定に基づいて色推薦システムの各種処理を実行します。

使用方法:
  1. config/config.example.py を config/config.py としてコピー
  2. config.py の設定を編集
  3. python src/color_recommendation/main.py を実行

設定ファイル: src/color_recommendation/config/config.py
"""

import json
from PIL import Image
import numpy as np

# 設定ファイルのインポート
try:
    from config import config
except ImportError:
    print("⚠️ エラー: config.py が見つかりません")
    print("以下のコマンドで設定ファイルを作成してください:")
    print("  cp src/color_recommendation/config/config.example.py src/color_recommendation/config/config.py")
    exit(1)

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
from utils.plot_survey_results import SurveyResultPlotter
from color_recommendation import (
    read_file, generate_recommend_colors_by_illustrator,
    save_recommendations_for_illustrators
)


def setup_illustrator_list(illustrator_list):
    """イラストレーターリストのセットアップ"""
    illustrator_list = get_not_monochrome_illustrator_list(illustrator_list)
    illustrator_list = get_excluded_small_number_illustrator_list(illustrator_list, 10)
    return illustrator_list


def run_survey_result_graphs():
    """アンケート結果グラフ生成"""
    if not config.IS_PLOT_SURVEY_RESULTS:
        return

    print("\n" + "=" * 60)
    print("📊 アンケート結果グラフ生成")
    print("=" * 60)

    plotter = SurveyResultPlotter()
    plotter.plot_all_results()  # 箱ひげ図・ヴァイオリン図・操作時間グラフを生成（全データ）
    plotter.plot_first_impression_results()  # 箱ひげ図・ヴァイオリン図を生成（第一印象のみ・順序効果排除）


def run_existing_app_comparison(illustrator_list):
    """既存アプリとの比較実行"""
    if not config.RUN_EXISTING_APP_COMPARISON:
        return

    print("\n" + "=" * 60)
    print("📱 既存アプリとの比較")
    print("=" * 60)

    # APP_NAMESにPROPOSED_METHODを追加
    app_names = config.APP_NAMES + [PROPOSED_METHOD]

    for recommend_type in config.RECOMMEND_TYPES:
        for sort_type in config.SORT_TYPES:
            if "existing_apps" in recommend_type:
                for app_name in app_names:
                    print(f"\n📊 処理中: {sort_type} - {recommend_type} - {app_name}")

                    if config.GENERATE_EXISTING_APP_RECOMMENDATIONS:
                        print(f"  → 推薦配色群の保存")
                        save_recommendations_for_illustrators(
                            illustrator_list, recommend_type, sort_type,
                            config.DIFF_VALUES, app_name
                        )

                    if config.GENERATE_EXISTING_APP_EVALUATIONS:
                        print(f"  → 次の色が含まれているかの判定結果を保存")
                        save_data_is_contained_next_for_illustrators(
                            illustrator_list, sort_type, recommend_type, app_name
                        )

                    if config.GENERATE_EXISTING_APP_GRAPHS:
                        print(f"  → recall@k グラフの保存")
                        save_plot_recall_at_k_for_illustrators(
                            illustrator_list, sort_type, recommend_type,
                            app_name, config.LEGEND_LOCATION
                        )


def run_main_graphs(illustrator_list):
    """主要グラフ生成"""
    if not config.IS_SAVE_GRAPH:
        return

    print("\n" + "=" * 60)
    print("📈 主要グラフ生成（PDF形式、graph_pdfディレクトリに保存）")
    print("=" * 60)

    # ソートタイプ別recall@kグラフ（エラーバー付き）
    if config.GENERATE_RECALL_AT_K_SORT_TYPES:
        print("\n✅ ソートタイプ別recall@kグラフ（エラーバー付き）")
        save_plot_recall_at_k_sort_types(
            illustrator_list, config.SORT_TYPES, "hue", config.LEGEND_LOCATION
        )

    # バリエーション別recall@kグラフ
    if config.GENERATE_RECALL_AT_K_DIFF_VALUES:
        print("\n📊 バリエーション別recall@kグラフ")
        save_plot_recall_at_k_diff_values(
            illustrator_list, "random", config.DIFF_VALUES_LIST, config.LEGEND_LOCATION
        )

    # 推薦段階別(color/hue/tone)recall@kグラフ
    if config.GENERATE_RECALL_AT_K_FIXED_SUBJECTS:
        print("\n📊 推薦段階別(color/hue/tone)recall@kグラフ")
        save_plot_recall_at_k_sort_types_fixed_subjects(
            illustrator_list, "random", config.LEGEND_LOCATION
        )


def run_statistical_graphs(illustrator_list):
    """統計グラフ生成"""
    if not config.IS_SAVE_GRAPH:
        return

    print("\n" + "=" * 60)
    print("📊 統計グラフ生成")
    print("=" * 60)

    # 無彩色使用率の棒グラフ（積み上げ）
    if config.GENERATE_ACHROMATIC_BAR:
        print("\n📊 無彩色使用率の棒グラフ（積み上げ）")
        save_plot_bar_from_used_achromatic_colors_average_rate_for_illustrators(illustrator_list)

    # 平均結果長のヴァイオリン図
    if config.GENERATE_MEAN_RESULTANT_VIOLIN:
        print("\n🎻 平均結果長のヴァイオリン図")
        save_plot_violin_from_mean_resultant_length_count_for_illustrators(illustrator_list)

    # 使用色相数のヴァイオリン図
    if config.GENERATE_USED_HUES_VIOLIN:
        print("\n🎻 使用色相数のヴァイオリン図")
        save_plot_violin_from_used_hues_count_for_illustrators(illustrator_list)

    # PCCS色相分布のヴァイオリン図
    if config.GENERATE_PCCS_DISTRIBUTION_VIOLIN:
        print("\n🎻 PCCS色相分布のヴァイオリン図")
        save_plot_violin_from_used_pccs_distribution_for_illustrators()

    # 使用色の散布図（彩度×明度）※多数のファイル生成
    if config.GENERATE_SCATTER_PLOTS:
        print("\n📊 使用色の散布図（彩度×明度）※多数のファイル生成")
        save_plot_scatter_for_illustrators(illustrator_list)

    # トーン使用のヒートマップ※多数のファイル生成
    if config.GENERATE_TONE_HEATMAPS:
        print("\n🗺️  トーン使用のヒートマップ※多数のファイル生成")
        save_plot_tone_heatmap_for_illustrators(illustrator_list)

    # 匿名版の統計グラフ生成
    if config.GENERATE_ANONYMOUS_GRAPHS:
        print("\n" + "=" * 60)
        print("📊 匿名版の統計グラフ生成")
        print("=" * 60)

        if config.GENERATE_ACHROMATIC_BAR:
            print("\n📊 匿名版：無彩色使用率の棒グラフ（積み上げ）")
            save_plot_bar_from_used_achromatic_colors_average_rate_for_illustrators(illustrator_list, is_anonymous=True)

        if config.GENERATE_MEAN_RESULTANT_VIOLIN:
            print("\n🎻 匿名版：平均結果長のヴァイオリン図")
            save_plot_violin_from_mean_resultant_length_count_for_illustrators(illustrator_list, is_anonymous=True)

        if config.GENERATE_USED_HUES_VIOLIN:
            print("\n🎻 匿名版：使用色相数のヴァイオリン図")
            save_plot_violin_from_used_hues_count_for_illustrators(illustrator_list, is_anonymous=True)

        if config.GENERATE_PCCS_DISTRIBUTION_VIOLIN:
            print("\n🎻 匿名版：PCCS色相分布のヴァイオリン図")
            save_plot_violin_from_used_pccs_distribution_for_illustrators(is_anonymous=True)

        if config.GENERATE_SCATTER_PLOTS:
            print("\n📊 匿名版：使用色の散布図（彩度×明度）")
            save_plot_scatter_for_illustrators(illustrator_list, is_anonymous=True)

        if config.GENERATE_TONE_HEATMAPS:
            print("\n🗺️  匿名版：トーン使用のヒートマップ")
            save_plot_tone_heatmap_for_illustrators(illustrator_list, is_anonymous=True)


def print_config_summary():
    """設定内容のサマリーを表示"""
    print("\n" + "=" * 60)
    print("⚙️  実行設定")
    print("=" * 60)
    print(f"デバッグモード: {config.DEBUG_MODE}")
    print(f"グラフ生成: {config.IS_SAVE_GRAPH}")
    print(f"アンケート結果グラフ: {config.IS_PLOT_SURVEY_RESULTS}")
    print(f"既存アプリ比較: {config.RUN_EXISTING_APP_COMPARISON}")

    if config.DEBUG_MODE:
        print(f"\nイラストレーター: {config.DEBUG_ILLUSTRATOR_LIST}")
    else:
        print(f"\nイラストレーター数: {len(config.ILLUSTRATOR_LIST)}名")

    print(f"\nソートタイプ: {', '.join(config.SORT_TYPES)}")
    print(f"推薦タイプ: {', '.join(config.RECOMMEND_TYPES)}")
    print("=" * 60)


def main():
    """
    メイン処理
    """
    print("\n" + "=" * 80)
    print("🎨 色推薦システム - メイン実行スクリプト")
    print("=" * 80)
    
    # 設定内容の表示
    print_config_summary()
    
    # イラストレーターリストのセットアップ
    if config.DEBUG_MODE:
        illustrator_list = config.DEBUG_ILLUSTRATOR_LIST
    else:
        illustrator_list = setup_illustrator_list(config.ILLUSTRATOR_LIST)
    
    print(f"\n✅ 処理対象イラストレーター: {len(illustrator_list)}名")
    if len(illustrator_list) <= 5:
        print(f"   → {illustrator_list}")
    
    # 統計グラフ生成
    run_statistical_graphs(illustrator_list)
    
    # アンケート結果のグラフ化
    if config.IS_PLOT_SURVEY_RESULTS:
        plot_survey_results()
    
    # 既存アプリとの比較
    if config.RUN_EXISTING_APP_COMPARISON:
        run_existing_app_comparison(illustrator_list)
    


if __name__ == "__main__":
    main()
