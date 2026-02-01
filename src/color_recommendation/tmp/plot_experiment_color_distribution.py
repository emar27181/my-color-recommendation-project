"""実験画像の色相環分布とトーン散布図を生成するスクリプト"""
import sys
import os
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import colorsys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.helpers.transform_color import rgb_to_hsl

IMAGE_BASE = os.path.join(os.path.dirname(__file__), '..', 'data', 'input', 'experiment_result', 'image')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'output', 'experiment_analysis')

UI_TASKS = [("UI1", "task1"), ("UI1", "task2"), ("UI2", "task1"), ("UI2", "task2")]


def load_colors(ui, task):
    path = os.path.join(IMAGE_BASE, ui, task, 'used_colors.json')
    with open(path, 'r') as f:
        return json.load(f)


def rgb_to_display_color(rgb):
    return tuple(c / 255.0 for c in rgb)


def plot_hue_wheel(ui, task, data, ax):
    """色相環上に使用色をプロット（rateで点サイズを変える）"""
    for name, colors in data.items():
        for c in colors:
            rgb = c['rgb']
            hsl = rgb_to_hsl(tuple(rgb))
            hue_deg = hsl[0]
            sat = hsl[1]
            light = hsl[2]
            # 無彩色(S<10 or L<10 or L>90)はスキップ
            if sat < 10 or light < 10 or light > 90:
                continue
            hue_rad = np.deg2rad(hue_deg)
            radius = 0.3 + 0.7 * (sat / 100.0)  # 彩度で半径を変える
            size = max(c['rate'] * 800, 8)
            ax.scatter(hue_rad, radius, s=size, c=[rgb_to_display_color(rgb)],
                       edgecolors='#333', linewidths=0.3, alpha=0.7, zorder=3)

    # 色相環の背景リング
    theta = np.linspace(0, 2 * np.pi, 360)
    for t in theta:
        hue = np.rad2deg(t) / 360.0
        rgb_bg = colorsys.hls_to_rgb(hue, 0.5, 1.0)
        ax.bar(t, 0.08, bottom=1.05, width=np.deg2rad(1.5),
               color=rgb_bg, edgecolor='none', alpha=0.8)

    ax.set_ylim(0, 1.15)
    ax.set_yticks([0.3, 0.65, 1.0])
    ax.set_yticklabels(['S=0', 'S=50', 'S=100'], fontsize=7, color='#555')
    ax.set_title(f'{ui} - {task}', fontsize=12, fontweight='bold', pad=15, color='black')
    ax.set_facecolor('#fafafa')
    ax.grid(True, alpha=0.3)


def plot_tone_scatter(ui, task, data, ax):
    """トーン散布図（横軸:彩度, 縦軸:明度）"""
    for name, colors in data.items():
        for c in colors:
            rgb = c['rgb']
            hsl = rgb_to_hsl(tuple(rgb))
            sat = hsl[1]
            light = hsl[2]
            size = max(c['rate'] * 800, 8)
            ax.scatter(sat, light, s=size, c=[rgb_to_display_color(rgb)],
                       edgecolors='#333', linewidths=0.3, alpha=0.7, zorder=3)

    ax.set_xlim(-2, 102)
    ax.set_ylim(-2, 102)
    ax.set_xlabel('Saturation (%)', fontsize=10, color='black')
    ax.set_ylabel('Lightness (%)', fontsize=10, color='black')
    ax.set_title(f'{ui} - {task}', fontsize=12, fontweight='bold', color='black')
    ax.tick_params(colors='black')
    ax.set_facecolor('#fafafa')
    ax.grid(True, alpha=0.3)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # --- 色相環プロット ---
    fig, axes = plt.subplots(2, 2, figsize=(12, 12), subplot_kw={'projection': 'polar'})
    fig.suptitle('Hue Distribution on Color Wheel (per UI/Task)', fontsize=14, fontweight='bold', color='black', y=0.98)
    for idx, (ui, task) in enumerate(UI_TASKS):
        ax = axes[idx // 2][idx % 2]
        data = load_colors(ui, task)
        plot_hue_wheel(ui, task, data, ax)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    hue_path = os.path.join(OUTPUT_DIR, 'hue_distribution_color_wheel.pdf')
    fig.savefig(hue_path, format='pdf', bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"Saved: {hue_path}")

    # --- トーン散布図 ---
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('Tone Distribution (Saturation vs Lightness)', fontsize=14, fontweight='bold', color='black', y=0.98)
    for idx, (ui, task) in enumerate(UI_TASKS):
        ax = axes[idx // 2][idx % 2]
        data = load_colors(ui, task)
        plot_tone_scatter(ui, task, data, ax)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    tone_path = os.path.join(OUTPUT_DIR, 'tone_distribution_scatter.pdf')
    fig.savefig(tone_path, format='pdf', bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"Saved: {tone_path}")


if __name__ == "__main__":
    main()
