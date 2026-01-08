"""
TaskA/TaskBごとのUI1/UI2比較分析
"""
import json
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from scipy import stats
import pandas as pd

# 日本語フォント設定
JP_FONT_PATH = '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf'
if Path(JP_FONT_PATH).exists():
    jp_font_prop = fm.FontProperties(fname=JP_FONT_PATH)
else:
    jp_font_prop = None

import matplotlib
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['Droid Sans Fallback', 'DejaVu Sans']
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['axes.unicode_minus'] = False

# 質問ラベル
QUESTION_LABELS = [
    "色が多すぎる",
    "色が少なすぎる",
    "塗りたい色が見つかった",
    "バランスよく塗れた",
    "スムーズに色を選べた",
    "絵の出来に満足",
    "UIに満足"
]


def load_all_experiment_data():
    """全実験データを読み込み"""
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

    return all_data


def extract_task_ui_data(all_data):
    """TaskA/TaskBごとのUI1/UI2データを抽出"""

    task_ui_data = {
        'TaskA': {'UI1': [], 'UI2': []},
        'TaskB': {'UI1': [], 'UI2': []}
    }

    for participant_data in all_data:
        for condition in participant_data.get('conditions', []):
            ui_type = condition.get('condition', '')  # UI1 or UI2
            material = condition.get('material', '')  # taskA or taskB
            duration = condition.get('task_duration_sec')

            if material.upper() == 'TASKA':
                task = 'TaskA'
            elif material.upper() == 'TASKB':
                task = 'TaskB'
            else:
                continue

            if ui_type in ['UI1', 'UI2'] and duration is not None:
                task_ui_data[task][ui_type].append({
                    'participant': participant_data['participant_name'],
                    'duration': duration,
                    'pattern': condition.get('pattern', '')
                })

    return task_ui_data


def calculate_task_statistics(task_ui_data):
    """タスクごとの統計を計算"""

    stats_results = {}

    for task in ['TaskA', 'TaskB']:
        ui1_durations = [d['duration'] for d in task_ui_data[task]['UI1']]
        ui2_durations = [d['duration'] for d in task_ui_data[task]['UI2']]

        stats_results[task] = {
            'UI1': {
                'n': len(ui1_durations),
                'mean': np.mean(ui1_durations) if ui1_durations else 0,
                'std': np.std(ui1_durations, ddof=1) if len(ui1_durations) > 1 else 0,
                'median': np.median(ui1_durations) if ui1_durations else 0
            },
            'UI2': {
                'n': len(ui2_durations),
                'mean': np.mean(ui2_durations) if ui2_durations else 0,
                'std': np.std(ui2_durations, ddof=1) if len(ui2_durations) > 1 else 0,
                'median': np.median(ui2_durations) if ui2_durations else 0
            }
        }

        # t検定
        if ui1_durations and ui2_durations:
            t_stat, p_value = stats.ttest_ind(ui1_durations, ui2_durations)
            stats_results[task]['t_test'] = {
                't_statistic': t_stat,
                'p_value': p_value,
                'significant': p_value < 0.05
            }

    return stats_results


