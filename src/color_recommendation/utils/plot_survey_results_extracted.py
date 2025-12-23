"""
extractedディレクトリのデータから直接アンケート結果グラフを生成
"""
import json
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

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
    "色が多すぎると感じた",
    "色が少なすぎると感じた",
    "塗りたい色が見つかった",
    "バランスよく塗れた",
    "スムーズに色を選べた",
    "絵の出来に満足できた",
    "UIに満足できた"
]


def load_extracted_data() -> Tuple[List[List[int]], List[List[int]], int, Dict, List[Dict]]:
    """extractedディレクトリからデータを読み込み"""
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

    # アンケートデータ抽出
    ui1_all_responses = []
    ui2_all_responses = []
    ui1_first_count = 0
    ui2_first_count = 0
    ui1_favorite_count = 0
    ui2_favorite_count = 0

    for data in all_data:
        survey = data['survey']
        first_ui = data.get('first_ui', '')

        ui1_responses = survey.get('ui1_responses', [])
        ui2_responses = survey.get('ui2_responses', [])

        if ui1_responses:
            ui1_all_responses.append(ui1_responses)
        if ui2_responses:
            ui2_all_responses.append(ui2_responses)

        if first_ui == "UI1":
            ui1_first_count += 1
        elif first_ui == "UI2":
            ui2_first_count += 1

        favorite = survey.get('favoriteUI', '')
        if favorite == "UI1":
            ui1_favorite_count += 1
        elif favorite == "UI2":
            ui2_favorite_count += 1

    participant_count = len(all_data)
    stats = {
        'ui1_first': ui1_first_count,
        'ui2_first': ui2_first_count,
        'ui1_favorite': ui1_favorite_count,
        'ui2_favorite': ui2_favorite_count
    }

    return ui1_all_responses, ui2_all_responses, participant_count, stats, all_data


def prepare_data_for_boxplot(ui1_responses: List[List[int]], ui2_responses: List[List[int]]) -> Tuple[List[List[int]], List[List[int]]]:
    """質問ごとにデータを整形"""
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


def to_fullwidth(text):
    """半角英数字を全角に変換"""
    return text.translate(str.maketrans(
        '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
        '０１２３４５６７８９ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ'
    ))


