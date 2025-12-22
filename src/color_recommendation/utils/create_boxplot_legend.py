"""
箱ひげ図の見方説明図を作成するスクリプト
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
from pathlib import Path
import warnings

warnings.filterwarnings('ignore', message='.*Glyph.*missing from font.*')

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


def create_boxplot_explanation():
    """箱ひげ図の見方を説明する図を作成"""

    # サンプルデータ（説明用）
    np.random.seed(42)
    data = [1.5, 2.0, 2.2, 2.5, 2.8, 3.0, 3.2, 3.5, 3.8, 4.0, 4.2, 4.5, 5.0]

    fig, ax = plt.subplots(figsize=(12, 8))

    # 箱ひげ図を描画
    bp = ax.boxplot(
        [data],
        positions=[2],
        widths=0.6,
        patch_artist=True,
        showmeans=True,
        meanprops=dict(marker='D', markerfacecolor='red', markersize=10, zorder=3),
        medianprops=dict(color='orange', linewidth=3),
        boxprops=dict(facecolor='#3498db', alpha=0.6, linewidth=2),
        whiskerprops=dict(linewidth=2),
        capprops=dict(linewidth=2),
        flierprops=dict(marker='o', markerfacecolor='black', markersize=8, alpha=0.5)
    )

    # 統計値を計算
    q1 = np.percentile(data, 25)
    median = np.median(data)
    q3 = np.percentile(data, 75)
    mean = np.mean(data)
    iqr = q3 - q1
    lower_whisker = max(min(data), q1 - 1.5 * iqr)
    upper_whisker = min(max(data), q3 + 1.5 * iqr)

    # 注釈を追加（矢印付き）
    annotation_style = dict(
        fontsize=12,
        fontweight='bold',
        ha='left',
        va='center',
        fontproperties=jp_font_prop,
        bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='black', linewidth=1.5)
    )

    arrow_props = dict(
        arrowstyle='->,head_width=0.4,head_length=0.8',
        linewidth=2,
        color='black'
    )

    # 各要素の説明
    # 上側のひげ
    ax.annotate(
        f'上側のひげ（最大値）\n= {upper_whisker:.1f}',
        xy=(2, upper_whisker),
        xytext=(3.5, upper_whisker),
        arrowprops=arrow_props,
        **annotation_style
    )

    # 第3四分位数（75%点）
    ax.annotate(
        f'第３四分位数（７５％点）\n箱の上端 = {q3:.1f}',
        xy=(2.3, q3),
        xytext=(3.5, q3),
        arrowprops=arrow_props,
        **annotation_style
    )

    # 中央値（オレンジの線）
    ax.annotate(
        f'中央値（オレンジの太線）\n= {median:.1f}',
        xy=(2.3, median),
        xytext=(3.5, median + 0.3),
        arrowprops=arrow_props,
        **annotation_style
    )

    # 平均値（赤いダイヤ）
    ax.annotate(
        f'平均値（赤いダイヤ◆）\n= {mean:.1f}',
        xy=(2, mean),
        xytext=(0.2, mean),
        arrowprops=dict(arrowstyle='->,head_width=0.4,head_length=0.8', linewidth=2, color='red'),
        fontsize=12,
        fontweight='bold',
        ha='right',
        va='center',
        fontproperties=jp_font_prop,
        bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='red', linewidth=2)
    )

    # 第1四分位数（25%点）
    ax.annotate(
        f'第１四分位数（２５％点）\n箱の下端 = {q1:.1f}',
        xy=(2.3, q1),
        xytext=(3.5, q1),
        arrowprops=arrow_props,
        **annotation_style
    )

    # 下側のひげ
    ax.annotate(
        f'下側のひげ（最小値）\n= {lower_whisker:.1f}',
        xy=(2, lower_whisker),
        xytext=(3.5, lower_whisker),
        arrowprops=arrow_props,
        **annotation_style
    )

    # 外れ値の説明（もし存在すれば）
    outliers = [x for x in data if x < lower_whisker or x > upper_whisker]
    if outliers:
        ax.annotate(
            '外れ値（○）',
            xy=(2, outliers[0]),
            xytext=(0.2, outliers[0]),
            arrowprops=arrow_props,
            **annotation_style
        )

    # 箱の説明（IQR）
    ax.annotate(
        '',
        xy=(1.4, q1),
        xytext=(1.4, q3),
        arrowprops=dict(arrowstyle='<->', linewidth=2, color='green')
    )
    ax.text(
        0.8, (q1 + q3) / 2,
        f'ＩＱＲ\n（四分位範囲）\n= {iqr:.1f}',
        ha='right',
        va='center',
        fontsize=11,
        fontweight='bold',
        fontproperties=jp_font_prop,
        bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen', edgecolor='green', linewidth=2)
    )

    # 軸設定
    ax.set_xlim(0, 6.5)
    ax.set_ylim(0.5, 5.5)
    ax.set_yticks(range(1, 6))
    for tick in ax.get_yticklabels():
        tick.set_fontsize(11)
        tick.set_fontfamily('DejaVu Sans')
    ax.set_xticks([])
    ax.set_ylabel('評価スコア', fontsize=13, fontweight='bold', fontproperties=jp_font_prop)

    # グリッド
    ax.yaxis.grid(True, linestyle='--', alpha=0.3)
    ax.set_axisbelow(True)

    # タイトル
    title_text = '箱ひげ図の見方'
    fig.suptitle(
        title_text,
        fontsize=16,
        fontweight='bold',
        y=0.96,
        fontproperties=jp_font_prop
    )

    # 補足説明を追加
    explanation_text = (
        '【データの分布を理解する】\n'
        '・箱の中に全データの５０％が含まれる\n'
        '・ひげを含めると、外れ値を除く大部分のデータが含まれる\n'
        '・中央値は「データを大小順に並べたときの真ん中の値」\n'
        '・平均値は「全データの合計 ÷ データ数」'
    )

    ax.text(
        0.5, -0.15,
        explanation_text,
        transform=ax.transAxes,
        fontsize=11,
        ha='left',
        va='top',
        fontproperties=jp_font_prop,
        bbox=dict(boxstyle='round,pad=0.8', facecolor='lightyellow', edgecolor='orange', linewidth=2)
    )

    # レイアウト調整
    plt.tight_layout(rect=[0, 0.15, 1, 0.94])

    # 保存
    output_dir = Path(__file__).parent.parent / "data" / "output" / "experiment_analysis"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "boxplot_explanation.pdf"

    plt.savefig(output_path, format='pdf', bbox_inches='tight', dpi=300)
    print(f"✅ 箱ひげ図の説明図を保存しました: {output_path}")

    plt.close()


if __name__ == "__main__":
    create_boxplot_explanation()
