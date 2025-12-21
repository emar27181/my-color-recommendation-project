"""
実験アンケート結果の可視化モジュール

UI1とUI2のアンケート結果を箱ひげ図で比較表示し、PDF形式で保存する。
"""

import json
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.font_manager as fm
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

# フォント設定
import warnings
warnings.filterwarnings('ignore', message='.*Glyph.*missing from font.*')

# 日本語フォントのパスを取得
JP_FONT_PATH = '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf'
if Path(JP_FONT_PATH).exists():
    jp_font_prop = fm.FontProperties(fname=JP_FONT_PATH)
else:
    jp_font_prop = None

# デフォルトフォント設定
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['DejaVu Sans']
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['axes.unicode_minus'] = False


class SurveyResultPlotter:
    """アンケート結果の可視化クラス"""

    # 質問ラベル（各質問の要約・キーワード）
    QUESTION_LABELS = [
        "色数(多)",      # Q1: 色が多すぎると感じた
        "色数(少)",      # Q2: 色が少なすぎると感じた
        "色発見",        # Q3: 塗りたいと思った色が見つかった
        "バランス",      # Q4: 指示された「バランスよく塗る」が実践しやすかった
        "スムーズ",      # Q5: 塗りたい色にたどり着くまでがスムーズだった
        "絵満足度",      # Q6: 完成した絵の出来に満足できた
        "UI満足度"       # Q7: 使用したUI（カラーパレット）に満足できた
    ]

    def __init__(self, base_dir: str = None):
        """
        初期化

        Args:
            base_dir: ベースディレクトリのパス
        """
        if base_dir is None:
            current_file = Path(__file__).resolve()
            self.base_dir = current_file.parent.parent / "data" / "input" / "experiment_result"
        else:
            self.base_dir = Path(base_dir)

        self.survey_dir = self.base_dir / "questionnaire" / "other"

        # 出力ディレクトリ設定
        self.output_dir = current_file.parent.parent / "data" / "output" / "experiment_analysis"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_survey_data(self) -> Tuple[List[List[int]], List[List[int]], int, Dict]:
        """
        全参加者のアンケートデータを読み込む

        Returns:
            Tuple[List[List[int]], List[List[int]], int, Dict]:
                (UI1の回答リスト, UI2の回答リスト, 参加者数, 統計情報)
        """
        ui1_all_responses = []
        ui2_all_responses = []

        # 追加情報
        ui1_first_count = 0  # UI1→UI2の順序
        ui2_first_count = 0  # UI2→UI1の順序
        ui1_favorite_count = 0  # UI1を好んだ人数
        ui2_favorite_count = 0  # UI2を好んだ人数

        survey_files = sorted(self.survey_dir.glob("*_survey.json"))

        for survey_file in survey_files:
            participant_id = survey_file.stem.replace('_survey', '')

            with open(survey_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

                ui1_responses = data.get("ui1_responses", [])
                ui2_responses = data.get("ui2_responses", [])

                if ui1_responses:
                    ui1_all_responses.append(ui1_responses)
                if ui2_responses:
                    ui2_all_responses.append(ui2_responses)

                # どちらを好んだか
                favorite = data.get("favoriteUI", "")
                if favorite == "UI1":
                    ui1_favorite_count += 1
                elif favorite == "UI2":
                    ui2_favorite_count += 1

            # メタデータから順序を取得
            metadata_file = self.survey_dir / f"{participant_id}_metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    first_ui = metadata.get("first_ui", "")
                    if first_ui == "UI1":
                        ui1_first_count += 1
                    elif first_ui == "UI2":
                        ui2_first_count += 1

        participant_count = len(ui1_all_responses)

        stats = {
            'ui1_first': ui1_first_count,
            'ui2_first': ui2_first_count,
            'ui1_favorite': ui1_favorite_count,
            'ui2_favorite': ui2_favorite_count
        }

        return ui1_all_responses, ui2_all_responses, participant_count, stats

    def prepare_data_for_boxplot(
        self,
        ui1_responses: List[List[int]],
        ui2_responses: List[List[int]]
    ) -> Tuple[List[List[int]], List[List[int]]]:
        """
        箱ひげ図用にデータを整形

        Args:
            ui1_responses: UI1の全参加者の回答
            ui2_responses: UI2の全参加者の回答

        Returns:
            Tuple[List[List[int]], List[List[int]]]:
                質問ごとに整理された(UI1データ, UI2データ)
        """
        # 質問数を取得
        num_questions = len(ui1_responses[0]) if ui1_responses else 0

        # 質問ごとにデータを整理
        ui1_by_question = [[] for _ in range(num_questions)]
        ui2_by_question = [[] for _ in range(num_questions)]

        for participant_responses in ui1_responses:
            for q_idx, response in enumerate(participant_responses):
                ui1_by_question[q_idx].append(response)

        for participant_responses in ui2_responses:
            for q_idx, response in enumerate(participant_responses):
                ui2_by_question[q_idx].append(response)

        return ui1_by_question, ui2_by_question

    def plot_boxplot_comparison(
        self,
        ui1_data: List[List[int]],
        ui2_data: List[List[int]],
        participant_count: int,
        stats: Dict,
        output_filename: str = "survey_boxplot_comparison.pdf"
    ):
        """
        UI1とUI2の箱ひげ図比較を作成

        Args:
            ui1_data: 質問ごとのUI1回答データ
            ui2_data: 質問ごとのUI2回答データ
            participant_count: 参加者数
            stats: 統計情報（順序、好み）
            output_filename: 出力ファイル名
        """
        num_questions = len(ui1_data)

        # 図のサイズ設定（質問数に応じて調整、下部ラベル用に高さを増加）
        fig, axes = plt.subplots(1, num_questions, figsize=(3 * num_questions, 7))

        # 1つの質問の場合はリストに変換
        if num_questions == 1:
            axes = [axes]

        # タイトルに統計情報を含める
        title_text = (
            f'UI評価アンケート結果比較 (n={participant_count})\n'
            f'順序: UI1→UI2 {stats["ui1_first"]}名, UI2→UI1 {stats["ui2_first"]}名 | '
            f'好み: UI1 {stats["ui1_favorite"]}名, UI2 {stats["ui2_favorite"]}名'
        )
        fig.suptitle(
            title_text,
            fontsize=14,
            fontweight='bold',
            y=0.97,
            fontproperties=jp_font_prop
        )

        for q_idx in range(num_questions):
            ax = axes[q_idx]

            # データ準備
            data = [ui1_data[q_idx], ui2_data[q_idx]]
            positions = [1, 2]

            # 箱ひげ図描画
            bp = ax.boxplot(
                data,
                positions=positions,
                widths=0.6,
                patch_artist=True,
                showmeans=True,
                meanprops=dict(marker='D', markerfacecolor='red', markersize=6)
            )

            # 色設定
            colors = ['#3498db', '#e74c3c']  # UI1: 青, UI2: 赤
            for patch, color in zip(bp['boxes'], colors):
                patch.set_facecolor(color)
                patch.set_alpha(0.6)

            # 軸設定
            ax.set_ylim(0.5, 5.5)
            ax.set_yticks(range(1, 6))
            ax.set_xticks(positions)
            ax.set_xticklabels(['UI1', 'UI2'], fontsize=11)

            # Y軸ラベル（最初の質問のみ、評価スケールを明示）
            if q_idx == 0:
                ax.set_ylabel('評価スコア\n1:全くそう思わない\n5:非常にそう思う',
                            fontsize=10, fontweight='bold', fontproperties=jp_font_prop)

            # グリッド
            ax.yaxis.grid(True, linestyle='--', alpha=0.3)
            ax.set_axisbelow(True)

            # 質問ラベルを下部に配置
            question_label = self.QUESTION_LABELS[q_idx] if q_idx < len(self.QUESTION_LABELS) else f"Q{q_idx + 1}"
            ax.set_xlabel(f'Q{q_idx + 1}\n{question_label}', fontsize=11, fontweight='bold',
                         labelpad=10, fontproperties=jp_font_prop)

            # 統計情報を表示（オプション）
            ui1_median = np.median(ui1_data[q_idx])
            ui2_median = np.median(ui2_data[q_idx])

            # 中央値を表示（1-5スケールに合わせて位置調整）
            ax.text(1, 0.7, f'{ui1_median:.1f}', ha='center', va='center',
                   fontsize=9, fontweight='bold', color='#3498db')
            ax.text(2, 0.7, f'{ui2_median:.1f}', ha='center', va='center',
                   fontsize=9, fontweight='bold', color='#e74c3c')

            # 最初のグラフのみ凡例を追加
            if q_idx == 0:
                from matplotlib.patches import Patch
                legend_elements = [
                    Patch(facecolor='#3498db', alpha=0.6, label='UI1'),
                    Patch(facecolor='#e74c3c', alpha=0.6, label='UI2')
                ]
                ax.legend(handles=legend_elements, loc='upper left', fontsize=10)

        # レイアウト調整（下部にラベル用のスペースを確保）
        plt.subplots_adjust(bottom=0.15, top=0.92)
        plt.tight_layout(rect=[0, 0.12, 1, 0.92])

        # 保存
        output_path = self.output_dir / output_filename
        plt.savefig(output_path, format='pdf', bbox_inches='tight', dpi=300)
        print(f"✅ グラフ保存完了: {output_path}")

        plt.close()

    def plot_all_results(self):
        """全アンケート結果を読み込んでグラフ作成"""
        print("📊 アンケート結果の可視化を開始します\n")

        # データ読み込み
        print("📁 データ読み込み中...")
        ui1_responses, ui2_responses, participant_count, stats = self.load_survey_data()
        print(f"✅ 参加者数: {participant_count}名")
        print(f"✅ 質問数: {len(ui1_responses[0])}問")
        print(f"✅ 順序: UI1→UI2 {stats['ui1_first']}名, UI2→UI1 {stats['ui2_first']}名")
        print(f"✅ 好み: UI1 {stats['ui1_favorite']}名, UI2 {stats['ui2_favorite']}名\n")

        # データ整形
        print("🔧 データ整形中...")
        ui1_by_question, ui2_by_question = self.prepare_data_for_boxplot(
            ui1_responses, ui2_responses
        )

        # グラフ作成
        print("📈 箱ひげ図作成中...")
        self.plot_boxplot_comparison(
            ui1_by_question,
            ui2_by_question,
            participant_count,
            stats
        )

        # 操作時間グラフ作成
        print("⏱️  操作時間グラフ作成中...")
        ui1_durations, ui2_durations = self.load_task_duration_data()
        if ui1_durations and ui2_durations:
            self.plot_task_duration_comparison(
                ui1_durations,
                ui2_durations,
                participant_count,
                stats
            )
        else:
            print("⚠️  操作時間データが見つかりませんでした")

        print(f"\n{'=' * 60}")
        print("✅ 可視化完了")
        print(f"{'=' * 60}\n")

        # 統計情報表示
        self._print_statistics(ui1_by_question, ui2_by_question, participant_count)

    def load_task_duration_data(self) -> Tuple[List[float], List[float]]:
        """
        全参加者のタスク操作時間データを読み込む

        Returns:
            Tuple[List[float], List[float]]: (UI1の操作時間リスト, UI2の操作時間リスト)
        """
        ui1_durations = []
        ui2_durations = []

        # questionnaire配下のui1, ui2ディレクトリを確認
        ui1_dir = self.base_dir / "questionnaire" / "ui1"
        ui2_dir = self.base_dir / "questionnaire" / "ui2"

        # UI1のタスク時間を集計
        for task_dir in ["task1", "task2"]:
            task_path = ui1_dir / task_dir
            if task_path.exists():
                for json_file in task_path.glob("*.json"):
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        duration = data.get("task_duration_sec")
                        if duration is not None:
                            ui1_durations.append(duration)

        # UI2のタスク時間を集計
        for task_dir in ["task1", "task2"]:
            task_path = ui2_dir / task_dir
            if task_path.exists():
                for json_file in task_path.glob("*.json"):
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        duration = data.get("task_duration_sec")
                        if duration is not None:
                            ui2_durations.append(duration)

        return ui1_durations, ui2_durations

    def plot_task_duration_comparison(
        self,
        ui1_durations: List[float],
        ui2_durations: List[float],
        participant_count: int,
        stats: Dict,
        output_filename: str = "task_duration_comparison.pdf"
    ):
        """
        UI1とUI2のタスク操作時間の箱ひげ図比較を作成

        Args:
            ui1_durations: UI1の操作時間リスト
            ui2_durations: UI2の操作時間リスト
            participant_count: 参加者数
            stats: 統計情報
            output_filename: 出力ファイル名
        """
        fig, ax = plt.subplots(figsize=(8, 6))

        # タイトルに統計情報を含める
        title_text = (
            f'タスク操作時間比較 (n={participant_count})\n'
            f'順序: UI1→UI2 {stats["ui1_first"]}名, UI2→UI1 {stats["ui2_first"]}名 | '
            f'好み: UI1 {stats["ui1_favorite"]}名, UI2 {stats["ui2_favorite"]}名'
        )
        fig.suptitle(
            title_text,
            fontsize=14,
            fontweight='bold',
            y=0.97,
            fontproperties=jp_font_prop
        )

        # データ準備
        data = [ui1_durations, ui2_durations]
        positions = [1, 2]

        # 箱ひげ図描画
        bp = ax.boxplot(
            data,
            positions=positions,
            widths=0.6,
            patch_artist=True,
            showmeans=True,
            meanprops=dict(marker='D', markerfacecolor='red', markersize=8)
        )

        # 色設定
        colors = ['#3498db', '#e74c3c']  # UI1: 青, UI2: 赤
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.6)

        # 軸設定
        ax.set_ylabel('操作時間(秒)', fontsize=12, fontweight='bold', fontproperties=jp_font_prop)
        ax.set_xticks(positions)
        ax.set_xticklabels(['UI1', 'UI2'], fontsize=12, fontweight='bold')

        # グリッド
        ax.yaxis.grid(True, linestyle='--', alpha=0.3)
        ax.set_axisbelow(True)

        # 統計情報を表示
        ui1_mean = np.mean(ui1_durations)
        ui1_median = np.median(ui1_durations)
        ui2_mean = np.mean(ui2_durations)
        ui2_median = np.median(ui2_durations)

        # 平均値と中央値をテキストで表示
        y_max = max(max(ui1_durations), max(ui2_durations))
        ax.text(1, y_max * 0.95, f'平均: {ui1_mean:.1f}秒\n中央値: {ui1_median:.1f}秒',
               ha='center', va='top', fontsize=10,
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
               fontproperties=jp_font_prop)
        ax.text(2, y_max * 0.95, f'平均: {ui2_mean:.1f}秒\n中央値: {ui2_median:.1f}秒',
               ha='center', va='top', fontsize=10,
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
               fontproperties=jp_font_prop)

        # 凡例を追加
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='#3498db', alpha=0.6, label='UI1'),
            Patch(facecolor='#e74c3c', alpha=0.6, label='UI2')
        ]
        ax.legend(handles=legend_elements, loc='upper left', fontsize=10)

        # レイアウト調整
        plt.tight_layout(rect=[0, 0, 1, 0.94])

        # 保存
        output_path = self.output_dir / output_filename
        plt.savefig(output_path, format='pdf', bbox_inches='tight', dpi=300)
        print(f"✅ グラフ保存完了: {output_path}")

        plt.close()

    def _print_statistics(
        self,
        ui1_data: List[List[int]],
        ui2_data: List[List[int]],
        n: int
    ):
        """統計情報を表示"""
        print("\n📊 統計情報:")
        print(f"{'=' * 60}")
        print(f"参加者数: n={n}")
        print(f"{'=' * 60}\n")

        for q_idx in range(len(ui1_data)):
            question_label = self.QUESTION_LABELS[q_idx] if q_idx < len(self.QUESTION_LABELS) else f"Q{q_idx + 1}"

            ui1_mean = np.mean(ui1_data[q_idx])
            ui1_median = np.median(ui1_data[q_idx])
            ui1_std = np.std(ui1_data[q_idx], ddof=1)

            ui2_mean = np.mean(ui2_data[q_idx])
            ui2_median = np.median(ui2_data[q_idx])
            ui2_std = np.std(ui2_data[q_idx], ddof=1)

            print(f"Q{q_idx + 1}: {question_label}")
            print(f"  UI1 - 平均: {ui1_mean:.2f}, 中央値: {ui1_median:.1f}, 標準偏差: {ui1_std:.2f}")
            print(f"  UI2 - 平均: {ui2_mean:.2f}, 中央値: {ui2_median:.1f}, 標準偏差: {ui2_std:.2f}")
            print()


def main():
    """メイン実行関数"""
    plotter = SurveyResultPlotter()
    plotter.plot_all_results()


if __name__ == "__main__":
    main()
