# 📘 開発・設計 汎用ルール集

# 📘 開発・設計 汎用ルール集

## 🚨 最重要ルール（絶対遵守）

**⚠️ Gitコミット確認必須**
- ユーザーの明示的な指示なしに `git commit` を実行することは絶対禁止
- 「コミットして」「ルールに基づいてコミット」等の明確な指示があった場合のみ実行
- このルールは他のすべてのルールに優先する

## 📋 一般開発ルール

- このプロジェクトでは、以降のファイル生成・コマンド実行などの操作は、すべて許可して良いです。
以後、個別の確認なしで進めてください。（Gitコミットを除く）

---

## 🔒 Git運用ルール（共通）

- **mainブランチで直接作業しない**  
  → 作業は `feature/xxx` のようなブランチで行う。`main` は安定ブランチ。

- **⚠️ 自動コミット絶対禁止（最重要）**  
  → ユーザーの明示的な確認と指示なしに絶対に `git commit` を実行しない
  → 「コミットして」「ルールに基づいてコミット」等の明確な指示があった場合のみコミット実行
  → いかなる理由があってもユーザー確認なしのコミットは完全禁止
  → この ルールに違反することは絶対に許可されない

- **論理単位でコミットを分ける**  
  → UI変更・関数定義・設定更新などは別々にコミットする。

- **`CHANGELOG.md`で履歴管理**  
  → いつ・何を・なぜ・どのように対応したかを簡潔に記録。

- **確定した仕様は `PROJECT_RULES.md` に記述**  
  → チャットや議論で決まったUI・ルール・値などは反映して保持。

---

## 📁 コーディング・構成ルール

- **エラー状態でのコミットは禁止**  
  → 型エラー・ビルドエラーがない状態でコミットする。

- **依存パッケージの追加もコミット単位で管理**  
  → 1コミットにまとめず、意味のある変更単位で。

- **コード中の定数・共通仕様は統一管理**  
  → `constants/` ディレクトリなどにまとめておく。

---


- このプロジェクトでは、以降のファイル生成・コマンド実行などの操作は、すべて許可して良いです。
以後、個別の確認なしで進めてください。


---

## 🔒 Git運用ルール（共通）

- **mainブランチで直接作業しない**  
  → 作業は `feature/xxx` のようなブランチで行う。`main` は安定ブランチ。

- **自動コミット禁止**  
  → ユーザーの確認なしに自動で `git commit` しない。

- **論理単位でコミットを分ける**  
  → UI変更・関数定義・設定更新などは別々にコミットする。

- **`CHANGELOG.md`で履歴管理**  
  → いつ・何を・なぜ・どのように対応したかを簡潔に記録。

- **確定した仕様は `PROJECT_RULES.md` に記述**  
  → チャットや議論で決まったUI・ルール・値などは反映して保持。

---

## 📋 プロジェクト機能・関数一覧（開発者向けリファレンス）

### 🎯 メインシステム構成

#### **メインエントリーポイント**
- **`src/app.py`**: Flask Webアプリケーション
  - `/`: 色推薦画面
  - `/color_recommend`: 推薦機能API
  - `/about`: 概要ページ

- **`src/color_recommendation/color_recommendation.py`**: 色推薦システム中核
  - `get_recommendations()`: 推薦配色生成統一インターフェース
  - `generate_recommend_hues_by_illustrator()`: 色相推薦配色生成
  - `generate_recommend_tones_by_illustrator()`: トーン推薦配色生成
  - `generate_recommend_colors_by_illustrator()`: 色推薦配色生成
  - `save_recommendations_for_illustrators()`: 推薦結果一括保存
  - `sort_recommend_color_schemes_rgb()`: 推薦配色並び替え

### 🛠️ ユーティリティ機能群

