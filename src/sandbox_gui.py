"""
Flask GUI for sandbox2.py functionality
色推薦システムの機能をWebインターフェースで操作できるGUIアプリケーション
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_from_directory
import os
import sys
import json
from datetime import datetime
import traceback

# プロジェクトのルートディレクトリをPythonパスに追加
current_dir = os.path.dirname(__file__)
color_recommendation_dir = os.path.join(current_dir, 'color_recommendation')
sys.path.append(color_recommendation_dir)

# color_recommendationモジュールをインポート
from utils.analyze_illustrator_statistics import (
    save_statistics_for_illustrators, 
    get_not_monochrome_illustrator_list, 
    get_excluded_small_number_illustrator_list,
    print_statistics_for_illustrators
)
from color_recommendation import save_recommendations_for_illustrators
from utils.check_data_is_contained_next_color import save_data_is_contained_next_for_illustrators
from utils.plot_graph import save_plot_recall_at_k_for_illustrators

app = Flask(__name__)
app.secret_key = 'sandbox-gui-secret-key-2025'

# デフォルトのイラストレーターリスト（sandbox2.pyから）
DEFAULT_ILLUSTRATOR_LIST = [
    "mika_pikazo_mpz", "harunonioikaze", "gaako_illust", 
    "mokmok_skd", "nest_virgo", "omrice4869", "oz_yarimasu", 
    "sa_ka_na_4", "trcoot", "birdstory_pic", "amao_1015",
    "meeesuke_", "shirokumaai", "tsumugitopan", "sexygirl.jp", 
    "obungu_mofumofu", "skt2ing", "iina.gram", "chi_bee.official", 
    "harupeipei", "bj00100", "jerome_trez_oudot", "deppa_53"
]

# 設定オプション
SORT_TYPES = ["random", "color_diff", "used_color_count", "no_sort", "mean_resultant_length", "custom_v0"]
RECOMMEND_TYPES = ["color", "hue", "tone", "color_existing_apps", "hue_existing_apps", "tone_existing_apps"]
APP_NAMES = ["clipstudio", "ibispaint", "medibang", "pixivsketch", "powerpoint"]
LEGEND_LOCATIONS = ["lower right", "upper right", "upper left", "lower left"]

@app.route('/')
def index():
    """メインページ"""
    return render_template('sandbox_gui.html', 
                         illustrators=DEFAULT_ILLUSTRATOR_LIST,
                         sort_types=SORT_TYPES,
                         recommend_types=RECOMMEND_TYPES,
                         app_names=APP_NAMES,
                         legend_locations=LEGEND_LOCATIONS)

@app.route('/run_statistics', methods=['POST'])
def run_statistics():
    """統計データの生成"""
    try:
        # フォームデータ取得
        selected_illustrators = request.form.getlist('illustrators')
        min_count = int(request.form.get('min_count', 10))
        
        if not selected_illustrators:
            flash('イラストレーターを選択してください', 'error')
            return redirect(url_for('index'))
        
        # フィルタリング処理
        filtered_illustrators = get_not_monochrome_illustrator_list(selected_illustrators)
        filtered_illustrators = get_excluded_small_number_illustrator_list(filtered_illustrators, min_count)
        
        # 統計データ生成実行
        save_statistics_for_illustrators(filtered_illustrators)
        
        flash(f'統計データが生成されました（{len(filtered_illustrators)}名）', 'success')
        return redirect(url_for('index'))
        
    except Exception as e:
        flash(f'エラーが発生しました: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/run_recommendations', methods=['POST'])
def run_recommendations():
    """推薦配色の生成"""
    try:
        # フォームデータ取得
        selected_illustrators = request.form.getlist('illustrators')
        recommend_type = request.form.get('recommend_type', 'color')
        sort_type = request.form.get('sort_type', 'random')
        app_name = request.form.get('app_name', '')
        diff_values_str = request.form.get('diff_values', '20, -20, 40, -40, 60, -60, 80, -80')
        
        if not selected_illustrators:
            flash('イラストレーターを選択してください', 'error')
            return redirect(url_for('index'))
        
        # 明度差分値の解析
        try:
            diff_values = [int(x.strip()) for x in diff_values_str.split(',') if x.strip()]
        except ValueError:
            diff_values = [20, -20, 40, -40, 60, -60, 80, -80]
        
        # フィルタリング処理
        min_count = int(request.form.get('min_count', 10))
        filtered_illustrators = get_not_monochrome_illustrator_list(selected_illustrators)
        filtered_illustrators = get_excluded_small_number_illustrator_list(filtered_illustrators, min_count)
        
        # 推薦配色生成実行
        save_recommendations_for_illustrators(
            filtered_illustrators, 
            recommend_type, 
            sort_type, 
            diff_values, 
            app_name
        )
        
        flash(f'推薦配色が生成されました（{len(filtered_illustrators)}名, {recommend_type}, {sort_type}）', 'success')
        return redirect(url_for('index'))
        
    except Exception as e:
        flash(f'エラーが発生しました: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/run_evaluation', methods=['POST'])
def run_evaluation():
    """評価データの生成"""
    try:
        # フォームデータ取得
        selected_illustrators = request.form.getlist('illustrators')
        sort_type = request.form.get('sort_type', 'random')
        recommend_type = request.form.get('recommend_type', 'color')
        app_name = request.form.get('app_name', '')
        
        if not selected_illustrators:
            flash('イラストレーターを選択してください', 'error')
            return redirect(url_for('index'))
        
        # フィルタリング処理
        min_count = int(request.form.get('min_count', 10))
        filtered_illustrators = get_not_monochrome_illustrator_list(selected_illustrators)
        filtered_illustrators = get_excluded_small_number_illustrator_list(filtered_illustrators, min_count)
        
        # 評価データ生成実行
        save_data_is_contained_next_for_illustrators(
            filtered_illustrators, 
            sort_type, 
            recommend_type, 
            app_name
        )
        
        flash(f'評価データが生成されました（{len(filtered_illustrators)}名）', 'success')
        return redirect(url_for('index'))
        
    except Exception as e:
        flash(f'エラーが発生しました: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/run_visualization', methods=['POST'])
def run_visualization():
    """グラフ・可視化の生成"""
    try:
        # フォームデータ取得
        selected_illustrators = request.form.getlist('illustrators')
        sort_type = request.form.get('sort_type', 'random')
        recommend_type = request.form.get('recommend_type', 'color')
        app_name = request.form.get('app_name', '')
        legend_location = request.form.get('legend_location', 'lower right')
        
        if not selected_illustrators:
            flash('イラストレーターを選択してください', 'error')
            return redirect(url_for('index'))
        
        # フィルタリング処理
        min_count = int(request.form.get('min_count', 10))
        filtered_illustrators = get_not_monochrome_illustrator_list(selected_illustrators)
        filtered_illustrators = get_excluded_small_number_illustrator_list(filtered_illustrators, min_count)
        
        # グラフ生成実行
        save_plot_recall_at_k_for_illustrators(
            filtered_illustrators, 
            sort_type, 
            recommend_type, 
            app_name, 
            legend_location
        )
        
        flash(f'グラフが生成されました（{len(filtered_illustrators)}名）', 'success')
        return redirect(url_for('index'))
        
    except Exception as e:
        flash(f'エラーが発生しました: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/get_illustrator_stats')
def get_illustrator_stats():
    """イラストレーター統計情報をJSON形式で返す"""
    try:
        selected_illustrators = request.args.getlist('illustrators')
        min_count = int(request.args.get('min_count', 10))
        
        if not selected_illustrators:
            return jsonify({'error': 'No illustrators selected'})
        
        # フィルタリング処理
        filtered_illustrators = get_not_monochrome_illustrator_list(selected_illustrators)
        filtered_illustrators = get_excluded_small_number_illustrator_list(filtered_illustrators, min_count)
        
        stats = {
            'selected_count': len(selected_illustrators),
            'filtered_count': len(filtered_illustrators),
            'filtered_list': filtered_illustrators
        }
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/output_files')
def output_files():
    """出力ファイル一覧ページ"""
    try:
        output_dir = os.path.join(os.path.dirname(__file__), 'color_recommendation', 'data', 'output')
        files = []
        
        if os.path.exists(output_dir):
            for root, dirs, filenames in os.walk(output_dir):
                for filename in filenames:
                    if filename.endswith(('.png', '.json')):
                        rel_path = os.path.relpath(os.path.join(root, filename), output_dir)
                        file_info = {
                            'name': filename,
                            'path': rel_path,
                            'size': os.path.getsize(os.path.join(root, filename)),
                            'modified': datetime.fromtimestamp(
                                os.path.getmtime(os.path.join(root, filename))
                            ).strftime('%Y-%m-%d %H:%M:%S')
                        }
                        files.append(file_info)
        
        # 更新日時順でソート
        files.sort(key=lambda x: x['modified'], reverse=True)
        
        return render_template('output_files.html', files=files)
        
    except Exception as e:
        flash(f'ファイル一覧の取得でエラーが発生しました: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/download/<path:filename>')
def download_file(filename):
    """出力ファイルのダウンロード"""
    try:
        output_dir = os.path.join(os.path.dirname(__file__), 'color_recommendation', 'data', 'output')
        return send_from_directory(output_dir, filename, as_attachment=True)
    except Exception as e:
        flash(f'ファイルダウンロードでエラーが発生しました: {str(e)}', 'error')
        return redirect(url_for('output_files'))

if __name__ == '__main__':
    # テンプレートディレクトリの作成
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    if not os.path.exists(template_dir):
        os.makedirs(template_dir)
    
    app.run(debug=True, host='127.0.0.1', port=5000)