def plot_boxplot_comparison(ui1_data, ui2_data, participant_count, stats, output_filename):
    """箱ひげ図比較を作成"""
    num_questions = len(ui1_data)
    fig, axes = plt.subplots(1, num_questions, figsize=(3 * num_questions, 7))

    if num_questions == 1:
        axes = [axes]

    title_text = (
        f'ＵＩ評価アンケート結果比較 (n={to_fullwidth(str(participant_count))})\n'
        f'順序: ＵＩ１→ＵＩ２: {to_fullwidth(str(stats["ui1_first"]))}名, ＵＩ２→ＵＩ１: {to_fullwidth(str(stats["ui2_first"]))}名\n'
        f'好み: ＵＩ１: {to_fullwidth(str(stats["ui1_favorite"]))}名, ＵＩ２: {to_fullwidth(str(stats["ui2_favorite"]))}名'
    )
    fig.suptitle(title_text, fontsize=11, fontweight='bold', y=0.99, fontproperties=jp_font_prop)

    for q_idx in range(num_questions):
        ax = axes[q_idx]
        data = [ui1_data[q_idx], ui2_data[q_idx]]
        positions = [1, 2]

        bp = ax.boxplot(data, positions=positions, widths=0.6, patch_artist=True,
                       showmeans=True, meanprops=dict(marker='D', markerfacecolor='red', markersize=6))

        colors = ['#3498db', '#e74c3c']
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.6)

        # 個別データポイントを重ねて表示（箱が潰れている場合の視認性向上）
        for pos_idx, (position, question_data) in enumerate(zip(positions, data)):
            # データポイントを少しずらして表示
            x_jitter = np.random.normal(0, 0.04, size=len(question_data))
            ax.scatter([position + x for x in x_jitter], question_data,
                      alpha=0.4, s=20, color=colors[pos_idx], edgecolors='black', linewidth=0.5, zorder=3)

        ax.set_ylim(0.5, 5.5)
        ax.set_yticks(range(1, 6))
        # Y軸の数字は明示的にDejaVu Sansフォントで表示（日本語フォントの影響を回避）
        for tick in ax.get_yticklabels():
            tick.set_fontsize(11)
            tick.set_fontfamily('DejaVu Sans')
        ax.set_xticks(positions)
        ax.set_xticklabels(['ＵＩ１', 'ＵＩ２'], fontsize=11, fontproperties=jp_font_prop)

        if q_idx == 0:
            ax.set_ylabel('評価スコア\n1: 全くそう思わない    5: 非常にそう思う',
                        fontsize=9, fontweight='bold', fontproperties=jp_font_prop)

        ax.yaxis.grid(True, linestyle='--', alpha=0.3)
        ax.set_axisbelow(True)

        question_label = QUESTION_LABELS[q_idx] if q_idx < len(QUESTION_LABELS) else f"Q{q_idx + 1}"
        ax.set_xlabel(f'Q{q_idx + 1}\n{question_label}', fontsize=11, fontweight='bold',
                     labelpad=10, fontproperties=jp_font_prop)

        ui1_median = np.median(ui1_data[q_idx])
        ui2_median = np.median(ui2_data[q_idx])
        ax.text(1, 0.7, f'{ui1_median:.1f}', ha='center', va='center',
               fontsize=9, fontweight='bold', color='#3498db')
        ax.text(2, 0.7, f'{ui2_median:.1f}', ha='center', va='center',
               fontsize=9, fontweight='bold', color='#e74c3c')

        if q_idx == 0:
            from matplotlib.patches import Patch
            from matplotlib.lines import Line2D
            legend_elements = [
                Patch(facecolor='#3498db', alpha=0.6, label='ＵＩ１'),
                Patch(facecolor='#e74c3c', alpha=0.6, label='ＵＩ２'),
                Line2D([0], [0], marker='D', color='w', markerfacecolor='red',
                      markersize=6, label='平均値（赤ひし形）'),
                Line2D([0], [0], color='black', linewidth=1.5, label='中央値（箱内の線）'),
                Patch(facecolor='gray', alpha=0.3, label='箱（第１〜第３四分位）'),
                Line2D([0], [0], color='black', linewidth=1, linestyle='-',
                      label='ひげ（最小値・最大値）'),
                Line2D([0], [0], marker='o', color='w', markerfacecolor='gray',
                      markersize=5, alpha=0.4, markeredgecolor='black', markeredgewidth=0.5,
                      linestyle='', label='個別データポイント')
            ]
            # 凡例を図の下部中央に配置（グラフの外側）
            fig.legend(handles=legend_elements, loc='lower center', fontsize=8,
                      prop=jp_font_prop, framealpha=0.9, ncol=2,
                      bbox_to_anchor=(0.5, -0.05))

    plt.subplots_adjust(left=0.08, right=0.98, bottom=0.20, top=0.89)
    plt.tight_layout(rect=[0.05, 0.18, 1, 0.89])

    output_dir = Path("/mnt/c/WSL-directory/my-color-recommendation-project/src/color_recommendation/data/output/experiment_analysis")
    output_path = output_dir / output_filename
    plt.savefig(output_path, format='pdf', dpi=300)
    print(f"✅ グラフ保存完了: {output_path}")
    plt.close()


