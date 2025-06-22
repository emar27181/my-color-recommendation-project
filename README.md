# my-color-recommendation-project

## はじめに
このプロジェクトはイラスト制作支援を目的とする配色推薦のためのものです。

## プロジェクト構造

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

## 配色推薦の流れ（実験段階）

### 1. 画像のダウンロード
Instagram等のSNSから実際のイラストレータの作品画像を収集し、配色分析の基礎データとする。

### 2. 量子化
`extract_used_color_count(image_path, quantize_threshold)`: 引数で受け取ったパスの画像の色とその出現回数を抽出する関数

### 3. クラスタリング
色データをクラスタリングアルゴリズムで分類し、代表的な色を抽出する。

### 4. 配色抽出
クラスタリング結果から配色パターンを抽出し、データベース化する。

### 5. 配色推薦
入力画像に対して、蓄積した配色パターンから適切な色を推薦する。

### 6. 評価
Recall@K等の指標を用いて推薦精度を評価し、手法の改善を行う。

## 使用方法

1. 仮想環境のセットアップ:
```bash
python -m venv venv_color_recommendation
source venv_color_recommendation/bin/activate  # Linux/Mac
# または
venv_color_recommendation\Scripts\activate     # Windows
```

2. 依存関係のインストール:
```bash
pip install -r requirements.txt
```

3. Webアプリケーションの起動:
```bash
python src/app.py
```