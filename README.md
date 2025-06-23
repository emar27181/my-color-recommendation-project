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

**開発者**: 配色推薦研究チーム  
**最終更新**: 2025-06-22  
**ライセンス**: 研究用途