def plot_task_ui_comparison(task_ui_data, stats_results, output_path):
    """TaskA/TaskBごとのUI1/UI2所要時間比較グラフを作成"""

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.patch.set_facecolor('white')

    for idx, task in enumerate(['TaskA', 'TaskB']):
        ax = axes[idx]
        ax.set_facecolor('white')

        ui1_durations = [d['duration'] for d in task_ui_data[task]['UI1']]
        ui2_durations = [d['duration'] for d in task_ui_data[task]['UI2']]

        data = [ui1_durations, ui2_durations]
        positions = [1, 2]

        # 箱ひげ図
        bp = ax.boxplot(data, positions=positions, widths=0.6, patch_artist=True,
                       showmeans=True,
                       meanprops=dict(marker='D', markerfacecolor='red', markersize=8),
                       medianprops=dict(color='black', linewidth=2))

        colors = ['#3498db', '#e74c3c']
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.6)

        # 個別データポイントをプロット
        for pos, dataset in zip(positions, data):
            y = dataset
            x = np.random.normal(pos, 0.04, size=len(y))
            ax.scatter(x, y, alpha=0.4, s=30, color='gray', edgecolor='black', linewidth=0.5)

        # 統計情報を表示
        ui1_stats = stats_results[task]['UI1']
        ui2_stats = stats_results[task]['UI2']

        info_text = (
            f"UI1: n={ui1_stats['n']}, M={ui1_stats['mean']:.1f}s, SD={ui1_stats['std']:.1f}s\n"
            f"UI2: n={ui2_stats['n']}, M={ui2_stats['mean']:.1f}s, SD={ui2_stats['std']:.1f}s"
        )

        if 't_test' in stats_results[task]:
            t_test = stats_results[task]['t_test']
            sig_mark = "**" if t_test['p_value'] < 0.01 else "*" if t_test['p_value'] < 0.05 else "n.s."
            info_text += f"\nt={t_test['t_statistic']:.2f}, p={t_test['p_value']:.4f} {sig_mark}"

        ax.text(0.5, 0.98, info_text, transform=ax.transAxes,
               fontsize=9, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        task_label = 'タスクＡ（キャラクター）' if task == 'TaskA' else 'タスクＢ（ロゴ）'
        ax.set_title(task_label, fontsize=14, fontweight='bold',
                    fontproperties=jp_font_prop, color='black')
        ax.set_xticks(positions)
        ax.set_xticklabels(['ＵＩ１', 'ＵＩ２'], fontproperties=jp_font_prop, fontsize=12)
        ax.set_ylabel('所要時間（秒）', fontproperties=jp_font_prop, fontsize=12, color='black')
        ax.grid(True, axis='y', linestyle='--', alpha=0.3, color='gray')
        ax.set_axisbelow(True)

        # 軸の色設定
        ax.tick_params(axis='x', colors='black')
        ax.tick_params(axis='y', colors='black')

    plt.suptitle('タスク別ＵＩ比較：所要時間', fontproperties=jp_font_prop,
                fontsize=16, fontweight='bold', y=0.98, color='black')

    plt.tight_layout()
    plt.savefig(output_path, format='pdf', dpi=300, facecolor='white', transparent=False)
    print(f"✅ グラフ保存完了: {output_path}")
    plt.close()


def generate_task_analysis_report(stats_results, output_path):
    """タスク別分析レポートを生成"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# TaskA/TaskB別 UI1/UI2比較分析レポート\n\n")
        f.write("生成日: 2026-01-08\n\n")

        f.write("## 概要\n\n")
        f.write("本レポートは、実験参加者のTaskA（キャラクター塗り）とTaskB（ロゴ塗り）における\n")
        f.write("UI1（従来UI）とUI2（二段階推薦UI）の所要時間を比較分析したものです。\n\n")

        for task in ['TaskA', 'TaskB']:
            task_label = 'タスクＡ（キャラクター塗り）' if task == 'TaskA' else 'タスクＢ（ロゴ塗り）'
            f.write(f"## {task_label}\n\n")

            ui1_stats = stats_results[task]['UI1']
            ui2_stats = stats_results[task]['UI2']

            f.write("### 記述統計\n\n")
            f.write("| UI | n | 平均（秒） | 標準偏差（秒） | 中央値（秒） |\n")
            f.write("|---|---|---|---|---|\n")
            f.write(f"| UI1 | {ui1_stats['n']} | {ui1_stats['mean']:.2f} | {ui1_stats['std']:.2f} | {ui1_stats['median']:.2f} |\n")
            f.write(f"| UI2 | {ui2_stats['n']} | {ui2_stats['mean']:.2f} | {ui2_stats['std']:.2f} | {ui2_stats['median']:.2f} |\n\n")

            diff = ui1_stats['mean'] - ui2_stats['mean']
            diff_percent = (diff / ui1_stats['mean']) * 100 if ui1_stats['mean'] > 0 else 0

            f.write(f"**平均所要時間の差**: {diff:.2f}秒 ({diff_percent:+.1f}%)\n\n")

            if 't_test' in stats_results[task]:
                t_test = stats_results[task]['t_test']
                f.write("### 統計的検定（対応のないt検定）\n\n")
                f.write(f"- t統計量: {t_test['t_statistic']:.4f}\n")
                f.write(f"- p値: {t_test['p_value']:.4f}\n")

                if t_test['p_value'] < 0.01:
                    sig_level = "1%水準で有意"
                elif t_test['p_value'] < 0.05:
                    sig_level = "5%水準で有意"
                else:
                    sig_level = "有意差なし"

                f.write(f"- 有意性: {sig_level}\n\n")

                if t_test['significant']:
                    if diff > 0:
                        f.write("**結論**: UI2の方が統計的に有意に所要時間が短い\n\n")
                    else:
                        f.write("**結論**: UI1の方が統計的に有意に所要時間が短い\n\n")
                else:
                    f.write("**結論**: UI1とUI2の所要時間に統計的に有意な差は見られない\n\n")

        f.write("## 考察\n\n")

        taskA_faster_ui2 = stats_results['TaskA'].get('t_test', {}).get('significant', False) and \
                           (stats_results['TaskA']['UI1']['mean'] > stats_results['TaskA']['UI2']['mean'])
        taskB_faster_ui2 = stats_results['TaskB'].get('t_test', {}).get('significant', False) and \
                           (stats_results['TaskB']['UI1']['mean'] > stats_results['TaskB']['UI2']['mean'])

        if taskA_faster_ui2 and taskB_faster_ui2:
            f.write("- TaskA、TaskBともにUI2（二段階推薦）の方が有意に速い\n")
            f.write("- 二段階推薦はタスクの種類に関わらず効果的\n\n")
        elif taskA_faster_ui2 and not taskB_faster_ui2:
            f.write("- TaskA（キャラクター塗り）ではUI2が有意に速い\n")
            f.write("- TaskB（ロゴ塗り）では有意差なし\n")
            f.write("- 複雑なタスクで二段階推薦の効果が顕著\n\n")
        elif not taskA_faster_ui2 and taskB_faster_ui2:
            f.write("- TaskB（ロゴ塗り）ではUI2が有意に速い\n")
            f.write("- TaskA（キャラクター塗り）では有意差なし\n")
            f.write("- シンプルなタスクで二段階推薦の効果が顕著\n\n")
        else:
            f.write("- TaskA、TaskBともに有意差は見られない\n")
            f.write("- タスクの種類によらず、UI1とUI2の効率は同程度\n\n")

    print(f"✅ レポート保存完了: {output_path}")


def main():
    """メイン処理"""
    print("=" * 60)
    print("TaskA/TaskB別 UI1/UI2比較分析")
    print("=" * 60)

    # データ読み込み
    print("\n1. 実験データを読み込み中...")
    all_data = load_all_experiment_data()
    print(f"   参加者数: {len(all_data)}名")

    # Task/UIデータを抽出
    print("\n2. TaskA/TaskBごとのデータを抽出中...")
    task_ui_data = extract_task_ui_data(all_data)
    for task in ['TaskA', 'TaskB']:
        print(f"   {task}: UI1={len(task_ui_data[task]['UI1'])}件, UI2={len(task_ui_data[task]['UI2'])}件")

    # 統計計算
    print("\n3. 統計量を計算中...")
    stats_results = calculate_task_statistics(task_ui_data)

    # グラフ生成
    print("\n4. グラフを生成中...")
    output_dir = Path("/mnt/c/WSL-directory/my-color-recommendation-project/src/color_recommendation/data/output/experiment_analysis")
    output_dir.mkdir(parents=True, exist_ok=True)

    graph_path = output_dir / "task_ui_comparison.pdf"
    plot_task_ui_comparison(task_ui_data, stats_results, graph_path)

    # レポート生成
    print("\n5. レポートを生成中...")
    report_path = output_dir / "task_ui_analysis_report.md"
    generate_task_analysis_report(stats_results, report_path)

    print("\n" + "=" * 60)
    print("✅ 分析完了")
    print("=" * 60)
    print(f"\n出力ファイル:")
    print(f"  - グラフ: {graph_path}")
    print(f"  - レポート: {report_path}")


if __name__ == '__main__':
    main()
