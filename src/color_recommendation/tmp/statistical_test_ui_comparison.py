"""
UI1とUI2のアンケート結果の統計検定
対応のあるデータに対してWilcoxon符号付き順位検定と対応のあるt検定を実施
"""
import json
import numpy as np
import pandas as pd
from pathlib import Path
from scipy import stats
from typing import List, Tuple, Dict

# 質問ラベル
QUESTION_LABELS = [
    "色が多すぎると感じた",
    "色が少なすぎると感じた",
    "塗りたい色が見つかった",
    "バランスよく塗れた",
    "スムーズに色を選べた",
    "絵の出来に満足できた",
    "UIに満足できた"
]


def load_paired_data() -> Tuple[List[List[int]], List[List[int]], int]:
    """extractedディレクトリからペアデータを読み込み"""
    base_dir = Path("/mnt/c/WSL-directory/my-color-recommendation-project/src/color_recommendation/data/input/experiment_result/extracted")

    all_data = []
    for participant_dir in sorted(base_dir.iterdir()):
        if participant_dir.is_dir():
            json_path = participant_dir / "log_noname.json"
            if json_path.exists():
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data['participant_name'] = participant_dir.name
                    all_data.append(data)

    # ペアデータ抽出（両方のUIを使用した参加者のみ）
    ui1_all_responses = []
    ui2_all_responses = []

    for data in all_data:
        survey = data['survey']
        ui1_responses = survey.get('ui1_responses', [])
        ui2_responses = survey.get('ui2_responses', [])

        # 両方の回答がある場合のみ追加
        if ui1_responses and ui2_responses:
            ui1_all_responses.append(ui1_responses)
            ui2_all_responses.append(ui2_responses)

    participant_count = len(ui1_all_responses)
    return ui1_all_responses, ui2_all_responses, participant_count


def prepare_paired_data(ui1_responses: List[List[int]], ui2_responses: List[List[int]]) -> Tuple[List[List[int]], List[List[int]]]:
    """質問ごとにペアデータを整形"""
    num_questions = len(ui1_responses[0]) if ui1_responses else 0
    ui1_by_question = [[] for _ in range(num_questions)]
    ui2_by_question = [[] for _ in range(num_questions)]

    for participant_responses in ui1_responses:
        for q_idx, response in enumerate(participant_responses):
            ui1_by_question[q_idx].append(response)

    for participant_responses in ui2_responses:
        for q_idx, response in enumerate(participant_responses):
            ui2_by_question[q_idx].append(response)

    return ui1_by_question, ui2_by_question


def calculate_cohens_d(data1: List[float], data2: List[float]) -> float:
    """Cohen's d（効果量）を計算"""
    n1, n2 = len(data1), len(data2)
    var1, var2 = np.var(data1, ddof=1), np.var(data2, ddof=1)

    # プールされた標準偏差
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))

    # Cohen's d
    d = (np.mean(data1) - np.mean(data2)) / pooled_std
    return d


def interpret_cohens_d(d: float) -> str:
    """Cohen's dの解釈"""
    abs_d = abs(d)
    if abs_d < 0.2:
        return "negligible (無視できる)"
    elif abs_d < 0.5:
        return "small (小)"
    elif abs_d < 0.8:
        return "medium (中)"
    else:
        return "large (大)"


def perform_statistical_tests(ui1_data: List[List[int]], ui2_data: List[List[int]], participant_count: int):
    """統計検定を実施"""
    num_questions = len(ui1_data)

    results = []

    for q_idx in range(num_questions):
        ui1_values = np.array(ui1_data[q_idx])
        ui2_values = np.array(ui2_data[q_idx])

        # 基本統計量
        ui1_mean = np.mean(ui1_values)
        ui1_median = np.median(ui1_values)
        ui1_std = np.std(ui1_values, ddof=1)

        ui2_mean = np.mean(ui2_values)
        ui2_median = np.median(ui2_values)
        ui2_std = np.std(ui2_values, ddof=1)

        mean_diff = ui2_mean - ui1_mean

        # 正規性検定（Shapiro-Wilk検定）
        _, ui1_normality_p = stats.shapiro(ui1_values)
        _, ui2_normality_p = stats.shapiro(ui2_values)

        # Wilcoxon符号付き順位検定（対応のあるノンパラメトリック検定）
        wilcoxon_stat, wilcoxon_p = stats.wilcoxon(ui1_values, ui2_values, alternative='two-sided')

        # 対応のあるt検定
        t_stat, t_p = stats.ttest_rel(ui1_values, ui2_values)

        # Cohen's d（効果量）
        cohens_d = calculate_cohens_d(ui1_values, ui2_values)
        cohens_d_interpretation = interpret_cohens_d(cohens_d)

        # 有意性判定（Wilcoxon検定基準）
        if wilcoxon_p < 0.001:
            significance = "***"
            significance_text = "p < 0.001 (非常に有意)"
        elif wilcoxon_p < 0.01:
            significance = "**"
            significance_text = "p < 0.01 (有意)"
        elif wilcoxon_p < 0.05:
            significance = "*"
            significance_text = "p < 0.05 (有意)"
        else:
            significance = "n.s."
            significance_text = "p ≥ 0.05 (有意差なし)"

        question_label = QUESTION_LABELS[q_idx] if q_idx < len(QUESTION_LABELS) else f"Q{q_idx + 1}"

        results.append({
            '質問番号': f'Q{q_idx + 1}',
            '質問内容': question_label,
            'n': participant_count,
            'UI1_平均': f'{ui1_mean:.2f}',
            'UI1_中央値': f'{ui1_median:.1f}',
            'UI1_SD': f'{ui1_std:.2f}',
            'UI2_平均': f'{ui2_mean:.2f}',
            'UI2_中央値': f'{ui2_median:.1f}',
            'UI2_SD': f'{ui2_std:.2f}',
            '平均値差(UI2-UI1)': f'{mean_diff:+.2f}',
            'Wilcoxon_検定統計量': f'{wilcoxon_stat:.2f}',
            'Wilcoxon_p値': f'{wilcoxon_p:.4f}',
            't検定_t値': f'{t_stat:.3f}',
            't検定_p値': f'{t_p:.4f}',
            "Cohen's_d": f'{cohens_d:.3f}',
            '効果量解釈': cohens_d_interpretation,
            '有意性': significance,
            '判定': significance_text,
            'UI1_正規性p値': f'{ui1_normality_p:.4f}',
            'UI2_正規性p値': f'{ui2_normality_p:.4f}'
        })

    return results