def plot_violin_comparison(ui1_data, ui2_data, participant_count, stats, output_filename):
    """ヴァイオリン図比較を作成"""
    num_questions = len(ui1_data)
    fig, axes = plt.subplots(1, num_questions, figsize=(3 * num_questions, 7))

    if num_questions == 1:
        axes = [axes]

    title_text = (
        f'ＵＩ評価アンケート結果比較（ヴァイオリン図） (n={to_fullwidth(str(participant_count))})\n'
        f'順序: ＵＩ１→ＵＩ２: {to_fullwidth(str(stats["ui1_first"]))}名, ＵＩ２→ＵＩ１: {to_fullwidth(str(stats["ui2_first"]))}名\n'
        f'好み: ＵＩ１: {to_fullwidth(str(stats["ui1_favorite"]))}名, ＵＩ２: {to_fullwidth(str(stats["ui2_favorite"]))}名'
    )
    fig.suptitle(title_text, fontsize=11, fontweight='bold', y=0.99, fontproperties=jp_font_prop)

    for q_idx in range(num_questions):
        ax = axes[q_idx]
        data = [ui1_data[q_idx], ui2_data[q_idx]]
        positions = [1, 2]

        parts = ax.violinplot(data, positions=positions, widths=0.45,
                            showmeans=True, showmedians=True, showextrema=True,
                            bw_method=0.3)

        colors = ['#3498db', '#e74c3c']
        for pc, color in zip(parts['bodies'], colors):
            pc.set_facecolor(color)
            pc.set_alpha(0.6)
            pc.set_edgecolor('black')
            pc.set_linewidth(1)

        parts['cmedians'].set_edgecolor('black')
        parts['cmedians'].set_linewidth(2)
        parts['cmeans'].set_edgecolor('red')
        parts['cmeans'].set_linewidth(2)
        parts['cbars'].set_edgecolor('black')
        parts['cmaxes'].set_edgecolor('black')
        parts['cmins'].set_edgecolor('black')

        ax.set_ylim(0.5, 5.5)
        ax.set_yticks(range(1, 6))
        # Y軸の数字は明示的にDejaVu Sansフォントで表示（日本語フォントの影響を回避）
        for tick in ax.get_yticklabels():
            tick.set_fontsize(11)
            tick.set_fontfamily('DejaVu Sans')
        ax.set_xticks(positions)
        ax.set_xticklabels(['ＵＩ１', 'ＵＩ２'], fontsize=11, fontproperties=jp_font_prop)

        if q_idx == 0:
            ax.set_ylabel('評価スコア\n1: 全くそう思わない    5: 非常にそう思う',
                        fontsize=9, fontweight='bold', fontproperties=jp_font_prop)

        ax.yaxis.grid(True, linestyle='--', alpha=0.3)
        ax.set_axisbelow(True)

        question_label = QUESTION_LABELS[q_idx] if q_idx < len(QUESTION_LABELS) else f"Q{q_idx + 1}"
        ax.set_xlabel(f'Q{q_idx + 1}\n{question_label}', fontsize=11, fontweight='bold',
                     labelpad=10, fontproperties=jp_font_prop)

        ui1_median = np.median(ui1_data[q_idx])
        ui2_median = np.median(ui2_data[q_idx])
        ax.text(1, 0.7, f'{ui1_median:.1f}', ha='center', va='center',
               fontsize=9, fontweight='bold', color='#3498db')
        ax.text(2, 0.7, f'{ui2_median:.1f}', ha='center', va='center',
               fontsize=9, fontweight='bold', color='#e74c3c')

        if q_idx == 0:
            from matplotlib.patches import Patch
            from matplotlib.lines import Line2D
            legend_elements = [
                Patch(facecolor='#3498db', alpha=0.6, label='ＵＩ１'),
                Patch(facecolor='#e74c3c', alpha=0.6, label='ＵＩ２'),
                Line2D([0], [0], color='red', linewidth=2, label='平均値（赤線）'),
                Line2D([0], [0], color='black', linewidth=2, label='中央値（黒線）'),
                Patch(facecolor='gray', alpha=0.3, label='分布（ヴァイオリン形状）'),
                Line2D([0], [0], color='black', linewidth=1, linestyle='-',
                      label='範囲（最小値・最大値）')
            ]
            # 凡例を図の下部中央に配置（グラフの外側）
            fig.legend(handles=legend_elements, loc='lower center', fontsize=8,
                      prop=jp_font_prop, framealpha=0.9, ncol=2,
                      bbox_to_anchor=(0.5, -0.05))

    plt.subplots_adjust(left=0.08, right=0.98, bottom=0.20, top=0.89)
    plt.tight_layout(rect=[0.05, 0.18, 1, 0.89])

    output_dir = Path("/mnt/c/WSL-directory/my-color-recommendation-project/src/color_recommendation/data/output/experiment_analysis")
    output_path = output_dir / output_filename
    plt.savefig(output_path, format='pdf', dpi=300)
    print(f"✅ グラフ保存完了: {output_path}")
    plt.close()