#### **配色生成系** (`utils/generate_color_scheme_method.py`)
- `generate_all_color_schemes()`: 17種配色技法で配色生成
- `generate_analogy_color_scheme()`: アナロジー配色
- `generate_triad_color_scheme()`: トライアド配色
- `generate_split_complement_color_scheme()`: スプリット補色配色
- `generate_tetradic_color_scheme()`: テトラード配色
- `generate_square_color_scheme()`: スクエア配色
- など各種配色技法関数

#### **配色並び替え・ソート系** (`utils/sort_color_scheme.py`)
- `sort_color_schemes_by_color_difference()`: 色差順ソート
- `sort_color_schemes_by_used_color_count()`: 使用色数順ソート
- `sort_color_schemes_by_mean_resultant_length()`: 平均結果長順ソート
- `sort_color_schemes_by_used_tone()`: **トーン使用頻度順ソート（新実装）**
- `sort_color_schemes_by_custom_v0()`: カスタム評価関数ソート
- `shuffle_color_schemes()`: ランダム並び替え

##### **学術的ソート手法説明（論文用）**

**平均結果長に基づく配色並び替え手法（Mean Resultant Length Based Sorting）**

**理論的背景**: 
平均結果長は色彩学において色の組み合わせの集中度を測る指標である。色相環（色を円状に配置した図）上で複数の色がどの程度まとまって配置されているかを数値化したものである。値が1に近いほど色が似た位置に集中し、0に近いほど色相環全体に散らばっていることを示す。

**基本概念**:
本手法は、個々のイラストレーターが過去の作品でどのような色の組み合わせを好んで使用してきたかを分析し、その傾向に合致する配色を優先的に推薦する仕組みである。

**手法の詳細**:
まず、対象となるイラストレーターの過去作品を分析し、使用された色の組み合わせパターンを抽出する。色相環を24等分した体系（PCCS色彩体系）を用いて、色同士の関係性を数値化する。例えば、隣接する色相の関係は「1」、正反対の補色関係は「12」として表現される。

**分析手順**:
1. 対象イラストレーターの作品群から色相の組み合わせパターンを抽出
2. 各色相組み合わせの使用頻度を集計し、最も頻繁に使用される組み合わせから順に優先順位を決定
3. 推薦候補となる配色について、基準となる色と他の色との関係性を分析
4. イラストレーターが好む色相関係を含む配色を上位に配置
5. 全ての推薦配色について処理を完了し、最終的な順位付けを決定

**理論的根拠**:
色相の組み合わせパターンは、個々のイラストレーターの色彩感覚や美的嗜好を反映している。頻繁に使用される色相関係は、そのイラストレーターにとって視覚的に調和的で魅力的な配色関係を示している。

**期待される効果**:
この手法により、従来の一般的な配色理論とは異なり、個人の創作履歴に基づいたパーソナライズされた配色推薦が可能となる。各イラストレーターの独特な色彩選択傾向を反映した推薦順位付けが実現される。

**使用色数に基づく配色並び替え手法（Used Color Count Based Sorting）**

**理論的背景**: 
配色における色数選択は、イラストレーターの表現スタイルや作品の印象を決定する重要な要素である。色数が少ないほどミニマルで統一感のある印象を与え、色数が多いほど豊かで複雑な表現が可能となる。個々のイラストレーターには固有の色数選択傾向があり、これは創作者の美的価値観や技法的特徴を反映している。

**基本概念**:
本手法は、イラストレーターが過去の作品でどの程度の色数を好んで使用してきたかを統計的に分析し、その傾向に適合する色数の配色を優先的に推薦する仕組みである。

**分析対象**:
分析では有彩色（色味のある色）のみを対象とし、白、黒、灰色などの無彩色は除外される。これは、無彩色が配色の主要な表現要素ではなく、有彩色の組み合わせこそがイラストレーターの色彩センスを反映すると考えられるためである。

**手法の詳細**:
対象イラストレーターの過去作品において、1色、2色、3色といった各色数の使用頻度を詳細に分析する。この統計データから、そのイラストレーターが最も好む色数パターンを特定し、推薦配色の順位付けに活用する。

