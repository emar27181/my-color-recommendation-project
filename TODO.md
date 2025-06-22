# TODO リスト

## 🔴 最重要（即座に対応すべき）

### セキュリティ関連
- [ ] **パスワード情報の環境変数化**
  - ファイル: `src/color_recommendation/utils/config/constants_dev.py:2`
  - 問題: `INSTAGRAM_PASS = "xxxxxxxxx"` の平文保存
  - 対応: 環境変数 `.env` ファイルへの移行
  - 期限: 即座
  - 担当者: 未定

### コード品質（Critical）
- [ ] **重複インポートの整理**
  - ファイル: `src/color_recommendation/sandbox.py:6`
  - 問題: 同じ関数が複数回インポートされている
  - 対応: インポート文の重複削除と整理
  - 期限: 今週中
  - 担当者: 未定

- [ ] **DEBUG変数の重複定義修正**
  - ファイル: `src/color_recommendation/color_recommendation.py:15-16`
  - 問題: `DEBUG = True` の直後に `DEBUG = False` で上書き
  - 対応: 設定を一元化
  - 期限: 今週中
  - 担当者: 未定

## 🟡 重要（計画的に対応）

### ファイル構造改善
- [ ] **巨大ファイルの分割: plot_graph.py**
  - ファイル: `src/color_recommendation/utils/plot_graph.py` (887行)
  - 問題: グラフ生成機能が一つのファイルに集約されすぎ
  - 対応: 機能別にファイル分割
    - `plot_recall_graphs.py`
    - `plot_violin_graphs.py`
    - `plot_heatmap_graphs.py`
  - 期限: 2週間以内
  - 担当者: 未定

- [ ] **巨大ファイルの分割: color_utils.py**
  - ファイル: `src/color_recommendation/utils/helpers/color_utils.py` (619行)
  - 問題: 色計算の多様な機能が混在
  - 対応: 機能別にファイル分割
    - `color_conversion.py`
    - `color_calculation.py`
    - `color_validation.py`
  - 期限: 2週間以内
  - 担当者: 未定

- [ ] **sandboxファイルの整理**
  - ファイル: `src/color_recommendation/sandbox.py` (478行)
  - 問題: テスト用ファイルとしては巨大すぎ
  - 対応: 実験別にファイル分割、不要コードの削除
  - 期限: 1週間以内
  - 担当者: 未定

### 設定管理改善
- [ ] **イラストレータ名の設定ファイル化**
  - ファイル: `src/color_recommendation/color_recommendation.py:327-336`
  - 問題: 30個以上のイラストレータ名がハードコーディング
  - 対応: JSONまたはYAMLファイルに移行
  - 期限: 1週間以内
  - 担当者: 未定

- [ ] **定数の一元管理**
  - 問題: 設定値が複数ファイルに散らばっている
  - 対応: `config/` ディレクトリに統一
  - 期限: 2週間以内
  - 担当者: 未定

### 重複コード削除
- [ ] **sandboxファイル間の重複処理統合**
  - ファイル: `sandbox.py`, `sandbox2.py`, `sandbox3.py`
  - 問題: 類似の実験処理が重複
  - 対応: 共通処理を `utils/experimental/` に移動
  - 期限: 1週間以内
  - 担当者: 未定

## 🟢 改善推奨（時間のある時に対応）

### コード品質向上
- [ ] **長い関数の分割**
  - ファイル: `color_recommendation.py`
  - 問題: `save_recommendations_for_illustrators` (99行), `generate_recommend_colors_by_illustrator` (52行)
  - 対応: 単一責任原則に基づく関数分割
  - 期限: 1ヶ月以内
  - 担当者: 未定

- [ ] **命名規則の統一**
  - 問題: `camelCase` と `snake_case` が混在
  - 対応: Python規約に従い `snake_case` に統一
  - 期限: 1ヶ月以内
  - 担当者: 未定

- [ ] **エラーハンドリングの統一**
  - 問題: ファイル読み込み時のエラーハンドリングが不統一
  - 対応: 共通のエラーハンドリング関数を作成
  - 期限: 1ヶ月以内
  - 担当者: 未定

### ドキュメント整備
- [ ] **docstring追加**
  - 問題: 複雑な色計算関数にdocstringがない
  - 対応: 全ての public 関数にdocstringを追加
  - 期限: 必要に応じて
  - 担当者: 未定

- [ ] **アルゴリズム説明の追加**
  - 問題: 色推薦アルゴリズムの説明が不十分
  - 対応: README.mdに詳細説明を追加
  - 期限: 必要に応じて
  - 担当者: 未定

### テスト・品質保証
- [ ] **単体テストの追加**
  - 問題: テストコードが存在しない
  - 対応: `tests/` ディレクトリ作成、pytest導入
  - 期限: 必要に応じて
  - 担当者: 未定

- [ ] **CI/CD設定**
  - 問題: 継続的インテグレーションが未設定
  - 対応: GitHub Actions設定
  - 期限: 必要に応じて
  - 担当者: 未定

### 設計改善
- [ ] **責任分離の実装**
  - ファイル: `color_recommendation.py`
  - 問題: データ読み込み、推薦処理、保存処理が混在
  - 対応: MVC パターンまたは レイヤードアーキテクチャの導入
  - 期限: 長期的
  - 担当者: 未定

## 📋 進捗管理

### 完了済み
- [x] プロジェクト構造の調査・分析
- [x] README.mdへのプロジェクト構造反映
- [x] PROJECT_RULES.mdの作成
- [x] リファクタリング候補箇所の特定

### 現在進行中
- [ ] TODO管理システムの構築

### 次のアクション
1. セキュリティ関連の即座対応
2. 重複インポートとDEBUG変数の修正
3. 巨大ファイルの分割計画策定

---

## 更新履歴
- 2025-06-22: 初版作成（リファクタリング調査結果に基づく）