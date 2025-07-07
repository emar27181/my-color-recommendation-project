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

## 📁 コーディング・構成ルール

- **エラー状態でのコミットは禁止**  
  → 型エラー・ビルドエラーがない状態でコミットする。

- **依存パッケージの追加もコミット単位で管理**  
  → 1コミットにまとめず、意味のある変更単位で。

- **コード中の定数・共通仕様は統一管理**  
  → `constants/` ディレクトリなどにまとめておく。

---