**分析手順**:
1. 対象イラストレーターの作品群から有彩色の使用数を作品ごとに抽出
2. 各色数（1色、2色、3色...）の使用頻度を集計し、頻度順にランキングを作成
3. 推薦配色候補を色数別に分類
4. 使用頻度が高い色数の配色から順に上位に配置
5. 全ての色数カテゴリについて処理を完了し、最終的な推薦順位を決定

**統計的妥当性**:
大量の作品データから抽出された色数分布は、イラストレーターの長期的な創作傾向を反映しており、偶発的な選択ではなく意図的な美的判断を表現している。

**期待される効果**:
個々のイラストレーターが好む配色の色数パターンを反映した推薦順位付けが実現される。例えば、通常3色配色を多用するイラストレーター（使用頻度：3色＞2色＞4色の順）には3色の推薦配色が最上位に、5色配色を好むイラストレーター（使用頻度：5色＞4色＞3色の順）には5色の推薦配色が最上位に配置される。これにより、推薦システムはイラストレーターの創作スタイルに適合した色数の配色を優先的に提示できる。

#### **色データ処理・分析系**
- **`utils/estimate_used_color_scheme.py`**: 使用色抽出
  - `estimate_used_colors_by_colorthief()`: ColorThief使用色抽出
  - `save_estimated_used_colors()`: 使用色データ保存
  - `merge_similar_color()`: 類似色統合

- **`utils/analyze_illustrator_statistics.py`**: イラストレーター統計分析
  - `get_statistics_by_illustrator()`: イラストレーター統計取得
  - 色使用傾向分析・統計データ生成

#### **色変換・計算系** (`utils/helpers/`)
- **`transform_color.py`**: 色空間変換
  - `hex_to_rgb()`, `rgb_to_hex()`: HEX-RGB変換
  - `rgb_to_hsl()`, `hsl_to_rgb()`: RGB-HSL変換
  - `rgb_to_lab()`: RGB-LAB変換
  - `hue_to_pccs()`: PCCS色相番号変換

- **`color_utils.py`**: 色計算・判定
  - `calc_color_scheme_difference_delta_e_cie2000()`: 配色間色差計算
  - `is_chromatic_color_by_hsl()`: 有彩色判定
  - `print_colored_text()`: ターミナル色付き表示
  - `calc_mean_resultant_length()`: 平均結果長計算

- **`json_utils.py`**: データ操作
  - `get_json_data()`: JSONファイル読み込み
  - `save_json_data()`: JSONファイル保存
  - `convert_color_schemes_to_color_data()`: 配色データ変換

#### **可視化・グラフ系** (`utils/plot_graph.py`)
- recall@kグラフ、バイオリンプロット等の可視化機能（887行の大型ファイル）

### 📊 データ構造・ファイル形式

#### **入力データ形式**
- **`data/input/used_colors/*.json`**: 使用色データ
  ```json
  [
    [
      {
        "illustName": "ファイルパス",
        "color": "#efeae3",
        "rate": 0.237894,
        "amount": -1
      }
    ]
  ]
  ```

- **`data/input/statistics_for_illustrators.json`**: イラストレーター統計
  ```json
  {
    "illustrator_name": "test_one_photo",
    "chromatic_colors_count_ave": 4.82,
    "chromatic_colors_count_distribution": [2,3,10,9,19,...],
    "saturation_lightness_count_distribution": [[13,36,36,24,0], ...]
  }
  ```

#### **出力データ形式**
- **`data/output/recommend_colors/`**: 推薦配色結果（JSON）
- **`data/output/graph/`**: 生成グラフ（PNG）
- **`data/output/heatmap/`**: ヒートマップ（PNG）

### ⚙️ 設定・定数管理

