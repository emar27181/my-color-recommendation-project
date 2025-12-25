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
  - `save_statistics_for_illustrators()`: 統計データ一括保存
  - `_extract_statistics_by_illustrator()`: 個別統計データ抽出
  - `_get_saturation_lightness_count_distribution()`: 明度彩度分布集計（**2025-09-05修正：出現率考慮**）
  - 色使用傾向分析・統計データ生成

- **`utils/extract_metadata_values.py`**: Instagram投稿メタデータ抽出・分析（**2025-09-08新規追加**）
  - `extract_metadata_from_json()`: .json.xzファイルから投稿メタデータ抽出
  - `get_metadata_for_image()`: 画像ファイルに対応するメタデータ取得
  - `get_all_metadata_by_illustrator()`: イラストレーター全投稿メタデータ取得
  - `get_engagement_statistics()`: エンゲージメント統計分析（いいね・コメント）
  - `get_popular_hashtags()`: 人気ハッシュタグ分析
  - `analyze_posting_patterns()`: 投稿パターン分析（時間帯・曜日）

- **`utils/extract_top_liked_images.py`**: 上位いいね画像抽出・コピー機能（**2025-09-08新規追加**）
  - `copy_top_liked_images_by_illustrator()`: イラストレーター別上位N枚画像コピー
  - `copy_all_illustrators_top_images()`: 全イラストレーター一括処理
  - `save_summary_report()`: 抽出結果サマリーレポート生成

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

- **`path_utils.py`**: パス管理ユーティリティ（**2025-09-08新規追加**）
  - `PathResolver`: Flask GUI・通常実行両対応の動的パス解決クラス
  - `get_used_colors_path()`, `get_used_hues_path()`: 使用色・色相データパス取得
  - `get_illustration_path()`, `get_statistics_path()`: イラスト・統計データパス取得
  - `get_output_path()`: 出力ディレクトリパス取得（推薦配色・グラフ・ヒートマップ等）
  - Flask GUI実行時（`src/`から実行）と通常実行（プロジェクトルートから実行）の両方に対応

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
- **`data/output/top_liked_images/`**: 上位いいね画像コレクション（**2025-09-08新規追加**）
  - `{illustrator_name}/`: イラストレーター別ディレクトリ
  - `rank_{順位:02d}_{いいね数:05d}_likes_{投稿日時}.jpg`: 画像ファイル（命名規則）
- **`data/output/top_liked_images_summary.json`**: 抽出結果サマリー（**2025-09-08新規追加**）
  ```json
  {
    "total_illustrators": 36,
    "total_images_copied": 76,
    "top_performers": [
      {"name": "oz_yarimasu", "max_likes": 653310, "avg_likes": 302960.7}
    ],
    "illustrator_details": {...}
  }
  ```

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
- **`run_extract_all_top_images.py`**: 上位いいね画像一括抽出スクリプト（**2025-09-08新規追加**）

### 🔄 主要データ処理フロー

```
1. 画像収集     → download_instagram_images.py
2. 色抽出       → estimate_used_color_scheme.py
3. 統計生成     → analyze_illustrator_statistics.py
4. 推薦生成     → color_recommendation.py
5. 評価         → plot_graph.py
6. メタデータ分析 → extract_metadata_values.py (2025-09-08新規追加)
7. 上位画像抽出  → extract_top_liked_images.py (2025-09-08新規追加)
```

