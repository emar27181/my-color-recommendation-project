import instaloader


# 引数で受け取ったユーザ名のイラストを一括ダウンロードする関数
def download_instagram_images(profile_name):
    # Instaloaderインスタンスを作成
    L = instaloader.Instaloader(dirname_pattern="src/color_recommendation/data/input/illustration/{target}")  # data/input/アカウント名 に保存

    # アカウントの写真をダウンロード
    L.download_profile(profile_name, profile_pic_only=False)
