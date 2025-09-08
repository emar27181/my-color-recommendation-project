"""
各イラストレーターの最もいいねが多かった投稿の画像上位3つを抽出してコピー
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict
import json

from utils.helpers.path_utils import get_illustration_path, get_output_path
from utils.extract_metadata_values import get_all_metadata_by_illustrator, ImageMetadata


def copy_top_liked_images_by_illustrator(illustrator_name: str, top_n: int = 3) -> List[Dict]:
    """
    指定したイラストレーターのいいね数上位N枚の画像をコピー
    
    Args:
        illustrator_name: イラストレーター名
        top_n: コピーする上位画像数（デフォルト: 3）
        
    Returns:
        コピーした画像の情報リスト
    """
    # メタデータを取得
    metadata_list = get_all_metadata_by_illustrator(illustrator_name)
    
    if not metadata_list:
        print(f"❌ {illustrator_name}: メタデータが見つかりません")
        return []
    
    # いいね数で降順ソート
    sorted_metadata = sorted(metadata_list, key=lambda m: m.like_count, reverse=True)
    top_metadata = sorted_metadata[:top_n]
    
    # 出力ディレクトリを作成
    output_dir = get_output_path(f"top_liked_images/{illustrator_name}")
    os.makedirs(output_dir, exist_ok=True)
    
    copied_images = []
    illustration_dir = get_illustration_path(illustrator_name)
    
    for i, metadata in enumerate(top_metadata, 1):
        # 対応する画像ファイルを探す
        timestamp_str = Path(metadata.shortcode).stem if hasattr(metadata, 'shortcode') else str(metadata.timestamp)
        
        # 可能な画像ファイル名パターンを試す
        possible_extensions = ['.jpg', '.jpeg', '.png']
        source_file = None
        
        for file in os.listdir(illustration_dir):
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                file_path = os.path.join(illustration_dir, file)
                # ファイルの作成時刻やメタデータから対応する画像を特定
                # 簡易的にはファイル名の一部でマッチング
                base_name = Path(file).stem
                
                # メタデータのタイムスタンプと画像ファイル名から対応付け
                if str(metadata.timestamp) in file or metadata.shortcode in file:
                    source_file = file_path
                    break
        
        # より確実な方法: JSONファイル名から画像ファイルを推定
        if not source_file:
            for file in os.listdir(illustration_dir):
                if file.endswith('.json.xz'):
                    json_base = file.replace('.json.xz', '')
                    for ext in possible_extensions:
                        candidate = os.path.join(illustration_dir, json_base + ext)
                        if os.path.exists(candidate):
                            # このJSONファイルが対応するメタデータかチェック
                            json_path = os.path.join(illustration_dir, file)
                            try:
                                import lzma
                                with lzma.open(json_path, 'rt', encoding='utf-8') as f:
                                    json_data = json.load(f)
                                    if json_data.get('node', {}).get('id') == metadata.post_id:
                                        source_file = candidate
                                        break
                            except:
                                continue
                    if source_file:
                        break
        
        if source_file and os.path.exists(source_file):
            # ファイル名を生成（順位_いいね数_元のファイル名）
            original_filename = Path(source_file).name
            new_filename = f"rank_{i:02d}_{metadata.like_count:05d}_likes_{original_filename}"
            dest_file = os.path.join(output_dir, new_filename)
            
            try:
                shutil.copy2(source_file, dest_file)
                
                image_info = {
                    'rank': i,
                    'illustrator': illustrator_name,
                    'post_id': metadata.post_id,
                    'shortcode': metadata.shortcode,
                    'like_count': metadata.like_count,
                    'comment_count': metadata.comment_count,
                    'engagement': metadata.engagement_rate,
                    'original_file': source_file,
                    'copied_file': dest_file,
                    'caption': metadata.caption[:100] + '...' if len(metadata.caption) > 100 else metadata.caption,
                    'hashtags': metadata.hashtags[:10],  # 最初の10個のハッシュタグ
                    'timestamp': metadata.timestamp
                }
                
                copied_images.append(image_info)
                print(f"✅ #{i} コピー完了: {new_filename} (いいね: {metadata.like_count})")
                
            except Exception as e:
                print(f"❌ コピーエラー {source_file}: {e}")
        else:
            print(f"⚠️ 画像ファイルが見つかりません: post_id={metadata.post_id}, likes={metadata.like_count}")
    
    return copied_images


def copy_all_illustrators_top_images(illustrator_list: List[str] = None, top_n: int = 3) -> Dict[str, List[Dict]]:
    """
    全イラストレーターの上位いいね画像をコピー
    
    Args:
        illustrator_list: 処理するイラストレーターのリスト（None の場合は全て）
        top_n: 各イラストレーターから抽出する画像数
        
    Returns:
        {illustrator_name: [image_info, ...], ...}
    """
    if illustrator_list is None:
        # illustration ディレクトリから全イラストレーター取得
        base_illustration_path = Path(get_illustration_path('dummy')).parent
        illustrator_list = [d.name for d in base_illustration_path.iterdir() 
                          if d.is_dir() and not d.name.startswith('.')]
    
    all_results = {}
    
    for illustrator_name in illustrator_list:
        print(f"\n=== {illustrator_name} ===")
        try:
            copied_images = copy_top_liked_images_by_illustrator(illustrator_name, top_n)
            all_results[illustrator_name] = copied_images
            
            if copied_images:
                total_likes = sum(img['like_count'] for img in copied_images)
                print(f"📊 完了: {len(copied_images)}枚コピー, 合計いいね数: {total_likes:,}")
            else:
                print("⚠️ コピー対象の画像が見つかりませんでした")
                
        except Exception as e:
            print(f"❌ エラー: {e}")
            all_results[illustrator_name] = []
    
    return all_results


def save_summary_report(results: Dict[str, List[Dict]], output_file: str = None):
    """
    抽出結果のサマリーレポートを保存
    
    Args:
        results: copy_all_illustrators_top_images の結果
        output_file: レポート保存先（None の場合は自動生成）
    """
    if output_file is None:
        output_file = get_output_path("top_liked_images_summary.json")
    
    # 統計情報を集計
    summary = {
        'total_illustrators': len(results),
        'total_images_copied': sum(len(images) for images in results.values()),
        'top_performers': [],
        'illustrator_details': {}
    }
    
    # イラストレーター別詳細
    for illustrator, images in results.items():
        if images:
            total_likes = sum(img['like_count'] for img in images)
            avg_likes = total_likes / len(images)
            max_likes = max(img['like_count'] for img in images)
            
            illustrator_summary = {
                'name': illustrator,
                'images_copied': len(images),
                'total_likes': total_likes,
                'average_likes': round(avg_likes, 1),
                'max_likes': max_likes,
                'images': images
            }
            
            summary['illustrator_details'][illustrator] = illustrator_summary
            
            # トップパフォーマー追加
            summary['top_performers'].append({
                'name': illustrator,
                'max_likes': max_likes,
                'avg_likes': round(avg_likes, 1)
            })
    
    # トップパフォーマーをいいね数でソート
    summary['top_performers'].sort(key=lambda x: x['max_likes'], reverse=True)
    
    # JSON形式で保存
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"\n📋 サマリーレポート保存: {output_file}")
    
    # コンソール出力
    print(f"\n=== 抽出サマリー ===")
    print(f"処理イラストレーター数: {summary['total_illustrators']}")
    print(f"抽出画像総数: {summary['total_images_copied']}")
    
    print(f"\n=== トップパフォーマー Top 5 ===")
    for i, performer in enumerate(summary['top_performers'][:5], 1):
        print(f"{i:2d}. {performer['name']:20s} 最高いいね数: {performer['max_likes']:5,} 平均: {performer['avg_likes']:6.1f}")


if __name__ == "__main__":
    # テスト実行: 指定したイラストレーターで試す
    test_illustrators = ['amao_1015', 'gaako_instagram', 'mika_pikazo_mpz']
    
    print("=== 上位いいね画像抽出開始 ===")
    
    # 全イラストレーター処理（コメントアウト）
    # results = copy_all_illustrators_top_images(top_n=3)
    
    # テスト用: 指定イラストレーターのみ
    results = copy_all_illustrators_top_images(test_illustrators, top_n=3)
    
    # サマリーレポート保存
    save_summary_report(results)
    
    print(f"\n🎉 処理完了！")
    print(f"出力ディレクトリ: {get_output_path('top_liked_images/')}")