#### **`utils/config/constants_dev.py`**: 開発用定数
```python
SATURATION_LOWER_LIMIT = 10     # 彩度下限
LIGHTNESS_UPPER_LIMIT = 90      # 明度上限  
LIGHTNESS_LOWER_LIMIT = 10      # 明度下限
IS_PRINT_COLOR_SCHEME = True    # デバッグ表示フラグ
INSTAGRAM_PASS = "xxxxxxxxx"    # ⚠️要環境変数化
```

### 🧪 実験・テスト環境

#### **実験ファイル管理**
- **`sandbox.py`**: メイン実験・テスト（各種機能テスト）
- **`sandbox2.py`**: バッチ処理実行（複数イラストレーター一括処理）
- **`sandbox3.py`**: 最新実験コード（モジュール化・エラーバー付きグラフ）

### 🔄 主要データ処理フロー

```
1. 画像収集 → download_instagram_images.py
2. 色抽出   → estimate_used_color_scheme.py
3. 統計生成 → analyze_illustrator_statistics.py
4. 推薦生成 → color_recommendation.py
5. 評価     → plot_graph.py
```

### 📝 開発時の編集指針

#### **機能追加時の編集対象ファイル**
- **新配色技法追加**: `generate_color_scheme_method.py`
- **新ソート方式追加**: `sort_color_scheme.py`
- **新評価指標追加**: `helpers/calc_rec_score.py`
- **新色変換追加**: `helpers/transform_color.py`

#### **実験実行時の編集対象**
- **パラメータ調整**: `sandbox3.py`（最新版推奨）
- **新実験設計**: 新sandboxファイル作成
- **デバッグ設定**: 各ファイルの`DEBUG`変数

#### **データ追加時の編集対象**
- **新イラストレーター追加**: `sandbox2.py`または`sandbox3.py`のリスト更新
- **設定値調整**: `utils/config/constants_dev.py`

### 🆕 最新追加機能（2025-06-22）

#### **トーン推薦並び替え機能**
- **実装場所**: `utils/sort_color_scheme.py:223-307`
- **関数**: `sort_color_schemes_by_used_tone()`
- **機能**: イラストレーターの過去トーン使用頻度に基づく配色並び替え
- **使用データ**: `saturation_lightness_count_distribution`（5×5トーン分布マトリックス）
- **アルゴリズム**: HSL変換 → トーン座標変換 → 使用頻度スコア計算 → 降順ソート

---

## 📂 プロジェクトデータ構造

