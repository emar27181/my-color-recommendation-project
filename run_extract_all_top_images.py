#!/usr/bin/env python3
"""
全イラストレーターの上位いいね画像を抽出するスクリプト
"""

import sys
import os

# パス設定
sys.path.append('/mnt/c/WSL-directory/my-color-recommendation-project/src/color_recommendation')

from utils.extract_top_liked_images import copy_all_illustrators_top_images, save_summary_report

def main():
    print("=== 全イラストレーター 上位いいね画像抽出開始 ===")
    
    # 全イラストレーターから上位3枚を抽出
    results = copy_all_illustrators_top_images(top_n=3)
    
    # サマリーレポート保存
    save_summary_report(results)
    
    # 成功したイラストレーター数を集計
    successful_illustrators = [name for name, images in results.items() if images]
    failed_illustrators = [name for name, images in results.items() if not images]
    
    print(f"\n=== 最終結果 ===")
    print(f"✅ 成功: {len(successful_illustrators)} イラストレーター")
    print(f"❌ 失敗: {len(failed_illustrators)} イラストレーター")
    
    if successful_illustrators:
        print(f"\n📊 成功したイラストレーター:")
        for name in successful_illustrators[:10]:  # 最初の10個を表示
            image_count = len(results[name])
            total_likes = sum(img['like_count'] for img in results[name])
            print(f"  - {name}: {image_count}枚, 合計いいね数: {total_likes:,}")
        
        if len(successful_illustrators) > 10:
            print(f"  ... 他 {len(successful_illustrators) - 10} イラストレーター")
    
    if failed_illustrators:
        print(f"\n⚠️ メタデータが見つからなかったイラストレーター:")
        for name in failed_illustrators[:10]:  # 最初の10個を表示
            print(f"  - {name}")
        
        if len(failed_illustrators) > 10:
            print(f"  ... 他 {len(failed_illustrators) - 10} イラストレーター")
    
    print(f"\n🎉 全処理完了！")

if __name__ == "__main__":
    main()