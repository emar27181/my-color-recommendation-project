import json
import os
from typing import List, Dict, Optional, Tuple
from .helpers.transform_color import hex_to_rgb, rgb_to_hsl
from .helpers.json_utils import get_json_data, save_json_data


def is_skin_tone(hex_color: str) -> bool:
    """
    色が肌色かどうかを判定する関数（改善版）
    
    改善された肌色の判定基準：
    - 色相: 15°-50° (より厳密なオレンジ〜黄色範囲)
    - 彩度: 10%-60% (適度な色味)
    - 明度: 30%-90% (自然な肌色の明度範囲)
    - RGB追加フィルタ: 緑成分が強すぎる色を除外
    """
    try:
        rgb = hex_to_rgb(hex_color)
        r, g, b = rgb
        h, s, l = rgb_to_hsl(rgb)
        
        # 無彩色は肌色ではない
        if s < 10:
            return False
        
        # より厳密な肌色の色相範囲 (15-50度)
        hue_valid = 15 <= h <= 50
        
        # 肌色の彩度範囲 (10-60%)
        saturation_valid = 10 <= s <= 60
        
        # 肌色の明度範囲 (30-93%)
        lightness_valid = 30 <= l <= 93
        
        # RGB追加フィルタ: 緑成分が強すぎる色を除外
        # 肌色では通常 R > B かつ緑が強すぎない
        rgb_valid = r > b and g <= r + 20  # 緑が赤より20以上大きくない
        
        # 暗すぎる色（全体的に値が低い）を除外
        brightness_valid = (r + g + b) >= 100
        
        return hue_valid and saturation_valid and lightness_valid and rgb_valid and brightness_valid
        
    except Exception:
        return False


def extract_skin_tones_from_colors(colors: List[Dict]) -> List[Dict]:
    """
    色リストから肌色を抽出する関数
    
    Args:
        colors: 色データのリスト [{"color": "#hex", "rate": float, ...}, ...]
    
    Returns:
        肌色のみのリスト
    """
    skin_tones = []
    
    for color_data in colors:
        if "color" in color_data and is_skin_tone(color_data["color"]):
            skin_tones.append(color_data)
    
    return skin_tones


def extract_skin_tones_by_illustrator(illustrator_name: str) -> Optional[List[Dict]]:
    """
    特定のイラストレーターの肌色を抽出する関数
    
    Args:
        illustrator_name: イラストレーター名
    
    Returns:
        肌色データのリスト、または None（ファイルが存在しない場合）
    """
    from .helpers.path_utils import get_used_colors_path
    file_path = get_used_colors_path(illustrator_name)
    
    try:
        used_colors_data = get_json_data(file_path)
        all_skin_tones = []
        
        for artwork_colors in used_colors_data:
            skin_tones = extract_skin_tones_from_colors(artwork_colors)
            if skin_tones:
                all_skin_tones.extend(skin_tones)
        
        return all_skin_tones if all_skin_tones else None
        
    except Exception as e:
        print(f"Error processing {illustrator_name}: {e}")
        return None


def extract_all_illustrators_skin_tones() -> Dict[str, List[Dict]]:
    """
    全イラストレーターの肌色を抽出する関数
    
    Returns:
        {illustrator_name: [skin_tone_data, ...], ...}
    """
    from .helpers.path_utils import get_data_path
    used_colors_dir = get_data_path("input/used_colors/")
    results = {}
    
    # ディレクトリ内のJSONファイルを取得
    for filename in os.listdir(used_colors_dir):
        if not filename.startswith("used_colors_") or not filename.endswith(".json"):
            continue
        
        # イラストレーター名を抽出
        illustrator_name = filename.replace("used_colors_", "").replace(".json", "")
        
        # パレット系ファイルはスキップ
        if any(palette in illustrator_name for palette in [
            "clipstudio_color_set_palette", "ibispaint_color_palette", 
            "medibang_color_palette", "pixivsketch_color_palette",
            "powerpoint_color_palette"
        ]):
            continue
        
        print(f"Processing {illustrator_name}...")
        
        skin_tones = extract_skin_tones_by_illustrator(illustrator_name)
        if skin_tones:
            results[illustrator_name] = skin_tones
            print(f"  Found {len(skin_tones)} skin tone colors")
        else:
            print(f"  No skin tones found")
    
    return results


def save_skin_tones_data(skin_tones_data: Dict[str, List[Dict]], output_file: str = None):
    """
    肌色データを保存する関数
    
    Args:
        skin_tones_data: 肌色データ
        output_file: 出力ファイルパス（デフォルト: data/output/skin_tones.json）
    """
    if output_file is None:
        from .helpers.path_utils import get_output_path
        output_file = get_output_path("skin_tones.json")
    
    # 出力ディレクトリを作成
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    save_json_data(skin_tones_data, os.path.dirname(output_file), output_file)
    print(f"Skin tones data saved to {output_file}")


def get_skin_tone_statistics(skin_tones_data: Dict[str, List[Dict]]) -> Dict[str, Dict]:
    """
    肌色使用統計を生成する関数
    
    Returns:
        {illustrator_name: {"count": int, "avg_rate": float, "colors": [hex, ...]}, ...}
    """
    statistics = {}
    
    for illustrator_name, skin_tones in skin_tones_data.items():
        if not skin_tones:
            continue
        
        count = len(skin_tones)
        avg_rate = sum(color_data.get("rate", 0) for color_data in skin_tones) / count
        colors = [color_data["color"] for color_data in skin_tones]
        
        statistics[illustrator_name] = {
            "count": count,
            "average_usage_rate": round(avg_rate, 4),
            "colors": colors
        }
    
    return statistics


if __name__ == "__main__":
    # 全イラストレーターの肌色を抽出
    print("Extracting skin tones from all illustrators...")
    skin_tones_data = extract_all_illustrators_skin_tones()
    
    # データを保存
    save_skin_tones_data(skin_tones_data)
    
    # 統計情報を生成・保存
    statistics = get_skin_tone_statistics(skin_tones_data)
    from .helpers.path_utils import get_output_path
    statistics_file = get_output_path("skin_tones_statistics.json")
    save_json_data(statistics, os.path.dirname(statistics_file), statistics_file)
    
    print(f"\nProcessing completed:")
    print(f"- Total illustrators with skin tones: {len(skin_tones_data)}")
    print(f"- Total skin tone colors found: {sum(len(colors) for colors in skin_tones_data.values())}")
    
    # 結果のサマリーを表示
    print("\nSummary by illustrator:")
    for name, stats in statistics.items():
        print(f"  {name}: {stats['count']} colors (avg rate: {stats['average_usage_rate']})")