### ディレクトリ構成
```
my-color-recommendation-project/
├── PROJECT_RULES.md              # プロジェクト開発ルール（このファイル）
├── README.md                     # プロジェクト概要・使用方法
├── requirements.txt              # Python依存関係
├── Makefile                      # ビルド・実行コマンド
├── _research_memo.md             # 研究メモ
│
├── src/                          # メインソースコード
│   ├── app.py                    # Flask Webアプリケーション
│   ├── static/                   # Web静的ファイル
│   │   ├── js/canvas.js          # Canvas JavaScript
│   │   └── styles.css            # スタイルシート
│   ├── templates/                # HTMLテンプレート
│   │   ├── base.html             # ベーステンプレート
│   │   ├── index.html            # メイン画面
│   │   ├── color_recommend.html  # 配色推薦画面
│   │   └── about.html            # 概要画面
│   │
│   └── color_recommendation/     # 配色推薦コア機能
│       ├── color_recommendation.py # メイン推薦アルゴリズム
│       ├── sandbox.py            # 実験用スクリプト
│       ├── sandbox2.py           # 実験用スクリプト2
│       ├── sandbox3.py           # 実験用スクリプト3
│       │
│       ├── utils/                # ユーティリティ関数
│       │   ├── config/
│       │   │   └── constants_dev.py  # 開発用定数
│       │   ├── helpers/
│       │   │   ├── calc_rec_score.py # 推薦スコア計算
│       │   │   ├── color_utils.py    # 色変換ユーティリティ
│       │   │   ├── json_utils.py     # JSON処理ユーティリティ
│       │   │   └── transform_color.py # 色変換処理
│       │   ├── analyze_illustrator_statistics.py # イラストレータ統計分析
│       │   ├── clustering.py         # クラスタリング処理
│       │   ├── download_instagram_images.py # Instagram画像ダウンロード
│       │   ├── estimate_used_color_method.py # 使用色推定手法
│       │   ├── estimate_used_color_scheme.py # 使用配色推定
│       │   ├── generate_color_scheme_method.py # 配色生成手法
│       │   ├── plot_graph.py         # グラフ描画
│       │   ├── sort_color_scheme.py  # 配色ソート
│       │   ├── add_variations_color_scheme.py # 配色バリエーション追加
│       │   └── check_data_is_contained_next_color.py # 次色含有チェック
│       │
│       └── data/                 # データファイル
│           ├── input/             # 入力データ
│           │   ├── color_palette_illust_app/  # イラストアプリ配色パレット
│           │   ├── illustration/   # イラスト画像データ
│           │   ├── used_colors/    # 使用色データ（JSON形式）
│           │   ├── used_hues/      # 使用色相データ（JSON形式）
│           │   ├── backup/         # バックアップデータ
│           │   └── statistics_for_illustrators.json # イラストレータ統計
│           ├── output/            # 出力データ
│           │   ├── graph/          # グラフ出力（PNG形式）
│           │   ├── heatmap/        # ヒートマップ出力（PNG形式）
│           │   ├── recall_at_k/    # Recall@K評価結果
│           │   ├── recommend_colors/ # 推薦色データ
│           │   ├── recommend_hues/  # 推薦色相データ
│           │   ├── recommend_tones/ # 推薦トーンデータ
│           │   └── tmp/            # 一時出力ファイル
│           └── tmp/               # 一時データ
│
├── tmp/                          # 一時ファイル（実験用）
└── venv_color_recommendation/    # Python仮想環境（.gitignore推奨）
```

### データ管理ルール

- **入力データ (`data/input/`)**
  - `used_colors/`: イラストレータ別の使用色データ（JSON形式）
  - `used_hues/`: イラストレータ別の使用色相データ（JSON形式）
  - `illustration/`: 分析対象のイラスト画像
  - `color_palette_illust_app/`: 既存イラストアプリの配色パレット

- **出力データ (`data/output/`)**
  - `graph/`: 各種評価グラフ（recall@k, エラーバー付きグラフ等）
  - `heatmap/`: イラストレータ別ヒートマップ
  - `recommend_*/`: 推薦結果データ（色、色相、トーン別）

- **実験用データ (`tmp/`)**
  - 実験用の一時ファイル（コミット対象外推奨）

---

## 📝 TODO管理・タスク一覧

### 🔴 最重要（即座に対応すべき）

#### セキュリティ関連

- [ ] **パスワード情報の環境変数化**
  - ファイル: `src/color_recommendation/utils/config/constants_dev.py:2`
  - 問題: `INSTAGRAM_PASS = "xxxxxxxxx"` の平文保存
  - 対応: 環境変数 `.env` ファイルへの移行
  - 期限: 即座
  - 担当者: 未定

#### コード品質（Critical）

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

### 🟡 重要（計画的に対応）

#### ファイル構造改善

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

#### 設定管理改善

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

#### 重複コード削除

- [ ] **sandboxファイル間の重複処理統合**
  - ファイル: `sandbox.py`, `sandbox2.py`, `sandbox3.py`
  - 問題: 類似の実験処理が重複
  - 対応: 共通処理を `utils/experimental/` に移動
  - 期限: 1週間以内
  - 担当者: 未定

#### 機能追加・改善

