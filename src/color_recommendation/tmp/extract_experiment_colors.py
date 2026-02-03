"""実験画像から使用色の割合を抽出し、UIとタスクごとにJSONで保存するスクリプト"""
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.estimate_used_color_scheme import estimate_used_color_scheme
from utils.helpers.transform_color import rgb_to_hex

BASE_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'input', 'experiment_result', 'image')

PARTICIPANTS = [
    "ema_kennosuke", "ema_megumi", "ikeyama", "irie", "ito_mitsuki",
    "ito_yuta", "kawasaki", "kurita", "matsusita", "nagaoka", "naka",
    "niiya", "nishio", "oomuro", "sato_hiromu", "sato_takehiro",
    "tsuchiya", "uemura", "ugawa", "ukigai"
]

UI_TASKS = [
    ("UI1", "task1"),
    ("UI1", "task2"),
    ("UI2", "task1"),
    ("UI2", "task2"),
]


def extract_colors_for_image(image_path):
    """画像から色の使用比率を抽出してdict形式で返す"""
    color_data = estimate_used_color_scheme(image_path)
    results = []
    for rgb, rate in color_data:
        results.append({
            "color": rgb_to_hex(rgb),
            "rgb": [int(c) for c in rgb],
            "rate": round(float(rate) / 100, 6)  # 0-1の範囲に正規化
        })
    return results


def main():
    for ui, task in UI_TASKS:
        task_dir = os.path.join(BASE_DIR, ui, task)
        all_data = {}

        print(f"\n=== {ui}/{task} ===")
        for name in PARTICIPANTS:
            image_path = os.path.join(task_dir, f"{name}.png")
            if not os.path.exists(image_path):
                print(f"  SKIP (not found): {name}")
                continue

            print(f"  Processing: {name}")
            colors = extract_colors_for_image(image_path)
            all_data[name] = colors

        # JSONで保存
        output_path = os.path.join(task_dir, "used_colors.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        print(f"  Saved: {output_path} ({len(all_data)} participants)")


if __name__ == "__main__":
    main()
