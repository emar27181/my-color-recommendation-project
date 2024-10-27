import instaloader


# 引数で受け取ったユーザ名のイラストを一括ダウンロードする関数
def download_instagram_images(profile_name, illust_count_limit):
    # Instaloaderインスタンスを作成
    L = instaloader.Instaloader(dirname_pattern="src/color_recommendation/data/input/illustration/{target}")

    # プロフィールを取得
    profile = instaloader.Profile.from_username(L.context, profile_name)

    # 投稿をダウンロード
    count = 0
    for post in profile.get_posts():
        if count >= illust_count_limit:
            return
        L.download_post(post, target=profile_name)
        count += 1