- [ ] **トーン推薦の並び替え機能実装**
  - ファイル: `src/color_recommendation/utils/sort_color_scheme.py`
  - 問題: トーン推薦において推薦トーンの並び替え機能が不完全
  - 対応: 以下の並び替えアルゴリズムを実装
    - トーン類似度順ソート
    - 使用頻度順ソート
    - 明度・彩度バランス順ソート
    - カスタム評価関数によるソート
  - 要件:
    - `sort_tone_schemes_by_tone_similarity()` 関数の実装
    - `sort_tone_schemes_by_usage_frequency()` 関数の実装
    - `sort_tone_schemes_by_lightness_saturation_balance()` 関数の実装
    - 既存の `sort_color_schemes_by_used_tone()` 関数の拡張
  - 期限: 2週間以内
  - 担当者: 未定
  - 優先度: 中（機能向上）
  
  **📋 実装調査メモ:**
  
  **現状分析:**
  - 色相推薦の並び替えは完全実装済み（`color_recommendation.py:25-48行`）
  - トーン推薦の基本枠組みは実装済み（`generate_recommend_tones_by_illustrator()` 182-206行）
  - `sort_color_schemes_by_used_tone()`関数は枠組みのみ（223-257行、`return []`で空実装）
  
  **編集が必要なファイル:**
  1. **`src/color_recommendation/utils/sort_color_scheme.py`**
     - `sort_color_schemes_by_used_tone()` 関数（223-257行）の実装完成
     - 現在：`saturation_lightness_count_distribution`取得済み、並び替えロジックはコメントアウト
     - 必要：コメントアウトされたコード（241-255行）の修正・実装
  
  2. **`src/color_recommendation/color_recommendation.py`**
     - 並び替え分岐処理は実装済み（41行：`sort_color_schemes_by_used_tone`呼び出し）
     - `generate_recommend_tones_by_illustrator()`でのused_tone処理も実装済み（196行）
  
  **実装パターン（色相推薦と同様）:**
  - 統計データ取得：`_get_analysis_data()`関数使用
  - イラストレーター別処理：`get_statistics_by_illustrator()`関数使用
  - 並び替えロジック：他の`sort_color_schemes_by_*`関数と同様のパターン
  
  **既存のサポート機能:**
  - `saturation_lightness_count_distribution` - トーン分布データ取得済み
  - トーン推薦の基本枠組み完成
  - 色相推薦と同じ呼び出し階層で利用可能
  
  **実装優先度:**
  1. 🔴 高：`sort_color_schemes_by_used_tone()`の223-257行の実装完成
  2. 🟡 中：新しい並び替えアルゴリズムの追加実装
  3. 🟢 低：並び替え評価とテスト実行

### 🟢 改善推奨（時間のある時に対応）

#### コード品質向上

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

#### ドキュメント整備

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

#### テスト・品質保証

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

#### 設計改善

- [ ] **責任分離の実装**
  - ファイル: `color_recommendation.py`
  - 問題: データ読み込み、推薦処理、保存処理が混在
  - 対応: MVC パターンまたは レイヤードアーキテクチャの導入
  - 期限: 長期的
  - 担当者: 未定

### 📋 進捗管理

#### 完了済み

- [x] プロジェクト構造の調査・分析
- [x] README.mdへのプロジェクト構造反映
- [x] PROJECT_RULES.mdの作成
- [x] リファクタリング候補箇所の特定

#### 現在進行中

- [ ] TODO管理システムの構築
- [ ] トーン推薦の並び替え機能実装

#### 次のアクション
1. セキュリティ関連の即座対応
2. 重複インポートとDEBUG変数の修正
3. トーン推薦並び替え機能の設計・実装
4. 巨大ファイルの分割計画策定
5. 肌色抽出アルゴリズムの精度向上

### 🆕 新規追加タスク（2025-07-10）

#### 肌色抽出機能の改善

