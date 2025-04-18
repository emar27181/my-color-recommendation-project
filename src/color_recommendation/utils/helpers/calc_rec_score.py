"""
生成された推薦配色をそれぞれ評価基準に基づいてスコアを計算する関数を保存するファイル
"""

from utils.helpers.color_utils import print_color_scheme

DEBUG = False


def calc_same_hue_score(used_color_scheme, rec_color_shceme):
    """ 同じ色相かどうかでスコアを計算する関数
    """

    if (DEBUG):
        print("======================")
        print("used_color_scheme: ", end="")
        print_color_scheme(used_color_scheme)
        print("rec_color_scheme:  ", end="")
        print_color_scheme(rec_color_shceme)

    return 1
