## TODO
（現在タスクなし）

## DONE
- グラフをpdfで生成する（2026-01-08完了）
    - 現在は保存自体は出来ているものの文字が透明で見えていない → 解決済み
    - seabornの設定上書き問題を解決し、全グラフでPDF出力時に文字が正しく表示されるよう修正
    - `plot_graph.py`と`plot_survey_results_extracted.py`で背景色・文字色を明示的に設定
    - コミット: f9417f5 "修正: PDF出力グラフの文字透明化問題を根本的に解決"

- 色の推薦機構を調査して流れをまとめる（2026-01-08完了）
    - 使用配色の抽出、使用割合の抽出、推薦配色の生成、推薦順序計算、評価の全フローを詳細調査
    - 17種配色技法、6種並び替え方式の実装と数式表現を記載
    - すべての設定値・閾値を具体的な数値で明記
    - 出力ファイル: `COLOR_RECOMMENDATION_SYSTEM_ANALYSIS.md`

- TaskA/TaskBでのUI1/UI2比較分析（2026-01-08完了）
    - TaskA（キャラクター塗り）とTaskB（ロゴ塗り）の所要時間をUI1/UI2で比較
    - 統計的検定（t検定）を実施し、有意差を分析
    - 分析結果: TaskA、TaskBともに有意差なし（p>0.05）
    - 出力ファイル:
        - `src/color_recommendation/utils/analyze_task_ui_comparison.py`
        - `src/color_recommendation/data/output/experiment_analysis/task_ui_comparison.pdf`
        - `src/color_recommendation/data/output/experiment_analysis/task_ui_analysis_report.md`