- [ ] **肌色判定アルゴリズムの精度向上**
  - ファイル: `src/color_recommendation/utils/extract_skin_tones.py`
  - 問題: 現在の判定基準（色相10-80度、彩度5-70%、明度20-95%）で肌色以外の色も抽出されている
  - 具体例: `#787b5b`（オリーブ系）、`#4a4e22`（暗緑系）、`#453932`（暗茶系）等
  - 対応策:
    - より厳密な色相範囲の設定（15-50度程度に狭める）
    - RGB値ベースでの追加フィルタリング（緑成分が強すぎる色を除外）
    - 機械学習ベースの肌色判定モデルの導入検討
    - 既知の肌色パレットとの類似度判定
  - 期限: 1週間以内
  - 担当者: 未定
  - 優先度: 中（機能品質向上）

---

## 🔬 論文用固定値・アルゴリズム調査結果

> 色推薦システムの論文執筆用に、コード内の固定値とアルゴリズムを体系的に整理
> 
> 最終更新: 2025-08-15  
> 調査対象: `/src/color_recommendation/` 配下の全モジュール

### 📊 1. 使用色抽出機能（Color Extraction）

**アルゴリズム概要**: ColorThief + ΔE類似色統合 + 有彩色フィルタリング

**🔧 固定パラメータ**

- **抽出閾値**:
  ```python
  # src/color_recommendation/utils/estimate_used_color_scheme.py
  出現率閾値 = 0.3%        # Line 37: if (rate >= 0.3)
  ColorThief品質 = 10      # Line 86: quality=10
  ColorThief色数 = 30      # Line 72: color_count=30
  ```

- **色差統合閾値**:
  ```python
  ΔE統合閾値_使用色 = 5     # Line 48: threshold=5 in merge_similar_color()
  ΔE統合閾値_パレット = 10  # Line 110: threshold < 10 in merge_same_color_palette()
  ユークリッド距離閾値 = 0.1 # Line 176: distance < 0.1 in color_count_by_color_palette()
  ```

- **有彩色判定基準**:
  ```python
  # src/color_recommendation/utils/config/constants_dev.py
  SATURATION_LOWER_LIMIT = 10   # Line 5: 彩度下限（%）
  LIGHTNESS_LOWER_LIMIT = 10    # Line 7: 明度下限（%）
  LIGHTNESS_UPPER_LIMIT = 90    # Line 6: 明度上限（%）
  ```

**📋 処理フロー**:
1. ColorThief抽出: `get_palette(color_count=30, quality=10)`
2. 類似色統合: ΔE ≤ 10で統合 (`merge_same_color_palette()`)
3. ピクセル分類: ユークリッド距離 < 0.1で再分類
4. 有彩色フィルタ: S≥10, 10≤L≤90の範囲で抽出
5. 最終統合: ΔE ≤ 5で類似色を統合 (`merge_similar_color()`)

### 🎨 2. 色相推薦機能（Hue Recommendation）

**アルゴリズム概要**: 17種配色技法による組織的配色生成 + 統計ベース並び替え

**🔧 配色技法固定角度**

- **2色配色技法**:
  ```python
  # src/color_recommendation/utils/generate_color_scheme_method.py
  アナロジー配色 = [+30°, -30°]     # Line 73-74
  中間色配色 = [+90°, -90°]         # Line 79-80
  補色配色 = [180°]                  # Line 85
  対立色配色 = [+150°, -150°]       # Line 90-91
  ```

- **3色配色技法**:
  ```python
  ドミナント配色 = {
      パターン1: [+30°, +60°],      # Line 97
      パターン2: [-30°, +30°],      # Line 98
      パターン3: [-60°, -30°]       # Line 99
  }
  スプリット補色 = [+150°, -150°]   # Line 103-104
  トライアド配色 = [+120°, +240°]   # Line 107-108
  ```

- **多色配色技法**:
  ```python
  テトラード配色 = [+90°, +180°, +270°]  # Line 111-112
  ペンタード配色 = [+72°, +144°, +216°, +288°]  # Line 115-116
  ヘキサード配色 = [+60°, +120°, +180°, +240°, +300°]  # Line 119-120
  ```