def save_results_to_csv(results: List[Dict], output_filename: str):
    """結果をCSVに保存"""
    output_dir = Path("/mnt/c/WSL-directory/my-color-recommendation-project/src/color_recommendation/data/output/experiment_analysis")
    output_path = output_dir / output_filename

    df = pd.DataFrame(results)
    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"✅ 統計検定結果を保存: {output_path}")


def print_results_summary(results: List[Dict]):
    """結果のサマリーを表示"""
    print("\n" + "=" * 100)
    print("📊 統計検定結果サマリー")
    print("=" * 100)
    print("\n【検定方法】")
    print("- Wilcoxon符号付き順位検定（対応のあるノンパラメトリック検定）")
    print("- 対応のあるt検定（参考）")
    print("- 効果量: Cohen's d")
    print("\n【有意水準】")
    print("- ***: p < 0.001 (非常に有意)")
    print("- **: p < 0.01 (有意)")
    print("- *: p < 0.05 (有意)")
    print("- n.s.: p ≥ 0.05 (有意差なし)")
    print("\n" + "-" * 100)

    for result in results:
        print(f"\n【{result['質問番号']}】 {result['質問内容']}")
        print(f"  UI1: 平均={result['UI1_平均']}, 中央値={result['UI1_中央値']}, SD={result['UI1_SD']}")
        print(f"  UI2: 平均={result['UI2_平均']}, 中央値={result['UI2_中央値']}, SD={result['UI2_SD']}")
        print(f"  平均値差(UI2-UI1): {result['平均値差(UI2-UI1)']}")
        print(f"  Wilcoxon検定: p={result['Wilcoxon_p値']} {result['有意性']}")
        print(f"  対応のあるt検定: t={result['t検定_t値']}, p={result['t検定_p値']}")
        cohens_d_key = "Cohen's_d"
        print(f"  Cohen's d: {result[cohens_d_key]} ({result['効果量解釈']})")
        print(f"  ➡️  {result['判定']}")

    print("\n" + "=" * 100)
    print("📌 有意差が認められた項目")
    print("=" * 100)

    significant_items = [r for r in results if r['有意性'] != 'n.s.']
    if significant_items:
        for item in significant_items:
            direction = "UI2 > UI1" if float(item['平均値差(UI2-UI1)']) > 0 else "UI2 < UI1"
            cohens_d_key = "Cohen's_d"
            print(f"  {item['質問番号']}: {item['質問内容']}")
            print(f"    → {direction}, Wilcoxon p={item['Wilcoxon_p値']} {item['有意性']}, Cohen's d={item[cohens_d_key]}")
    else:
        print("  有意差が認められた項目はありません")

    print("\n" + "=" * 100)


def main():
    """メイン実行関数"""
    print("📊 UI1とUI2の統計検定を実施します\n")

    # データ読み込み
    print("📁 ペアデータ読み込み中...")
    ui1_responses, ui2_responses, participant_count = load_paired_data()
    print(f"✅ 参加者数（両方のUIを使用）: {participant_count}名\n")

    # データ整形
    print("🔧 データ整形中...")
    ui1_by_question, ui2_by_question = prepare_paired_data(ui1_responses, ui2_responses)

    # 統計検定実施
    print("📈 統計検定実施中...")
    results = perform_statistical_tests(ui1_by_question, ui2_by_question, participant_count)

    # 結果保存
    save_results_to_csv(results, "statistical_test_results.csv")

    # 結果表示
    print_results_summary(results)

    print("\n✅ 検定完了")


if __name__ == "__main__":
    main()
