"""
パス管理ユーティリティ
Flask GUI実行時（src/から実行）と通常実行（プロジェクトルートから実行）の両方に対応
"""

import os
from pathlib import Path


class PathResolver:
    """
    プロジェクトのパス解決を統一的に管理するクラス
    """
    
    def __init__(self):
        self._project_root = None
        self._is_flask_gui_mode = None
    
    @property
    def project_root(self):
        """プロジェクトルートディレクトリを取得"""
        if self._project_root is None:
            self._project_root = self._find_project_root()
        return self._project_root
    
    @property
    def is_flask_gui_mode(self):
        """Flask GUIモード（src/から実行）かどうかを判定"""
        if self._is_flask_gui_mode is None:
            current_dir = Path.cwd()
            self._is_flask_gui_mode = current_dir.name == 'src'
        return self._is_flask_gui_mode
    
    def _find_project_root(self):
        """プロジェクトルートディレクトリを自動検出"""
        current = Path.cwd()
        
        # Flask GUIモード（src/から実行）の場合
        if current.name == 'src':
            return current.parent
        
        # 通常モードの場合、CLAUDE.mdがある場所を探す
        for path in [current] + list(current.parents):
            if (path / 'CLAUDE.md').exists():
                return path
        
        # フォールバック
        return current
    
    def get_data_path(self, relative_path):
        """
        データディレクトリへの統一的なパスを取得
        
        Args:
            relative_path: data/ 以下の相対パス
            
        Returns:
            絶対パス
        """
        return self.project_root / "src" / "color_recommendation" / "data" / relative_path
    
    def get_used_colors_path(self, illustrator_name):
        """使用色データファイルのパスを取得"""
        return self.get_data_path(f"input/used_colors/used_colors_{illustrator_name}.json")
    
    def get_used_hues_path(self, illustrator_name):
        """使用色相データファイルのパスを取得"""
        return self.get_data_path(f"input/used_hues/used_hues_{illustrator_name}.json")
    
    def get_illustration_path(self, illustrator_name):
        """イラスト画像ディレクトリのパスを取得"""
        return self.get_data_path(f"input/illustration/{illustrator_name}")
    
    def get_statistics_path(self):
        """統計データファイルのパスを取得"""
        return self.get_data_path("input/statistics_for_illustrators.json")
    
    def get_output_path(self, relative_path):
        """出力ディレクトリへのパスを取得"""
        return self.get_data_path(f"output/{relative_path}")
    
    def get_recommend_colors_path(self, sort_type, filename):
        """推薦配色ファイルのパスを取得"""
        return self.get_output_path(f"recommend_colors/sort_by_{sort_type}/{filename}")
    
    def get_recommend_hues_path(self, sort_type, filename):
        """推薦色相ファイルのパスを取得"""
        return self.get_output_path(f"recommend_hues/sort_by_{sort_type}/{filename}")
    
    def get_recommend_tones_path(self, sort_type, filename):
        """推薦トーンファイルのパスを取得"""
        return self.get_output_path(f"recommend_tones/sort_by_{sort_type}/{filename}")
    
    def get_graph_path(self, filename):
        """グラフファイルのパスを取得"""
        return self.get_output_path(f"graph/{filename}")
    
    def get_heatmap_path(self, filename):
        """ヒートマップファイルのパスを取得"""
        return self.get_output_path(f"heatmap/{filename}")
    
    def get_recall_at_k_path(self, filename):
        """Recall@Kファイルのパスを取得"""
        return self.get_output_path(f"recall_at_k/{filename}")
    
    def get_color_palette_app_path(self, app_name, filename):
        """アプリ配色パレットファイルのパスを取得"""
        return self.get_data_path(f"input/color_palette_illust_app/{app_name}/{filename}")
    
    def ensure_output_dir(self, relative_path):
        """出力ディレクトリが存在しない場合は作成"""
        output_path = self.get_output_path(relative_path)
        output_path.mkdir(parents=True, exist_ok=True)
        return output_path


# グローバルインスタンス（シングルトンパターン）
_path_resolver = PathResolver()

# 便利関数（後方互換性のため）
def get_data_path(relative_path):
    """データディレクトリへの統一的なパスを取得"""
    return str(_path_resolver.get_data_path(relative_path))

def get_used_colors_path(illustrator_name):
    """使用色データファイルのパスを取得"""
    return str(_path_resolver.get_used_colors_path(illustrator_name))

def get_used_hues_path(illustrator_name):
    """使用色相データファイルのパスを取得"""
    return str(_path_resolver.get_used_hues_path(illustrator_name))

def get_illustration_path(illustrator_name):
    """イラスト画像ディレクトリのパスを取得"""
    return str(_path_resolver.get_illustration_path(illustrator_name))

def get_statistics_path():
    """統計データファイルのパスを取得"""
    return str(_path_resolver.get_statistics_path())

def get_output_path(relative_path):
    """出力ディレクトリへのパスを取得"""
    return str(_path_resolver.get_output_path(relative_path))

def get_recommend_colors_path(sort_type, filename):
    """推薦配色ファイルのパスを取得"""
    return str(_path_resolver.get_recommend_colors_path(sort_type, filename))

def get_recommend_hues_path(sort_type, filename):
    """推薦色相ファイルのパスを取得"""
    return str(_path_resolver.get_recommend_hues_path(sort_type, filename))

def get_recommend_tones_path(sort_type, filename):
    """推薦トーンファイルのパスを取得"""
    return str(_path_resolver.get_recommend_tones_path(sort_type, filename))

def get_graph_path(filename):
    """グラフファイルのパスを取得"""
    return str(_path_resolver.get_graph_path(filename))

def get_heatmap_path(filename):
    """ヒートマップファイルのパスを取得"""
    return str(_path_resolver.get_heatmap_path(filename))

def get_recall_at_k_path(filename):
    """Recall@Kファイルのパスを取得"""
    return str(_path_resolver.get_recall_at_k_path(filename))

def get_color_palette_app_path(app_name, filename):
    """アプリ配色パレットファイルのパスを取得"""
    return str(_path_resolver.get_color_palette_app_path(app_name, filename))

def ensure_output_dir(relative_path):
    """出力ディレクトリが存在しない場合は作成"""
    return str(_path_resolver.ensure_output_dir(relative_path))

# デバッグ用
def debug_paths():
    """現在のパス設定をデバッグ出力"""
    print(f"Current working directory: {Path.cwd()}")
    print(f"Project root: {_path_resolver.project_root}")
    print(f"Flask GUI mode: {_path_resolver.is_flask_gui_mode}")
    print(f"Statistics path: {get_statistics_path()}")
    print(f"Sample used_colors path: {get_used_colors_path('test')}")
    print(f"Sample output path: {get_output_path('test.json')}")