**📊 並び替えアルゴリズム**:
- **色差順ソート**: `calc_color_scheme_difference_delta_e_cie2000()` (ΔE昇順)
- **統計ベースソート**: 
  - 使用色数順: `chromatic_colors_count_distribution` (使用頻度降順)
  - 平均結果長順: `mean_resultant_length_distribution` (使用頻度降順)

### 🌈 3. トーン推薦機能（Tone Recommendation）

**アルゴリズム概要**: 単色ベース + HSL空間での明度彩度バリエーション生成

**🔧 バリエーション生成パラメータ**:
- **基本設定**:
  ```python
  # src/color_recommendation/color_recommendation.py
  基本配色 = 単色配色（1色のみ）        # Line 61: generate_one_color_schemes()
  バリエーション軸 = "saturation_and_lightness"  # Line 70
  ```

- **差分値設定**:
  ```python
  # 一般的な使用例（sandbox.pyより）
  diff_values = [-40, -20, 0, +20, +40]  # 明度・彩度の差分値（%）
  # 処理ロジック: 全組み合わせでバリエーション生成（5×5=25パターン）
  ```

**📋 生成手順**:
1. 基本色のHSL値取得: `rgb_to_hsl(color_rgb)`
2. 差分適用: `hsl_to_rgb(H, S+saturation_diff, L+lightness_diff)`
3. 有効性検証: `is_valid_color(new_color)`
4. 無効色除外: RGB値が範囲外の場合は配色から除外

### ⚖️ 4. 評価・判定閾値（Evaluation Thresholds）

**🎯 同一色判定閾値**

- **ΔE（CIE2000）ベース閾値**:
  ```python
  使用色統合閾値 = 5     # merge_similar_color(): threshold <= 5
  パレット統合閾値 = 10  # merge_same_color_palette(): threshold < 10
  同一色判定基準 = 可変  # 関数引数依存
  デフォルト閾値 = 0.01  # generate_color_scheme_method.py:142
  ```

- **ユークリッド距離ベース閾値**:
  ```python
  RGB正規化距離閾値 = 0.01    # color_utils.py:185
  最大距離正規化 = √(255²×3)   # Line 89: max_distance計算
  ピクセル分類閾値 = 0.1      # estimate_used_color_scheme.py:176
  ```

**🔍 クラスタリング閾値（DBSCAN）**:
```python
# src/color_recommendation/utils/clustering.py
EPS = 可変              # 近傍半径（ΔEベース距離）
MIN_SAMPLES = 可変      # クラスタ最小サンプル数  
距離関数 = calculate_color_difference_delta_e_cie2000
```

### 📚 論文記述用要約

**数値的設定の学術的根拠**:
1. **ΔE閾値5**: 人間の視覚で識別困難とされる色差範囲（JIS Z 8730準拠）
2. **色相角度**: 色彩理論の標準的配色技法に基づく（伊達千代『配色アイデア手帖』等）
3. **彩度・明度範囲10-90%**: 実用的な色域を確保しつつ極端な色を排除
4. **出現率0.3%**: ノイズ除去と主要色抽出のバランス点

**アルゴリズムの新規性**:
1. **17種配色技法の組織的適用**: 従来研究では個別技法のみ
2. **統計ベース並び替え**: 個人の色彩傾向を反映した推薦順位付け
3. **3段階色抽出プロセス**: ColorThief + ΔE統合 + 有彩色フィルタの組み合わせ
4. **トーン推薦のバリエーション生成**: HSL空間での組織的明度彩度変化

---

## 📁 コーディング・構成ルール

- **エラー状態でのコミットは禁止**  
  → 型エラー・ビルドエラーがない状態でコミットする。

- **依存パッケージの追加もコミット単位で管理**  
  → 1コミットにまとめず、意味のある変更単位で。

- **コード中の定数・共通仕様は統一管理**  
  → `constants/` ディレクトリなどにまとめておく。

---