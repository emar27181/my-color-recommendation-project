# 引数で受け取ったRGB値の文字を表示させる関数
def print_colored_text(text, rgb):
    # RGBから16進数カラーコードに変換
    hex_color = '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])

    # ANSIエスケープシーケンスを使って色を設定
    print(f"\033[38;2;{rgb[0]};{rgb[1]};{rgb[2]}m{text}\033[0m", end="")


# 引数で受け取った配色群を表示させる関数
def print_color_schemes(color_schemes):
    for color_scheme_method in color_schemes:
        for color_scheme in color_scheme_method:
            for color in color_scheme:
                print_colored_text("■", color)

            print("")