def plot_task_duration_comparison(all_data, participant_count, stats, output_filename):
    """タスク操作時間比較グラフを作成"""
    ui1_durations = []
    ui2_durations = []

    for data in all_data:
        for condition in data.get('conditions', []):
            ui_type = condition.get('condition', '')
            duration = condition.get('task_duration_sec')

            if duration is not None:
                if ui_type == 'UI1':
                    ui1_durations.append(duration)
                elif ui_type == 'UI2':
                    ui2_durations.append(duration)

    if not ui1_durations or not ui2_durations:
        print("⚠️ タスク時間データが不足しています")
        return

    fig, ax = plt.subplots(figsize=(8, 6))

    title_text = (
        f'タスク操作時間比較 (n={to_fullwidth(str(participant_count))})\n'
        f'順序: ＵＩ１→ＵＩ２: {to_fullwidth(str(stats["ui1_first"]))}名, ＵＩ２→ＵＩ１: {to_fullwidth(str(stats["ui2_first"]))}名\n'
        f'好み: ＵＩ１: {to_fullwidth(str(stats["ui1_favorite"]))}名, ＵＩ２: {to_fullwidth(str(stats["ui2_favorite"]))}名'
    )
    fig.suptitle(title_text, fontsize=11, fontweight='bold', y=0.98, fontproperties=jp_font_prop)

    data = [ui1_durations, ui2_durations]
    positions = [1, 2]

    bp = ax.boxplot(data, positions=positions, widths=0.6, patch_artist=True,
                   showmeans=True, meanprops=dict(marker='D', markerfacecolor='red', markersize=8))

    colors = ['#3498db', '#e74c3c']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)

    # 個別データポイントを重ねて表示
    for pos_idx, (position, duration_data) in enumerate(zip(positions, data)):
        x_jitter = np.random.normal(0, 0.04, size=len(duration_data))
        ax.scatter([position + x for x in x_jitter], duration_data,
                  alpha=0.4, s=20, color=colors[pos_idx], edgecolors='black', linewidth=0.5, zorder=3)

    ax.set_ylabel('操作時間(秒)', fontsize=12, fontweight='bold', fontproperties=jp_font_prop)
    ax.set_xticks(positions)
    ax.set_xticklabels(['ＵＩ１', 'ＵＩ２'], fontsize=12, fontweight='bold', fontproperties=jp_font_prop)

    ax.yaxis.grid(True, linestyle='--', alpha=0.3)
    ax.set_axisbelow(True)

    ui1_mean = np.mean(ui1_durations)
    ui1_median = np.median(ui1_durations)
    ui2_mean = np.mean(ui2_durations)
    ui2_median = np.median(ui2_durations)

    y_max = max(max(ui1_durations), max(ui2_durations))
    ax.text(1, y_max * 0.95, f'平均: {ui1_mean:.1f}秒\n中央値: {ui1_median:.1f}秒',
           ha='center', va='top', fontsize=10,
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
           fontproperties=jp_font_prop)
    ax.text(2, y_max * 0.95, f'平均: {ui2_mean:.1f}秒\n中央値: {ui2_median:.1f}秒',
           ha='center', va='top', fontsize=10,
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
           fontproperties=jp_font_prop)

    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    legend_elements = [
        Patch(facecolor='#3498db', alpha=0.6, label='ＵＩ１'),
        Patch(facecolor='#e74c3c', alpha=0.6, label='ＵＩ２'),
        Line2D([0], [0], marker='D', color='w', markerfacecolor='red',
              markersize=8, label='平均値（赤ひし形）'),
        Line2D([0], [0], color='black', linewidth=1.5, label='中央値（箱内の線）'),
        Patch(facecolor='gray', alpha=0.3, label='箱（第１〜第３四分位）'),
        Line2D([0], [0], color='black', linewidth=1, linestyle='-',
              label='ひげ（最小値・最大値）'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='gray',
              markersize=5, alpha=0.4, markeredgecolor='black', markeredgewidth=0.5,
              linestyle='', label='個別データポイント')
    ]
    # 凡例を図の下部中央に配置
    fig.legend(handles=legend_elements, loc='lower center', fontsize=8,
              prop=jp_font_prop, framealpha=0.9, ncol=2,
              bbox_to_anchor=(0.5, -0.05))

    plt.subplots_adjust(left=0.10, right=0.95, bottom=0.15, top=0.90)
    plt.tight_layout(rect=[0.08, 0.15, 1, 0.90])

    output_dir = Path("/mnt/c/WSL-directory/my-color-recommendation-project/src/color_recommendation/data/output/experiment_analysis")
    output_path = output_dir / output_filename
    plt.savefig(output_path, format='pdf', dpi=300)
    print(f"✅ グラフ保存完了: {output_path}")
    plt.close()


def main():
    """メイン実行関数"""
    print("📊 新しいデータからグラフを生成します\n")

    # データ読み込み
    print("📁 データ読み込み中...")
    ui1_responses, ui2_responses, participant_count, stats, all_data = load_extracted_data()
    print(f"✅ 参加者数: {participant_count}名")
    print(f"✅ 順序: UI1→UI2 {stats['ui1_first']}名, UI2→UI1 {stats['ui2_first']}名")
    print(f"✅ 好み: UI1 {stats['ui1_favorite']}名, UI2 {stats['ui2_favorite']}名\n")

    # データ整形
    print("🔧 データ整形中...")
    ui1_by_question, ui2_by_question = prepare_data_for_boxplot(ui1_responses, ui2_responses)

    # グラフ作成
    print("📈 箱ひげ図作成中...")
    plot_boxplot_comparison(ui1_by_question, ui2_by_question, participant_count, stats,
                           "survey_boxplot_comparison.pdf")

    print("🎻 ヴァイオリン図作成中...")
    plot_violin_comparison(ui1_by_question, ui2_by_question, participant_count, stats,
                          "survey_violin_comparison.pdf")

    print("⏱️  タスク時間グラフ作成中...")
    plot_task_duration_comparison(all_data, participant_count, stats,
                                 "task_duration_comparison.pdf")

    print(f"\n{'=' * 60}")
    print("✅ 全グラフ生成完了")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
