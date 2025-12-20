# ========================================
# 📝 このファイルについて
# ========================================
# このファイルはテンプレートファイルです。
# 使用する際は、ファイル名から「_template」を削除してください。
#
# 【使用方法】
# 1. このファイルをコピーして「constants_dev_template.py」→「constants_dev.py」にリネーム
# 2. Instagram認証情報を環境変数から読み込むか、直接記入（セキュリティ注意）
# 3. このファイル(constants_dev.py)はgitの追跡対象外なので、機密情報を含めても安全です
#
# 【セキュリティ注意】
# - INSTAGRAM_PASS は本番環境では必ず環境変数(.env)から読み込んでください
# - テスト環境でのみ直接記述を許可（gitにコミットしないこと）
# ========================================

# 推奨: 環境変数から読み込み
# import os
# from dotenv import load_dotenv
# load_dotenv()
# INSTAGRAM_ID = os.getenv("INSTAGRAM_ID", "your_instagram_id")
# INSTAGRAM_PASS = os.getenv("INSTAGRAM_PASS", "your_password")

# テスト環境用（機密情報を直接記述する場合）
INSTAGRAM_ID = "your_instagram_id"  # ← あなたのInstagram IDに書き換えてください
INSTAGRAM_PASS = "your_password"     # ← あなたのパスワードに書き換えてください

# 使用した配色として判定する閾値
SATURATION_LOWER_LIMIT = 10      # 彩度下限（%）: この値未満は無彩色とみなす
LIGHTNESS_UPPER_LIMIT = 90       # 明度上限（%）: この値より大きい色は白とみなす
LIGHTNESS_LOWER_LIMIT = 10       # 明度下限（%）: この値より小さい色は黒とみなす

# デバッグ表示設定
IS_PRINT_COLOR_SCHEME = True                # 使用色の抽出の様子を逐一表示させるかどうか
IS_PRINT_COLOR_SCHEME_BEFORE_MERGED = False # 統合前の配色を表示するかどうか
