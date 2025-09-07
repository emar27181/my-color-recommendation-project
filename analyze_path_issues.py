#!/usr/bin/env python3
"""
Flask GUI パス問題分析ツール
色推薦システム内のハードコーディングされたパスを検出し、修正案を提供します。
"""

import os
import re
from pathlib import Path

def find_hardcoded_paths():
    """ハードコーディングされたパスを検索"""
    
    # 検索対象ディレクトリ
    search_dir = Path("src/color_recommendation")
    
    # パスパターンの定義
    patterns = {
        "hardcoded_src_path": r'["\']src/color_recommendation/',
        "data_input_illustration": r'data/input/illustration/',
        "data_input_used_colors": r'data/input/used_colors/',  
        "data_input_used_hues": r'data/input/used_hues/',
        "data_output": r'data/output/',
        "open_function": r'open\s*\(\s*["\']([^"\']+)["\']',
        "get_json_data": r'get_json_data\s*\(\s*["\']([^"\']+)["\']'
    }
    
    results = {pattern_name: [] for pattern_name in patterns}
    
    # Python ファイルを再帰的に検索
    for py_file in search_dir.rglob("*.py"):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                for line_num, line in enumerate(lines, 1):
                    for pattern_name, pattern in patterns.items():
                        matches = re.findall(pattern, line)
                        if matches:
                            results[pattern_name].append({
                                'file': str(py_file),
                                'line': line_num,
                                'content': line.strip(),
                                'matches': matches
                            })
                            
        except Exception as e:
            print(f"エラー読み取り {py_file}: {e}")
    
    return results

def analyze_path_patterns(results):
    """パスパターンを分析し、問題箇所を特定"""
    
    print("=" * 80)
    print("🔍 Flask GUI パス問題分析レポート")
    print("=" * 80)
    
    # 1. ハードコーディングされた src/ パス
    print("\n📁 1. ハードコーディングされた 'src/color_recommendation/' パス")
    print("-" * 60)
    
    hardcoded_paths = results["hardcoded_src_path"]
    if hardcoded_paths:
        for item in hardcoded_paths:
            rel_path = os.path.relpath(item['file'])
            print(f"  🚨 {rel_path}:{item['line']}")
            print(f"     {item['content']}")
            print()
    else:
        print("  ✅ ハードコードされたsrcパスは見つかりませんでした")
    
    # 2. data/input/illustration パス
    print("\n🖼️  2. data/input/illustration/ パス使用箇所")
    print("-" * 60)
    
    illustration_paths = results["data_input_illustration"]
    if illustration_paths:
        for item in illustration_paths:
            rel_path = os.path.relpath(item['file'])
            print(f"  📍 {rel_path}:{item['line']}")
            print(f"     {item['content']}")
            print()
    
    # 3. data/input/used_colors パス  
    print("\n🎨 3. data/input/used_colors/ パス使用箇所")
    print("-" * 60)
    
    used_colors_paths = results["data_input_used_colors"]
    if used_colors_paths:
        for item in used_colors_paths:
            rel_path = os.path.relpath(item['file'])
            print(f"  📍 {rel_path}:{item['line']}")
            print(f"     {item['content']}")
            print()
    
    # 4. data/input/used_hues パス
    print("\n🌈 4. data/input/used_hues/ パス使用箇所") 
    print("-" * 60)
    
    used_hues_paths = results["data_input_used_hues"]
    if used_hues_paths:
        for item in used_hues_paths:
            rel_path = os.path.relpath(item['file'])
            print(f"  📍 {rel_path}:{item['line']}")
            print(f"     {item['content']}")
            print()
    
    # 5. data/output パス
    print("\n📊 5. data/output/ パス使用箇所")
    print("-" * 60)
    
    output_paths = results["data_output"]
    if output_paths:
        count = 0
        for item in output_paths:
            count += 1
            if count <= 10:  # 最初の10件のみ表示
                rel_path = os.path.relpath(item['file'])
                print(f"  📍 {rel_path}:{item['line']}")
                print(f"     {item['content']}")
                print()
        if count > 10:
            print(f"  ... 他 {count - 10} 件")
    
    return hardcoded_paths, illustration_paths, used_colors_paths, used_hues_paths, output_paths

