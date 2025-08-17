# 🎨 イラストレーター向け配色推薦システム

> 🤖 **このドキュメントは[Claude Code](https://claude.ai/code)を使用して作成・管理されています**  
> プロジェクトの開発・ドキュメント整備・コード実装において、AIアシスタントによる効率的な開発支援を活用しています。

## 📋 プロジェクト概要

このプロジェクトは、**イラストレーターの過去の作品分析に基づく個人化配色推薦システム**です。機械学習と色彩理論を組み合わせて、各イラストレーターの色使用傾向を学習し、新しい作品に適した配色を提案します。

### 🎯 主な特徴
- **個人化推薦**: イラストレーター別の色使用統計に基づく推薦
- **多様な配色技法**: 17種類の配色理論（アナロジー、トライアド、補色等）を実装
- **高精度ソート**: 色差・使用頻度・トーン分布による多角的な配色並び替え
- **Webインターフェース**: ブラウザ上での直感的な配色推薦体験
- **研究支援**: Recall@K評価・可視化機能による推薦精度の検証

### 🔬 研究背景
従来の配色推薦システムは一般的な色彩理論に基づいていますが、本システムはイラストレーター個人の**色使用パターン**と**トーン傾向**を学習することで、より個性に適した配色推薦を実現します。

## 📂 プロジェクト構造

```
my-color-recommendation-project/
├── PROJECT_RULES.md              # プロジェクト開発ルール
├── README.md                     # このファイル
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
│           │   ├── used_colors/    # 使用色データ
│           │   ├── used_hues/      # 使用色相データ
│           │   ├── backup/         # バックアップデータ
│           │   └── statistics_for_illustrators.json # イラストレータ統計
│           ├── output/            # 出力データ
│           │   ├── graph/          # グラフ出力
│           │   ├── heatmap/        # ヒートマップ出力
│           │   ├── recall_at_k/    # Recall@K評価結果
│           │   ├── recommend_colors/ # 推薦色データ
│           │   ├── recommend_hues/  # 推薦色相データ
│           │   ├── recommend_tones/ # 推薦トーンデータ
│           │   └── tmp/            # 一時出力ファイル
│           └── tmp/               # 一時データ
│
├── tmp/                          # 一時ファイル（実験用）
└── venv_color_recommendation/    # Python仮想環境
```

## 🔄 配色推薦システムの処理フロー

### 📊 データ収集・前処理フェーズ
1. **画像データ収集** (`download_instagram_images.py`)
   - Instagram等のSNSから実際のイラストレーター作品を収集
   - 個人別のポートフォリオデータを蓄積

2. **色抽出・量子化** (`estimate_used_color_scheme.py`)
   - ColorThiefライブラリによる支配色抽出
   - 類似色の統合・量子化処理
   - JSON形式での使用色データ保存

3. **統計分析** (`analyze_illustrator_statistics.py`)
   - イラストレーター別の色使用傾向分析
   - 色相・トーン・明度分布の統計生成
   - `saturation_lightness_count_distribution`による5×5トーンマトリックス作成

### 🎨 配色推薦フェーズ
4. **配色生成** (`generate_color_scheme_method.py`)
   - 17種の配色技法による候補色生成
   - アナロジー・トライアド・補色・分裂補色・テトラード等
   - バリエーション展開機能

5. **個人化ソート** (`sort_color_scheme.py`)
   - **色差順ソート**: ΔE2000による色差計算
   - **使用頻度順ソート**: 過去の色数使用パターン
   - **トーン使用頻度順ソート**: HSL→トーン座標変換による個人傾向反映
   - **平均結果長順ソート**: 色相環での分散度評価

6. **推薦結果出力** (`color_recommendation.py`)
   - 色相推薦・トーン推薦・色推薦の統合処理
   - JSON形式での推薦結果保存

### 📈 評価・検証フェーズ
7. **精度評価** (`plot_graph.py`)
   - Recall@K指標による推薦精度測定
   - バイオリンプロット・ヒートマップ生成
   - エラーバー付きグラフによる手法比較

## 🛠️ 主要機能・アルゴリズム

### 🎯 推薦アルゴリズム
- **色相推薦**: PCCS色相環に基づく調和色生成
- **トーン推薦**: 明度・彩度分布に基づく個人化トーン提案
- **複合推薦**: 色相×トーンのマトリックス推薦

### 📐 配色技法（17種実装）
```
基本技法: モノクロマティック・アナロジー・補色・分裂補色
高度技法: トライアド・テトラード・スクエア・五角形・六角形
特殊技法: ダブル補色・ダブル分裂補色・三分割補色 等
```

### 🔢 評価指標
- **Recall@K**: 上位K個の推薦中の正解率
- **ΔE2000色差**: 知覚的色差による類似度評価
- **平均結果長**: 色相環での調和度評価

## 🚀 最新機能（2025-06-22実装）

### 🎨 トーン使用頻度順ソート機能
イラストレーターの過去作品から抽出した**5×5トーン分布マトリックス**に基づく高精度ソート機能を新実装：

- **HSL色空間変換**: hex → RGB → HSL → トーン座標
- **個人化スコア計算**: 各配色の過去使用頻度を数値化
- **動的ソート**: 使用頻度降順での推薦順序最適化

```python
# 実装場所: src/color_recommendation/utils/sort_color_scheme.py
sort_color_schemes_by_used_tone(color_schemes, illustrator_name)
```

## 🚀 クイックスタート

### 📋 前提条件
- Python 3.8+
- Git
- 仮想環境管理ツール（venv推奨）

### ⚡ インストール・セットアップ

1. **リポジトリのクローン**
```bash
git clone <repository-url>
cd my-color-recommendation-project
```

2. **仮想環境のセットアップ**
```bash
python -m venv venv_color_recommendation
source venv_color_recommendation/bin/activate  # Linux/Mac
# または
venv_color_recommendation\Scripts\activate     # Windows
```

3. **依存関係のインストール**
```bash
pip install -r requirements.txt
```

### 🌐 Webアプリケーション

4. **Flaskサーバーの起動**
```bash
python src/app.py
```

5. **ブラウザでアクセス**
```
http://localhost:5000/
```

### 🧪 研究・実験モード

最新の実験機能を使用する場合：
```bash
cd src/color_recommendation
python sandbox3.py  # 最新実験コード（推奨）
```

パラメータ調整やバッチ処理：
```bash
python sandbox2.py  # バッチ処理・複数イラストレーター分析
```

### 📊 データ分析・可視化

推薦精度の評価とグラフ生成：
```bash
cd src/color_recommendation
python utils/plot_graph.py
```

## 📁 データ管理

### 📥 入力データ形式

**使用色データ** (`data/input/used_colors/*.json`)
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

**イラストレーター統計** (`data/input/statistics_for_illustrators.json`)
```json
{
  "illustrator_name": "artist_name",
  "chromatic_colors_count_ave": 4.82,
  "saturation_lightness_count_distribution": [[13,36,36,24,0], ...]
}
```

### 📤 出力データ

- **推薦結果**: `data/output/recommend_colors/`
- **評価グラフ**: `data/output/graph/`
- **ヒートマップ**: `data/output/heatmap/`

## 🔧 設定・カスタマイズ

### ⚙️ 主要設定ファイル
- **`src/color_recommendation/utils/config/constants_dev.py`**: 開発用定数
- **`PROJECT_RULES.md`**: 開発ルール・機能リファレンス

### 🎛️ 調整可能パラメータ
```python
SATURATION_LOWER_LIMIT = 10     # 彩度下限
LIGHTNESS_UPPER_LIMIT = 90      # 明度上限
LIGHTNESS_LOWER_LIMIT = 10      # 明度下限
IS_PRINT_COLOR_SCHEME = True    # デバッグ出力
```

## 🧑‍💻 開発者向け情報

### 📝 新機能追加
- **配色技法追加**: `generate_color_scheme_method.py`を編集
- **ソート方式追加**: `sort_color_scheme.py`を編集
- **評価指標追加**: `helpers/calc_rec_score.py`を編集

### 🔍 デバッグ
各ファイルの`DEBUG`変数を`True`に設定：
```python
DEBUG = True  # 詳細ログ出力
```

### 📚 詳細ドキュメント
- **開発ルール**: `PROJECT_RULES.md`
- **機能リファレンス**: `PROJECT_RULES.md`内の関数一覧
- **研究メモ**: `_research_memo.md`

## 📊 評価・実験結果

### 🎯 推薦精度指標
- **Recall@5**: 上位5推薦の正解率
- **Recall@10**: 上位10推薦の正解率
- **平均色差**: ΔE2000による知覚的距離

### 📈 比較評価
- 色差順ソート vs トーン使用頻度順ソート
- 個人化推薦 vs 一般的配色理論
- 17種配色技法の効果比較

## 🤝 貢献・開発

### 📋 開発フロー
1. `PROJECT_RULES.md`の確認
2. 機能実装・テスト
3. 実験コードでの検証
4. ドキュメント更新
5. コミット（ルールに基づく）

### ⚠️ 注意事項
- **セキュリティ**: `constants_dev.py`のパスワード情報は環境変数化必須
- **コミット**: ユーザー明示的指示なしの自動コミット禁止
- **データ管理**: 個人情報を含む画像データの取り扱い注意

---

## 🔬 論文用固定値・アルゴリズム詳細

> 研究の再現性確保のため、システム内の全固定値とアルゴリズムを詳細記録

### 📊 1. 使用色抽出アルゴリズム

**手法**: ColorThief + ΔE類似色統合 + 有彩色フィルタリング

**🔧 固定パラメータ**:
```python
# src/color_recommendation/utils/estimate_used_color_scheme.py
出現率閾値 = 0.3%        # Line 37: if (rate >= 0.3)
ColorThief品質 = 10      # Line 86: quality=10
ColorThief色数 = 30      # Line 72: color_count=30

# 色差統合閾値
ΔE統合閾値_使用色 = 5     # Line 48: threshold=5 in merge_similar_color()
ΔE統合閾値_パレット = 10  # Line 110: threshold < 10 in merge_same_color_palette()
ユークリッド距離閾値 = 0.1 # Line 176: distance < 0.1 in color_count_by_color_palette()

# 有彩色判定基準 (src/color_recommendation/utils/config/constants_dev.py)
SATURATION_LOWER_LIMIT = 10   # Line 5: 彩度下限（%）
LIGHTNESS_LOWER_LIMIT = 10    # Line 7: 明度下限（%）
LIGHTNESS_UPPER_LIMIT = 90    # Line 6: 明度上限（%）
```

**📋 処理フロー**:
1. ColorThief抽出: `get_palette(color_count=30, quality=10)`
2. 類似色統合: ΔE ≤ 10で統合
3. ピクセル分類: ユークリッド距離 < 0.1で再分類
4. 有彩色フィルタ: S≥10, 10≤L≤90の範囲で抽出
5. 最終統合: ΔE ≤ 5で類似色を統合

### 🎨 2. 色相推薦アルゴリズム

**手法**: 17種配色技法による組織的配色生成 + 統計ベース並び替え

**🔧 配色技法固定角度**:
```python
# src/color_recommendation/utils/generate_color_scheme_method.py
# 2色配色技法
アナロジー配色 = [+30°, -30°]     # Line 73-74
中間色配色 = [+90°, -90°]         # Line 79-80
補色配色 = [180°]                  # Line 85
対立色配色 = [+150°, -150°]       # Line 90-91

# 3色配色技法
ドミナント配色 = {
    パターン1: [+30°, +60°],      # Line 97
    パターン2: [-30°, +30°],      # Line 98
    パターン3: [-60°, -30°]       # Line 99
}
スプリット補色 = [+150°, -150°]   # Line 103-104
トライアド配色 = [+120°, +240°]   # Line 107-108

# 多色配色技法
テトラード配色 = [+90°, +180°, +270°]  # Line 111-112
ペンタード配色 = [+72°, +144°, +216°, +288°]  # Line 115-116
ヘキサード配色 = [+60°, +120°, +180°, +240°, +300°]  # Line 119-120
```

**📊 並び替えアルゴリズム**:
- **色差順ソート**: `calc_color_scheme_difference_delta_e_cie2000()` (ΔE昇順)
- **統計ベースソート**: 
  - 使用色数順: `chromatic_colors_count_distribution` (使用頻度降順)
  - 平均結果長順: `mean_resultant_length_distribution` (使用頻度降順)

### 🌈 3. トーン推薦アルゴリズム

**手法**: 単色ベース + HSL空間での明度彩度バリエーション生成

**🔧 バリエーション生成パラメータ**:
```python
# src/color_recommendation/color_recommendation.py
基本配色 = 単色配色（1色のみ）        # Line 61: generate_one_color_schemes()
バリエーション軸 = "saturation_and_lightness"  # Line 70

# 差分値設定（一般的な使用例）
diff_values = [-40, -20, 0, +20, +40]  # 明度・彩度の差分値（%）
# 処理ロジック: 全組み合わせでバリエーション生成（5×5=25パターン）
```

**📋 生成手順**:
1. 基本色のHSL値取得: `rgb_to_hsl(color_rgb)`
2. 差分適用: `hsl_to_rgb(H, S+saturation_diff, L+lightness_diff)`
3. 有効性検証: `is_valid_color(new_color)`
4. 無効色除外: RGB値が範囲外の場合は配色から除外

### ⚖️ 4. 評価・判定閾値

**🎯 同一色判定閾値**:
```python
# ΔE（CIE2000）ベース閾値
使用色統合閾値 = 5     # merge_similar_color(): threshold <= 5
パレット統合閾値 = 10  # merge_same_color_palette(): threshold < 10
同一色判定基準 = 可変  # 関数引数依存
デフォルト閾値 = 0.01  # generate_color_scheme_method.py:142

# ユークリッド距離ベース閾値
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

### 📚 学術的根拠

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

**開発者**: 配色推薦研究チーム  
**最終更新**: 2025-08-15 (論文用データ追加)  
**ライセンス**: 研究用途