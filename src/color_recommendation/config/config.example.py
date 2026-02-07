"""
設定ファイルテンプレート

このファイルをコピーして config.py として使用してください：
  cp src/color_recommendation/config/config.example.py src/color_recommendation/config/config.py

config.py は .gitignore に含まれており、個人の設定を保存できます。
"""

# ========== 実行制御フラグ ==========

# グラフ生成を実行するかどうか
IS_SAVE_GRAPH = True

# アンケート結果グラフ生成を実行するかどうか
IS_PLOT_SURVEY_RESULTS = False

# デバッグモード（1名のイラストレーターのみで実行）
DEBUG_MODE = False


# ========== イラストレーターリスト ==========

# 分析対象のイラストレーターリスト
ILLUSTRATOR_LIST = [
    "mika_pikazo_mpz", "harunonioikaze", "gaako_illust", "mokmok_skd",
    "nest_virgo", "omrice4869", "oz_yarimasu", "sa_ka_na_4", "trcoot",
    "birdstory_pic", "amao_1015", "meeesuke_", "shirokumaai", "tsumugitopan",
    "sexygirl.jp", "obungu_mofumofu", "skt2ing", "iina.gram", "chi_bee.official",
    "harupeipei", "bj00100", "jerome_trez_oudot", "deppa_53"
]

# デバッグ用イラストレーターリスト（DEBUG_MODE=Trueの場合に使用）
DEBUG_ILLUSTRATOR_LIST = ["mika_pikazo_mpz"]


# ========== 推薦設定 ==========

# ソートタイプのリスト
SORT_TYPES = [
    "random",
    # "color_diff",
    "used_color_count",
    # "no_sort",
    "mean_resultant_length",
    # "custom_v0"
]

# 推薦タイプのリスト
RECOMMEND_TYPES = [
    "hue",  # 色相推薦
    # "tone",  # トーン推薦
    # "color",  # 色推薦
    # "color_existing_apps",  # 既存アプリとの比較
]

# 差分値リスト（明度・彩度のバリエーション）
DIFF_VALUES = [20, -20, 40, -40, 60, -60, 80, -80]

# 差分値リストのバリエーション（複数パターンで実験する場合）
DIFF_VALUES_LIST = [
    [20, -20, 40, -40],
    [20, -20, 40, -40, 60, -60, 80, -80],
    [-10, 10, -20, 20, -30, 30, -40, 40, -50, 50, -60, 60, -70, 70, -80, 80, -90, 90]
]

# 比較対象アプリ名リスト
APP_NAMES = [
    "clipstudio",
    "ibispaint",
    "medibang",
    "pixivsketch",
    "powerpoint",
    # "proposed_method"  # 提案手法（自動で追加される）
]

# グラフの凡例位置
LEGEND_LOCATION = "lower right"


# ========== グラフ生成設定 ==========

# 主要グラフ生成フラグ
GENERATE_RECALL_AT_K_SORT_TYPES = True  # ソートタイプ別recall@kグラフ
GENERATE_RECALL_AT_K_DIFF_VALUES = False  # バリエーション別recall@kグラフ
GENERATE_RECALL_AT_K_FIXED_SUBJECTS = False  # 推薦段階別recall@kグラフ

# 統計グラフ生成フラグ
GENERATE_ACHROMATIC_BAR = True  # 無彩色使用率の棒グラフ
GENERATE_MEAN_RESULTANT_VIOLIN = True  # 平均結果長のヴァイオリン図
GENERATE_USED_HUES_VIOLIN = True  # 使用色相数のヴァイオリン図
GENERATE_PCCS_DISTRIBUTION_VIOLIN = False  # PCCS色相分布のヴァイオリン図
GENERATE_SCATTER_PLOTS = False  # 使用色の散布図（※多数のファイル生成）
GENERATE_TONE_HEATMAPS = False  # トーン使用のヒートマップ（※多数のファイル生成）
GENERATE_ANONYMOUS_GRAPHS = False  # 匿名版の統計グラフを生成するかどうか


# ========== 既存アプリ比較設定 ==========

# 既存アプリとの比較を実行するかどうか
RUN_EXISTING_APP_COMPARISON = False

# 既存アプリ比較の推薦データ生成
GENERATE_EXISTING_APP_RECOMMENDATIONS = False

# 既存アプリ比較の評価データ生成
GENERATE_EXISTING_APP_EVALUATIONS = False

# 既存アプリ比較のグラフ生成
GENERATE_EXISTING_APP_GRAPHS = False