#### **新規追加処理フロー（メタデータ活用系）**
```
A. エンゲージメント分析フロー:
   illustration/*.json.xz → extract_metadata_values.py → 統計分析結果

B. 人気画像抽出フロー:
   メタデータ分析 → extract_top_liked_images.py → top_liked_images/ + サマリー
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

### 📊 統計データ取得・集計システム（詳細実装）

#### **統計データ生成フロー**
1. **データソース**: `data/input/used_hues/*.json` + `data/input/used_colors/*.json`
2. **集計処理**: `_extract_statistics_by_illustrator(illustrator_name)`
3. **保存**: `save_statistics_for_illustrators(illustrator_list)` → `statistics_for_illustrators.json`

#### **統計データの種類と取得方法**

**🎨 色数統計**:
```python
# 有彩色・無彩色の平均使用数
chromatic_colors_count_ave = chromatic_colors_count_sum / len(data)
achromatic_colors_count_ave = achromatic_colors_count_sum / len(data)

# 有彩色・無彩色の使用率
chromatic_colors_rate_ave = 1 - (achromatic_colors_rate_sum / len(data))
achromatic_colors_rate_ave = achromatic_colors_rate_sum / len(data)

# 有彩色使用数分布（0色〜19色の頻度）
chromatic_colors_count_distribution[chromatic_colors_count] += 1
```

**🌈 色相統計**:
```python
# PCCS色相番号使用頻度分布（24色相）
used_pccs_count_sum_distribution[pccs] += 1

# 使用色相の出現率分布（360度）
used_hues_rate_sum_distribution[used_hue_rate[0] % 360] += used_hue_rate[1]
```

**📐 平均結果長統計**:
```python
# 平均結果長計算（色相の集中度指標）
mean_resultant_length_sum += _mean_resultant_length(used_chromatic_hues)

# 平均結果長の分布（12段階）
mean_resultant_index = round(_mean_resultant_length(used_chromatic_hues) * DIV_NUMBER)
mean_resultant_length_sum_distribution[mean_resultant_index] += 1
```

**🎯 明度彩度分布統計**（**2025-09-05修正版**）:
```python
# 出現率考慮の明度彩度分布集計
def _get_saturation_lightness_count_distribution(illustrator_name, illust_name, index_num):
    # 5×5マトリックス（DIVIDE_NUM=4）
    saturation_lightness_count_distribution = [[0 for _ in range(DIVIDE_NUM + 1)] for _ in range(DIVIDE_NUM + 1)]
    
    for used_color_info in used_colors_info:
        used_color_rate = used_color_info['rate']  # 🆕出現率取得
        used_color_hsl = rgb_to_hsl(hex_to_rgb(used_color_info['color']))
        
        # インデックス計算（0-4）
        saturation_index = round(used_color_hsl[1] / (100 / DIVIDE_NUM))
        lightness_index = round(used_color_hsl[2] / (100 / DIVIDE_NUM))
        
        # 🆕出現率で重み付けカウント
        saturation_lightness_count_distribution[lightness_index][saturation_index] += used_color_rate
```

#### **統計データの活用方法**

**🔄 推薦配色並び替え**:
```python
# 使用色数順ソート
sort_color_schemes_by_used_color_count(color_schemes, chromatic_colors_count_distribution)

# 平均結果長順ソート  
sort_color_schemes_by_mean_resultant_length(color_schemes, mean_resultant_length_distribution)

# トーン使用頻度順ソート
sort_color_schemes_by_used_tone(color_schemes, saturation_lightness_count_distribution)
```

#### **データ実行・保存方法**

**手動実行**:
```python
# sandbox2.py の136行目のコメントを外す
save_statistics_for_illustrators(illustrator_list)

# または直接実行
from utils.analyze_illustrator_statistics import save_statistics_for_illustrators
illustrator_list = ['amao_1015', 'mika_pikazo_mpz']
save_statistics_for_illustrators(illustrator_list)
```

**データアクセス**:
```python
# 個別統計データ取得
stats = get_statistics_by_illustrator('amao_1015', 'all')
tone_dist = get_statistics_by_illustrator('amao_1015', 'saturation_lightness_count_distribution')
```

### 🆕 最新追加機能（2025-06-22）

#### **トーン推薦並び替え機能**
- **実装場所**: `utils/sort_color_scheme.py:223-307`
- **関数**: `sort_color_schemes_by_used_tone()`
- **機能**: イラストレーターの過去トーン使用頻度に基づく配色並び替え
- **使用データ**: `saturation_lightness_count_distribution`（5×5トーン分布マトリックス）
- **アルゴリズム**: HSL変換 → トーン座標変換 → 使用頻度スコア計算 → 降順ソート

### 🔧 最新修正（2025-09-05）

#### **明度彩度分布集計の出現率考慮修正**
- **問題**: 従来は色の種類数のみカウント（背景色も装飾色も同じ重み）
- **修正**: 色の出現率（rate）を考慮した重み付きカウントに変更
- **影響**: より正確な色使用傾向の統計データを生成
- **修正ファイル**: `utils/analyze_illustrator_statistics.py:63-66, 70-73`

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

- [ ] **PDF出力グラフの文字色表示問題の解決**
  - ファイル: `src/color_recommendation/utils/plot_graph.py`
  - 問題: PDFで出力したグラフの文字（タイトル、軸ラベル、凡例）が白色になり背景と同化して見えない
  - 現在の対応状況:
    - matplotlib.rcParamsで各種色設定を追加済み（text.color, axes.labelcolor等）
    - seabornスタイルをreset_orig()でリセット済み
    - 各グラフ生成関数で明示的にcolor='black'を指定済み
    - savefigにtransparent=False, facecolor='white'を追加済み
  - 未解決の原因:
    - PDFバックエンドとmatplotlib/seabornの相互作用が複雑
    - 何らかの設定が上書きされている可能性
  - 検討すべき対応策:
    - matplotlib/seabornの完全なスタイルリセット（mpl.style.use('default')）
    - PDFバックエンドの明示的な設定（matplotlib.use('PDF')）
    - 別のバックエンド（cairo、svg→pdf変換）の検討
    - フォント埋め込み設定の見直し
    - PDFライブラリ（reportlab等）での直接生成
  - 期限: 未定（機能的には動作しているが見た目の問題）
  - 担当者: 未定
  - 優先度: 中（論文用グラフとして重要）
  - 回避策: PNG形式での出力は問題なく動作

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

## 🚨 Instagram/Instaloader 現状報告（2025-09-11更新）

### 📊 ダウンロード機能の現在の状況

**❌ 深刻な問題発生中**: Instagram画像の新規ダウンロードが**不可能**

#### 🔍 問題の詳細

**根本原因**: Instagram API仕様変更（2025年1月頃〜）
- **症状**: 401 Unauthorized エラー「Please wait a few minutes before you try again」
- **影響範囲**: 全世界のInstaloaderユーザーで同様の問題が多発
- **技術的原因**: `sessionid`クッキーが空になる現象

#### 🧪 実施した調査・テスト

**調査期間**: 2025-09-11  
**Instaloaderバージョン**: 4.14.1 → 4.14.2 (最新版にアップデート済み)

**✅ 成功した機能**:
- セッション読み込み (`load_session_from_file()`)
- プロフィール基本情報取得 (`Profile.from_username()`)
- フォロワー数・投稿数などの統計取得

**❌ 失敗した機能**:
- 投稿リスト取得 (`profile.get_posts()`)
- 投稿ダウンロード (`download_post()`)
- GraphQL API呼び出し全般

#### 📋 試行した解決策

1. **レート制限対策**: 60秒〜20分の待機時間 → **効果なし**
2. **セッション再作成**: 既存セッション削除・再生成 → **効果なし**
3. **設定最適化**: 保守的なInstaloader設定 → **効果なし**
4. **バージョンアップデート**: 4.14.1 → 4.14.2 → **効果なし**

#### 🔬 技術的分析結果

**セッション診断結果**:
```
sessionid: [空文字] ← 問題の核心
csrftoken: W25iefQ_J8s_wuy6omY7... [正常]
mid: aMEEggAEAAFW_syS-JYh... [正常]
ig_did: F692B524-45CD-4497-8... [正常]
```

**GitHub Issues調査**: 
- [Issue #2532](https://github.com/instaloader/instaloader/issues/2532)
- [Issue #2501](https://github.com/instaloader/instaloader/issues/2501) 
- 同様の報告が多数・解決策は未確立

#### 🛠️ 推奨対応策

**短期対応**:
1. **手動ログイン実行** (最も確実):
   ```bash
   instaloader --login emachansub
   ```
2. **Firefoxクッキー取り込み**: `firefox_session_import.py`使用
3. **プロキシ/VPN経由**: 異なるネットワーク環境での試行

**中長期対応**:
1. **既存データ活用**: 2024年までの豊富なデータで開発継続
2. **代替収集手法**: Selenium自動化、Instagram Basic Display API検討
3. **API状況監視**: Instagram側の制限緩和を待機

#### 📈 データ保有状況

**✅ 利用可能なデータ**:
- **期間**: 2021年〜2025年1月
- **イラストレーター数**: 36名以上
- **画像数**: 数千枚
- **メタデータ**: いいね数・投稿日時・ハッシュタグ等

**データ例**:
```
./src/color_recommendation/data/input/illustration/amao_1015/
├── 2021-01-01_12-09-07_UTC.jpg
├── 2021-01-08_13-14-28_UTC.jpg
└── ... (179投稿分のデータ)
```

#### 💡 開発継続方針

**現在の推奨アプローチ**:
1. **既存データで機能完成**: 色推薦システム・評価機能の完成を優先
2. **新規データ収集は後回し**: Instagram API問題解決まで一時停止
3. **代替手法の並行検討**: 技術的制約を回避する方法を模索

#### 🔗 作成された調査ツール

プロジェクトに以下の診断・修正ツールを追加:
- `instagram_debug_report.md`: 詳細分析レポート  
- `test_download.py`: 改良版テストスクリプト
- `debug_session.py`: セッション詳細診断
- `instaloader_fixes.py`: 複数修正方法の実装
- `minimal_download_test.py`: 最小限ダウンロードテスト
- `manual_login_attempt.py`: 手動ログイン支援

#### ⏰ 次回確認予定

**再評価時期**: 2025年10月中旬  
**確認項目**: Instagram API制限の緩和状況・Instaloaderコミュニティでの解決策

---

## 📋 Instagram API制限：全方位調査結果（2025-09-11更新）

### 🔍 調査背景

Instaloaderのダウンロード問題が個別のライブラリ問題か、Instagram側の包括的制限かを調査。

### 📊 調査結果サマリー

**結論**: **全てのPythonライブラリ・公式API含めて制限対象** ✅ユーザーの予想が的中

---

### 🚫 他のPythonライブラリの現状

#### **Gallery-dl**
**状況**: 同様の401 Unauthorizedエラーが多発
- GitHub Issues: [#3707](https://github.com/mikf/gallery-dl/issues/3707), [#4368](https://github.com/mikf/gallery-dl/issues/4368), [#4668](https://github.com/mikf/gallery-dl/issues/4668)
- **問題**: 「IP blocking is very aggressive」「After 5 API requests without being logged in, your IP gets blocked for the day」
- **回避策**: ブラウザクッキー必須、頻繁な失効で不安定
- **制限**: 2025年1月頃から品質低下（1280p→640p）

#### **Instagram-scraper・Instascrape**
**状況**: 基本的なAPI制限は同じ
- 軽量ライブラリでも根本的な制約は変わらず
- クッキー認証必須、セッション管理の複雑化

#### **商用スクレイピングサービス**
**2025年で利用可能な代替案**:
- **Bright Data**: 企業向け高額サービス
- **ScrapFly**: プロキシ・アンチボット機能付き
- **Data365・Apify**: リアルタイムデータ取得API

**制約**: 個人・研究用途には高コスト（月数万円〜）

---

### 🏢 Instagram公式API完全終了

#### **Meta Instagram Basic Display API**

**❌ 2024年12月4日で廃止済み**
- 「consumer developer appsのためのInstagram APIは二度と提供しない」明言
- 代替API提供の予定なし

#### **残存する公式API**

**Instagram Graph API（制限付き）**:
- **対象**: ビジネス・クリエイターアカウント専用
- **制約**: 個人アカウントのデータ取得不可
- **要件**: Facebook連携必須、管理者権限必要

---

### 🛡️ Instagram側の戦略的API封鎖

#### **制限強化の段階的実施**

**2024年後半**: 認証なしアクセス大幅制限
**2024年12月4日**: 公式Basic Display API廃止
**2025年1月〜**: スクレイピングツール包括的ブロック

#### **技術的封鎖手段**

1. **GraphQL APIエンドポイント認証強化**
   - `sessionid`検証の厳格化
   - 空sessionid即座拒否

2. **IPベース積極ブロッキング**
   - VPS・クラウドIP優先的遮断
   - 短時間大量リクエスト即座制限

3. **User-Agent・行動パターン検出**
   - 自動化ツール特有パターン識別
   - 「useragent mismatch」エラー多発

---

### 💡 2025年現在の実現可能な選択肢

#### **✅ 技術的に可能（高コスト・複雑）**

1. **商用APIサービス**: 月額数万円〜十万円
2. **住宅用プロキシ網**: 検出回避、高額・運用複雑
3. **Selenium等ブラウザ自動化**: 不安定、検出リスク高
4. **手動収集**: 確実だが大量処理不可

#### **❌ 現実的でない選択肢**

- 個人・研究用途での安定データ収集
- 無料での大量データ取得
- プログラマティックな継続アクセス

---

### 📈 他プラットフォームとの比較

#### **Twitter/X**: 
- API有料化（月$100〜）、無料枠大幅削減
- 同様の制限強化傾向

#### **YouTube**: 
- API Quotaの厳格化、商用利用制限
- 個人利用は比較的寛容

#### **TikTok**: 
- 地域・政治的制約、API提供限定的

---

### 🎯 本プロジェクトへの影響評価

#### **✅ 優位な状況**

**豊富な既存データ**:
- **期間**: 2021年〜2025年1月（4年分）
- **規模**: 36名以上のイラストレーター、数千枚画像
- **品質**: メタデータ完備、研究用途十分

#### **📋 推奨戦略転換**

1. **既存データ完全活用**: 新規収集停止、分析・システム開発に集中
2. **技術実証完成**: 色推薦アルゴリズムの完成と評価
3. **学術成果最大化**: 論文・技術報告に注力
4. **将来的データ収集**: API制限緩和まで延期

---

### 🔮 将来予測

#### **短期（2025年内）**:
- 現在の厳格制限継続
- 商用サービスのみ実用的

#### **中長期（2026年以降）**:
- AI学習用データ需要増でさらなる制限強化予想
- プラットフォーム側のデータ権利意識向上

#### **学術研究への影響**:
- 既存データセット活用が主流に
- リアルタイム分析研究の困難化
- 商用パートナーシップの重要性増大

---

## 📁 コーディング・構成ルール

- **エラー状態でのコミットは禁止**  
  → 型エラー・ビルドエラーがない状態でコミットする。

- **依存パッケージの追加もコミット単位で管理**  
  → 1コミットにまとめず、意味のある変更単位で。

- **コード中の定数・共通仕様は統一管理**  
  → `constants/` ディレクトリなどにまとめておく。

---
## 📊 実験データ処理・グラフ生成ワークフロー

### 🎯 概要

実験参加者から収集したzipファイルを解凍し、アンケート結果のグラフと感想まとめを自動生成する。

### 📁 データ構造

**入力データ**: `src/color_recommendation/data/input/experiment_result/zip/`
- `experiment_{participant_name}.zip` 形式のzipファイル
- 各zipファイルには以下が含まれる：
  - `log_noname.json`: アンケート・実験ログデータ
  - `UI1-TaskA_canvas.png`, `UI1-TaskB_canvas.png`: UI1で作成した画像
  - `UI2-TaskA_canvas.png`, `UI2-TaskB_canvas.png`: UI2で作成した画像

**出力データ**: `src/color_recommendation/data/output/experiment_analysis/`
- `survey_boxplot_comparison.pdf`: UI評価の箱ひげ図
- `survey_violin_comparison.pdf`: UI評価のヴァイオリン図
- `task_duration_comparison.pdf`: タスク所要時間比較グラフ
- `experiment_feedback_summary.md`: 統計サマリー付き感想まとめ

### 🔄 処理フロー

#### 1. zipファイルの解凍

```bash
# extractedディレクトリをクリーンアップ
cd src/color_recommendation/data/input/experiment_result
rm -rf extracted
mkdir -p extracted

# 全zipファイルを解凍
for zipfile in zip/*.zip; do
    participant=$(basename "$zipfile" .zip | sed 's/experiment_//')
    echo "解凍中: $participant"
    unzip -oq "$zipfile" -d "extracted/$participant"
done
```

#### 2. グラフ生成

```bash
cd /mnt/c/WSL-directory/my-color-recommendation-project
python3 src/color_recommendation/utils/plot_survey_results_extracted.py
```

**生成されるグラフ**:
- 箱ひげ図（UI1 vs UI2の7項目評価）
- ヴァイオリン図（UI1 vs UI2の7項目評価）
- タスク所要時間比較（UI1 vs UI2）

#### 3. 感想まとめ生成

統計サマリー付きの感想mdファイルを自動生成（`plot_survey_results_extracted.py`と同時に生成）

**生成される内容**:
1. **統計サマリー**:
   - UI選好率（UI1/UI2好み）
   - 使用順序分布
   - 参加者属性（デバイスタイプ、イラスト経験、入力デバイス）
2. **主な意見・傾向**:
   - UI2を好んだ理由（上位5件）
   - UI1を好んだ理由（上位5件）
   - 改善提案（上位10件）
3. **個別回答詳細**: 全参加者の詳細データ

### 🛠️ 使用ツール・モジュール

- **`plot_survey_results_extracted.py`**: extractedディレクトリから直接グラフ生成
  - 箱ひげ図生成: `plot_boxplot_comparison()`
  - ヴァイオリン図生成: `plot_violin_comparison()`
  - タスク時間グラフ: `plot_task_duration_comparison()`

### 📋 新しいデータを追加した場合の手順

1. zipファイルを `src/color_recommendation/data/input/experiment_result/zip/` に配置
2. 解凍スクリプト実行（上記「1. zipファイルの解凍」参照）
3. グラフ生成スクリプト実行（上記「2. グラフ生成」参照）

### ⚠️ 注意事項

- zipファイル名は必ず `experiment_{participant_name}.zip` 形式にすること
- log_noname.jsonのフォーマットを変更しないこと
- 日本語フォント（Droid Sans Fallback）がシステムにインストールされていること

---
