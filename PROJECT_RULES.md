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