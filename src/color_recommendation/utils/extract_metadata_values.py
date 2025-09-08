"""
イラストのメタデータから各種値を取得するユーティリティ
Instagramから収集されたイラストのメタデータ（.json.xz, .txt）から値を抽出
"""

import json
import lzma
import os
from pathlib import Path
from typing import Dict, List, Optional, Union
from dataclasses import dataclass

from utils.helpers.path_utils import get_illustration_path


@dataclass
class ImageMetadata:
    """画像メタデータを格納するデータクラス"""
    # 基本情報
    post_id: str
    shortcode: str
    illustrator_name: str
    username: str
    full_name: str
    timestamp: int
    
    # エンゲージメント指標
    like_count: int
    comment_count: int
    
    # テキスト情報
    caption: str
    hashtags: List[str]
    
    # 画像情報
    width: int
    height: int
    is_video: bool
    
    # 追加情報
    is_paid_partnership: bool
    accessibility_caption: Optional[str]
    
    @property
    def engagement_rate(self) -> float:
        """簡易エンゲージメント率（いいね数+コメント数）"""
        return self.like_count + self.comment_count


def extract_metadata_from_json(json_file_path: str) -> Optional[ImageMetadata]:
    """
    圧縮されたJSONメタデータファイルから情報を抽出
    
    Args:
        json_file_path: .json.xz ファイルのパス
        
    Returns:
        ImageMetadata オブジェクト、またはエラー時は None
    """
    try:
        # .json.xz ファイルを展開・読み込み
        with lzma.open(json_file_path, 'rt', encoding='utf-8') as f:
            data = json.load(f)
        
        # 必要な情報を抽出
        node = data.get('node', {})
        
        # ハッシュタグを抽出
        caption_text = node.get('caption', '')
        hashtags = []
        if caption_text:
            hashtags = [word for word in caption_text.split() if word.startswith('#')]
        
        # ImageMetadata オブジェクトを構築
        metadata = ImageMetadata(
            post_id=node.get('id', ''),
            shortcode=node.get('shortcode', ''),
            illustrator_name=Path(json_file_path).parent.name,
            username=node.get('owner', {}).get('username', ''),
            full_name=node.get('owner', {}).get('full_name', ''),
            timestamp=node.get('date', 0),
            
            like_count=node.get('edge_media_preview_like', {}).get('count', 0),
            comment_count=node.get('comments', 0),
            
            caption=caption_text,
            hashtags=hashtags,
            
            width=node.get('dimensions', {}).get('width', 0),
            height=node.get('dimensions', {}).get('height', 0),
            is_video=node.get('is_video', False),
            
            is_paid_partnership=node.get('is_paid_partnership', False),
            accessibility_caption=node.get('accessibility_caption')
        )
        
        return metadata
        
    except Exception as e:
        print(f"JSONメタデータ抽出エラー {json_file_path}: {e}")
        return None