def generate_fix_recommendations():
    """修正案を生成"""
    
    print("\n" + "=" * 80)
    print("🛠️  修正案・推奨解決方法")
    print("=" * 80)
    
    print("""
📋 問題分析:
    1. Flask GUI は src/ ディレクトリから実行される
    2. しかし、color_recommendationモジュール内のパスは "src/color_recommendation/" で始まっている
    3. 結果的に "src/src/color_recommendation/data/..." のような不正なパスになる

✅ 解決方法1: 動的パス解決システム（推奨）
    
    以下のようなPath Utilityクラスを作成:
    
    ```python
    import os
    from pathlib import Path
    
    class PathResolver:
        def __init__(self):
            self.project_root = self._find_project_root()
            self.color_rec_dir = self.project_root / "src" / "color_recommendation"
        
        def _find_project_root(self):
            current = Path(__file__).parent
            while current.parent != current:
                if (current / "src" / "color_recommendation").exists():
                    return current
                current = current.parent
            raise RuntimeError("Project root not found")
        
        def get_data_path(self, relative_path: str) -> Path:
            if relative_path.startswith("src/color_recommendation/"):
                relative_path = relative_path[len("src/color_recommendation/"):]
            return self.color_rec_dir / relative_path
        
        def get_input_path(self, filename: str) -> Path:
            return self.color_rec_dir / "data" / "input" / filename
        
        def get_output_path(self, filename: str) -> Path:
            return self.color_rec_dir / "data" / "output" / filename
        
        def get_illustration_path(self, illustrator_name: str) -> Path:
            return self.color_rec_dir / "data" / "input" / "illustration" / illustrator_name
    ```
    
✅ 解決方法2: 条件付きパス調整（部分的解決）
    
    sort_color_scheme.py の例に従って各ファイルで:
    
    ```python
    import os
    
    def get_data_path(relative_path):
        if os.path.basename(os.getcwd()) == 'src':
            # Flask GUI から実行時
            return f"color_recommendation/{relative_path}"
        else:
            # 通常実行時 
            return f"src/color_recommendation/{relative_path}"
    ```

✅ 解決方法3: 環境変数ベース
    
    プロジェクトルートを環境変数で設定:
    
    ```python
    import os
    
    PROJECT_ROOT = os.environ.get('COLOR_REC_PROJECT_ROOT', 
                                  os.path.dirname(os.path.dirname(__file__)))
    
    def get_data_path(relative_path):
        return os.path.join(PROJECT_ROOT, "src", "color_recommendation", relative_path)
    ```

🎯 修正対象ファイル（優先順位順）:
    1. utils/sort_color_scheme.py - 既に部分実装済み、拡張対象
    2. utils/estimate_used_color_scheme.py - illustration/ パス使用
    3. utils/analyze_illustrator_statistics.py - illustration/ パス使用  
    4. utils/download_instagram_images.py - illustration/ パス使用
    5. utils/plot_graph.py - 多数のoutput/パス使用
    6. utils/estimate_used_color_method.py - used_colors/, used_hues/ パス使用
    7. color_recommendation.py - 推薦処理のメインファイル

🚀 実装手順:
    1. PathResolver クラスを utils/helpers/path_utils.py に作成
    2. 各モジュールでPathResolverをインポート・使用に変更
    3. ハードコーディングされたパスを動的パス解決に置き換え
    4. テスト実行: src/ と プロジェクトルート の両方で動作確認
""")

def check_sort_color_scheme_implementation():
    """sort_color_scheme.pyの動的パス実装を確認"""
    
    print("\n📋 参考実装: sort_color_scheme.py の動的パス調整")
    print("-" * 60)
    
    sort_file = Path("src/color_recommendation/utils/sort_color_scheme.py")
    
    try:
        with open(sort_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for i, line in enumerate(lines[110:120], 111):
            print(f"  {i:3}: {line.rstrip()}")
            
        print("\n✅ この実装パターンを他のファイルにも適用可能")
        
    except Exception as e:
        print(f"❌ sort_color_scheme.py を読み込めませんでした: {e}")

if __name__ == "__main__":
    # パス問題を分析
    results = find_hardcoded_paths()
    hardcoded, illustration, used_colors, used_hues, output = analyze_path_patterns(results)
    
    # 統計情報
    print(f"\n📊 統計:")
    print(f"  - ハードコード src/ パス: {len(hardcoded)} 箇所")  
    print(f"  - illustration/ パス: {len(illustration)} 箇所")
    print(f"  - used_colors/ パス: {len(used_colors)} 箇所")
    print(f"  - used_hues/ パス: {len(used_hues)} 箇所")
    print(f"  - output/ パス: {len(output)} 箇所")
    
    # 修正案を表示
    generate_fix_recommendations()
    
    # 参考実装を確認
    check_sort_color_scheme_implementation()
    
    print("\n" + "=" * 80)
    print("🎯 次のステップ: PathResolver クラスの実装と適用")
    print("=" * 80)