def extract_caption_from_txt(txt_file_path: str) -> str:
    """
    .txtファイルからキャプションテキストを抽出
    
    Args:
        txt_file_path: .txt ファイルのパス
        
    Returns:
        キャプションテキスト
    """
    try:
        with open(txt_file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        print(f"テキストファイル読み込みエラー {txt_file_path}: {e}")
        return ""


def get_metadata_for_image(image_path: str) -> Optional[ImageMetadata]:
    """
    画像ファイルパスに対応するメタデータを取得
    
    Args:
        image_path: 画像ファイル（.jpg, .png）のパス
        
    Returns:
        ImageMetadata オブジェクト、またはメタデータがない場合は None
    """
    base_path = Path(image_path).with_suffix('')
    json_path = f"{base_path}.json.xz"
    
    if os.path.exists(json_path):
        return extract_metadata_from_json(json_path)
    
    return None


def get_all_metadata_by_illustrator(illustrator_name: str) -> List[ImageMetadata]:
    """
    指定したイラストレーターの全画像のメタデータを取得
    
    Args:
        illustrator_name: イラストレーター名
        
    Returns:
        ImageMetadata オブジェクトのリスト
    """
    illustration_dir = get_illustration_path(illustrator_name)
    metadata_list = []
    
    if not os.path.exists(illustration_dir):
        print(f"イラストディレクトリが存在しません: {illustration_dir}")
        return metadata_list
    
    # 画像ファイルを検索
    for file_name in os.listdir(illustration_dir):
        if file_name.lower().endswith(('.jpg', '.jpeg', '.png')):
            image_path = os.path.join(illustration_dir, file_name)
            metadata = get_metadata_for_image(image_path)
            
            if metadata:
                metadata_list.append(metadata)
    
    return metadata_list


def get_engagement_statistics(illustrator_name: str) -> Dict[str, Union[int, float]]:
    """
    イラストレーターのエンゲージメント統計を取得
    
    Args:
        illustrator_name: イラストレーター名
        
    Returns:
        統計情報の辞書
    """
    metadata_list = get_all_metadata_by_illustrator(illustrator_name)
    
    if not metadata_list:
        return {}
    
    # エンゲージメント数を集計
    like_counts = [m.like_count for m in metadata_list]
    comment_counts = [m.comment_count for m in metadata_list]
    engagement_rates = [m.engagement_rate for m in metadata_list]
    
    statistics = {
        'total_posts': len(metadata_list),
        'total_likes': sum(like_counts),
        'total_comments': sum(comment_counts),
        'total_engagement': sum(engagement_rates),
        
        'avg_likes': sum(like_counts) / len(like_counts) if like_counts else 0,
        'avg_comments': sum(comment_counts) / len(comment_counts) if comment_counts else 0,
        'avg_engagement': sum(engagement_rates) / len(engagement_rates) if engagement_rates else 0,
        
        'max_likes': max(like_counts) if like_counts else 0,
        'min_likes': min(like_counts) if like_counts else 0,
        'max_comments': max(comment_counts) if comment_counts else 0,
        'min_comments': min(comment_counts) if comment_counts else 0,
        
        'max_engagement': max(engagement_rates) if engagement_rates else 0,
        'min_engagement': min(engagement_rates) if engagement_rates else 0,
    }
    
    return statistics


def get_popular_hashtags(illustrator_name: str, top_n: int = 20) -> List[tuple]:
    """
    イラストレーターがよく使用するハッシュタグを取得
    
    Args:
        illustrator_name: イラストレーター名
        top_n: 取得する上位ハッシュタグ数
        
    Returns:
        (hashtag, count) のタプルリスト
    """
    metadata_list = get_all_metadata_by_illustrator(illustrator_name)
    hashtag_count = {}
    
    for metadata in metadata_list:
        for hashtag in metadata.hashtags:
            hashtag_count[hashtag] = hashtag_count.get(hashtag, 0) + 1
    
    # 使用頻度順でソート
    sorted_hashtags = sorted(hashtag_count.items(), key=lambda x: x[1], reverse=True)
    return sorted_hashtags[:top_n]


def analyze_posting_patterns(illustrator_name: str) -> Dict[str, int]:
    """
    投稿パターンを分析（時間、曜日など）
    
    Args:
        illustrator_name: イラストレーター名
        
    Returns:
        投稿パターンの分析結果
    """
    from datetime import datetime
    
    metadata_list = get_all_metadata_by_illustrator(illustrator_name)
    
    if not metadata_list:
        return {}
    
    # 投稿時間を分析
    hours = []
    weekdays = []
    
    for metadata in metadata_list:
        if metadata.timestamp > 0:
            dt = datetime.fromtimestamp(metadata.timestamp)
            hours.append(dt.hour)
            weekdays.append(dt.weekday())  # 0=Monday, 6=Sunday
    
    hour_distribution = {}
    for hour in range(24):
        hour_distribution[f'hour_{hour:02d}'] = hours.count(hour)
    
    weekday_distribution = {}
    weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for i, day_name in enumerate(weekday_names):
        weekday_distribution[day_name] = weekdays.count(i)
    
    return {
        'posting_hours': hour_distribution,
        'posting_weekdays': weekday_distribution,
        'total_analyzed_posts': len(metadata_list)
    }


if __name__ == "__main__":
    # 使用例
    illustrator_name = "amao_1015"
    
    print(f"=== {illustrator_name} のメタデータ分析 ===")
    
    # 全メタデータ取得
    metadata_list = get_all_metadata_by_illustrator(illustrator_name)
    print(f"メタデータ取得可能な画像数: {len(metadata_list)}")
    
    if metadata_list:
        # エンゲージメント統計
        print(f"\n=== エンゲージメント統計 ===")
        stats = get_engagement_statistics(illustrator_name)
        for key, value in stats.items():
            print(f"{key}: {value}")
        
        # 人気ハッシュタグ
        print(f"\n=== 人気ハッシュタグ Top 10 ===")
        popular_hashtags = get_popular_hashtags(illustrator_name, 10)
        for hashtag, count in popular_hashtags:
            print(f"{hashtag}: {count}")
        
        # 投稿パターン分析
        print(f"\n=== 投稿パターン分析 ===")
        patterns = analyze_posting_patterns(illustrator_name)
        print(f"分析対象投稿数: {patterns.get('total_analyzed_posts', 0)}")
        
        # 最も投稿が多い時間帯
        if 'posting_hours' in patterns:
            best_hour = max(patterns['posting_hours'].items(), key=lambda x: x[1])
            print(f"最も投稿の多い時間帯: {best_hour[0]} ({best_hour[1]} 投稿)")
        
        # 最も投稿が多い曜日
        if 'posting_weekdays' in patterns:
            best_day = max(patterns['posting_weekdays'].items(), key=lambda x: x[1])
            print(f"最も投稿の多い曜日: {best_day[0]} ({best_day[1]} 投稿)")
        
        # サンプル投稿の詳細
        print(f"\n=== サンプル投稿詳細 ===")
        sample = metadata_list[0]
        print(f"投稿ID: {sample.post_id}")
        print(f"Shortcode: {sample.shortcode}")
        print(f"いいね数: {sample.like_count}")
        print(f"コメント数: {sample.comment_count}")
        print(f"エンゲージメント: {sample.engagement_rate}")
        print(f"画像サイズ: {sample.width}x{sample.height}")
        print(f"ハッシュタグ数: {len(sample.hashtags)}")
        print(f"キャプション抜粋: {sample.caption[:100]}...")