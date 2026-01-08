# 色推薦システム 詳細分析ドキュメント

## 目次

1. [システム概要](#1-システム概要)
2. [使用配色の抽出](#2-使用配色の抽出)
3. [使用割合の抽出とベースカラーの決定](#3-使用割合の抽出とベースカラーの決定)
4. [推薦配色の生成](#4-推薦配色の生成)
5. [推薦順序計算](#5-推薦順序計算)
6. [評価方法](#6-評価方法)
7. [システムフローチャート](#7-システムフローチャート)

---

## 1. システム概要

本色推薦システムは、イラストレーターの過去作品から色使用傾向を学習し、個人の色彩感覚に適合した配色を推薦する機構である。システムは以下の5段階で構成される：

```
[画像] → [色抽出] → [統計分析] → [推薦生成] → [並び替え] → [評価]
```

---

## 2. 使用配色の抽出

### 2.1 概要

イラスト画像から使用されている色を抽出し、類似色を統合して代表色を決定する処理。

**実装ファイル**: `estimate_used_color_scheme.py`

### 2.2 ColorThiefによる色抽出

#### 設定値

```python
# estimate_used_color_scheme.py: Line 72-87
color_count = 30      # 抽出する色の数
quality = 10          # 抽出品質（1-10, 大きいほど高速・低品質）
```

#### 処理フロー

```python
def estimate_used_colors_by_colorthief(image_path, color_count):
    color_thief = ColorThief(image_path)
    palette = color_thief.get_palette(color_count=30, quality=10)
    return palette
```

**数式表現**:
```
P = ColorThief.extract(I, n=30, q=10)
where:
  P: 抽出されたパレット（RGB色のリスト）
  I: 入力画像
  n: 抽出色数
  q: 品質パラメータ
```

### 2.3 類似色統合

#### 統合閾値

```python
# estimate_used_color_scheme.py: Line 48-49, 97-142
ΔE統合閾値_使用色 = 5      # merge_similar_color()の閾値
ΔE統合閾値_パレット = 10    # merge_same_color_palette()の閾値
```

#### 統合アルゴリズム（ΔE ≤ 10）

```python
def merge_same_color_palette(palette, threshold=10):
    merged_palette = []

    while len(palette) > 0:
        base_color = palette[0]
        to_merge_colors = [base_color]
        palette = palette[1:]

        # 類似色を検索
        for i in range(len(palette) - 1, -1, -1):
            if calculate_color_difference_delta_e_cie2000(base_color, palette[i]) < threshold:
                to_merge_colors.append(palette[i])
                palette.pop(i)

        # 平均色を計算
        merged_color = [0, 0, 0]
        for color in to_merge_colors:
            merged_color[0] += color[0]
            merged_color[1] += color[1]
            merged_color[2] += color[2]
        merged_color = [int(c / len(to_merge_colors)) for c in merged_color]

        merged_palette.append(merged_color)

    return merged_palette
```

**数式表現**:
```
統合条件: ΔE(C_i, C_j) ≤ τ
統合後の色: C_merged = (1/n) Σ C_k  (k ∈ 統合対象色)

where:
  ΔE: CIE2000色差
  τ: 閾値（5または10）
  n: 統合される色数
```

### 2.4 ピクセル分類と使用率計算

#### ユークリッド距離による分類

```python
# estimate_used_color_scheme.py: Line 158-196
ユークリッド距離閾値 = 0.1  # 正規化RGB距離

def color_count_by_color_palette(color_palette, image_path):
    image = Image.open(image_path)
    color_pixels = list(image.getdata())
    color_palette_count = [0] * len(color_palette)

    for color_pixel in color_pixels:
        for i in range(len(color_palette)):
            if calculate_rgb_distance_by_euclidean(color_palette[i], color_pixel[:3]) < 0.1:
                color_palette_count[i] += 1

    # 使用率計算
    color_palette_rate = [count / classified_color_count for count in color_palette_count]

    return color_palette, color_palette_rate
```

**数式表現**:
```
距離関数: d(C_p, C_i) = √[(R_p - R_i)² + (G_p - G_i)² + (B_p - B_i)²] / √(255² × 3)

分類条件: pixel_i ∈ Palette_j if d(Palette_j, pixel_i) < 0.1

使用率: rate_j = count_j / Σ count_k
```

### 2.5 有彩色判定

#### 判定基準

```python
# constants_dev.py: Line 5-7
SATURATION_LOWER_LIMIT = 10    # 彩度下限（%）
LIGHTNESS_LOWER_LIMIT = 10     # 明度下限（%）
LIGHTNESS_UPPER_LIMIT = 90     # 明度上限（%）
```

```python
def delete_achromatic(color_scheme):
    color_scheme = [color for color in color_scheme
                    if rgb_to_hsl(color[0])[1] > SATURATION_LOWER_LIMIT]
    color_scheme = [color for color in color_scheme
                    if rgb_to_hsl(color[0])[2] > LIGHTNESS_LOWER_LIMIT]
    color_scheme = [color for color in color_scheme
                    if rgb_to_hsl(color[0])[2] < LIGHTNESS_UPPER_LIMIT]
    return color_scheme
```

**数式表現**:
```
有彩色条件:
  S > 10% AND 10% < L < 90%

where:
  S: HSL彩度
  L: HSL明度
```

### 2.6 最終出力形式

```json
[
  {
    "illustName": "path/to/image.jpg",
    "color": "#efeae3",
    "rate": 0.237894,
    "amount": -1
  },
  ...
]
```

---

## 3. 使用割合の抽出とベースカラーの決定

### 3.1 概要

イラストレーターの色使用統計を分析し、推薦配色生成・並び替えに使用する統計データを生成する。

**実装ファイル**: `analyze_illustrator_statistics.py`

### 3.2 ベースカラーの決定

**決定方法**: 使用率が最も高い有彩色を自動選択

```python
# color_recommendation.py: Line 225
base_color_rgb = hex_to_rgb(illust_data[0]['color'])  # 配列の先頭要素
```

**データ形式**: 使用色データは使用率降順でソート済み（`estimate_used_color_scheme.py: Line 52`）

```python
merged_used_color_schemes = sorted(merged_used_color_schemes,
                                   key=lambda x: x[1],
                                   reverse=True)
```

### 3.3 統計データの種類

#### 3.3.1 色数統計

```python
# analyze_illustrator_statistics.py: Line 99-108, 151-155
chromatic_colors_count_sum = 0        # 有彩色数の合計
achromatic_colors_count_sum = 0       # 無彩色数の合計
chromatic_colors_count_distribution = [0] * 20  # 0色〜19色の頻度分布
```

**数式表現**:
```
平均有彩色数: μ_chroma = (1/N) Σ n_chroma_i

色数分布: D[k] = |{i | n_chroma_i = k}|

where:
  N: イラスト総数
  n_chroma_i: イラストiの有彩色数
  D[k]: k色を使用したイラスト数
```

#### 3.3.2 色相統計（PCCS 24色相）

```python
# analyze_illustrator_statistics.py: Line 104, 146-148
used_pccs_count_sum_distribution = [0] * 25  # PCCS色相0-24の使用頻度
```

**数式表現**:
```
PCCS分布: P[h] = Σ δ(pccs_i = h)

where:
  P[h]: PCCS色相hの使用回数
  δ: クロネッカーのデルタ関数
  pccs_i: i番目の色のPCCS色相番号（0-24）
```

#### 3.3.3 平均結果長統計

```python
# analyze_illustrator_statistics.py: Line 14-36, 137-144
def _mean_resultant_length(angles_deg):
    if len(angles_deg) == 0:
        return 0

    angles_rad = [math.radians(angle) for angle in angles_deg]
    sum_cos = sum(math.cos(angle) for angle in angles_rad)
    sum_sin = sum(math.sin(angle) for angle in angles_rad)

    n = len(angles_rad)
    avg_cos = sum_cos / n
    avg_sin = sum_sin / n

    R = math.sqrt(avg_cos**2 + avg_sin**2)
    return R
```

**数式表現**:
```
平均結果長: R = √[(C̄)² + (S̄)²]

where:
  C̄ = (1/n) Σ cos(θ_i)
  S̄ = (1/n) Σ sin(θ_i)
  θ_i: 色相角度（ラジアン）
  n: 色数

意味:
  R ≈ 1: 色相が集中（類似色使用）
  R ≈ 0: 色相が分散（多様な色使用）
```

#### 3.3.4 明度彩度分布統計（5×5マトリックス）

**重要**: 2025-09-05修正版では出現率を考慮した重み付きカウントを実装

```python
# analyze_illustrator_statistics.py: Line 38-81, 164-179
DIVIDE_NUM = 4  # 5×5マトリックス（0-4の5段階）

def _get_saturation_lightness_count_distribution(illustrator_name, illust_name, index_num):
    saturation_lightness_count_distribution = [[0 for _ in range(DIVIDE_NUM + 1)]
                                                for _ in range(DIVIDE_NUM + 1)]

    for used_color_info in used_colors_info:
        used_color_rate = used_color_info['rate']  # 出現率取得（2025-09-05修正）
        used_color_hsl = rgb_to_hsl(hex_to_rgb(used_color_info['color']))

        saturation_index = round(used_color_hsl[1] / (100 / DIVIDE_NUM))
        lightness_index = round(used_color_hsl[2] / (100 / DIVIDE_NUM))

        # 出現率で重み付けカウント（2025-09-05修正）
        saturation_lightness_count_distribution[lightness_index][saturation_index] += used_color_rate

    # 正規化（合計を1にする）
    total = sum(sum(row) for row in saturation_lightness_count_distribution)
    if total > 0:
        for i in range(len(saturation_lightness_count_distribution)):
            for j in range(len(saturation_lightness_count_distribution[i])):
                saturation_lightness_count_distribution[i][j] /= total

    return saturation_lightness_count_distribution
```

**数式表現**:
```
座標変換:
  idx_S = ⌊S / 20⌋  (0 ≤ idx_S ≤ 4)
  idx_L = ⌊L / 20⌋  (0 ≤ idx_L ≤ 4)

重み付きカウント（2025-09-05修正）:
  M[idx_L][idx_S] = Σ rate_k  (k: 該当するトーンの色)

正規化:
  M'[i][j] = M[i][j] / Σ Σ M[i][j]

where:
  M: トーン分布マトリックス
  rate_k: 色kの出現率
  S, L: 彩度・明度（0-100%）
```

**マトリックス構造**:
```
         彩度 →
       0    1    2    3    4
明  0 [低L  低L  低L  低L  低L]
度     低S  中低S 中S  中高S 高S
↓  1 [中低L 中低L 中低L 中低L 中低L]
      低S  中低S 中S  中高S 高S
   2 [中L  中L  中L  中L  中L]
      低S  中低S 中S  中高S 高S
   3 [中高L 中高L 中高L 中高L 中高L]
      低S  中低S 中S  中高S 高S
   4 [高L  高L  高L  高L  高L]
      低S  中低S 中S  中高S 高S

各値: 正規化された出現率（合計=1.0）
```

### 3.4 統計データアクセス

```python
# 統計データ取得関数
def get_statistics_by_illustrator(illustrator_name, keyword):
    statistics = _extract_statistics_by_illustrator(illustrator_name)

    if keyword == "all":
        return statistics
    else:
        return statistics[keyword]

# 使用例
tone_dist = get_statistics_by_illustrator('amao_1015', 'saturation_lightness_count_distribution')
color_count_dist = get_statistics_by_illustrator('amao_1015', 'chromatic_colors_count_distribution')
```

---

## 4. 推薦配色の生成

### 4.1 色相推薦（Hue Recommendation）

#### 概要

17種類の配色技法を適用し、ベースカラーの色相を基準とした調和配色を生成する。

**実装ファイル**: `generate_color_scheme_method.py`, `color_recommendation.py`

#### 4.1.1 配色技法一覧

| 配色技法 | 色数 | 色相角度差 | 配色数 | 実装行 |
|---------|-----|-----------|--------|--------|
| アイデンティティ（同一色） | 1 | - | 1 | 66-68 |
| アナロジー（類似色） | 2 | ±30° | 2 | 72-75 |
| 中間色 | 2 | ±90° | 2 | 78-81 |
| ダイアド（補色） | 2 | 180° | 1 | 84-86 |
| 対立色 | 2 | ±150° | 2 | 89-92 |
| ドミナント | 3 | [+30°,+60°], [-30°,+30°], [-60°,-30°] | 3 | 96-100 |
| スプリット補色 | 3 | [+150°,-150°], [-150°,+60°], [-60°,+150°] | 3 | 103-107 |
| トライアド | 3 | [+120°,+240°] | 1 | 110-112 |
| テトラード（四色） | 4 | [+90°,+180°,+270°] | 1 | 116-118 |
| ペンタード（五色） | 5 | [+72°,+144°,+216°,+288°] | 1 | 122-124 |
| ヘキサード（六色） | 6 | [+60°,+120°,+180°,+240°,+300°] | 1 | 128-130 |
| **合計** | **-** | **-** | **17** | **-** |

#### 4.1.2 配色生成関数

```python
def generate_color_scheme(base_color_rgb, hue_differences):
    base_color_hsl = rgb_to_hsl(base_color_rgb)
    base_color_hue = base_color_hsl[0]
    base_color_saturation = base_color_hsl[1]
    base_color_lightness = base_color_hsl[2]

    color_scheme = [base_color_rgb]

    for hue_difference in hue_differences:
        new_hue = (base_color_hue + hue_difference) % 360
        color_scheme.append(hsl_to_rgb(new_hue, base_color_saturation, base_color_lightness))

    return color_scheme
```

**数式表現**:
```
配色生成: C_i = (H_base + Δh_i mod 360, S_base, L_base)

where:
  C_i: i番目の推薦色
  H_base: ベースカラーの色相（0-360°）
  Δh_i: 配色技法で定義された色相差
  S_base, L_base: ベースカラーの彩度・明度
```

#### 4.1.3 配色技法の具体例

**アナロジー配色（類似色）**:
```python
def generate_analogy_color_scheme(base_color_rgb):
    color_scheme1 = generate_color_scheme(base_color_rgb, [30])   # +30°
    color_scheme2 = generate_color_scheme(base_color_rgb, [-30])  # -30°
    return color_scheme1, color_scheme2
```

**トライアド配色（三色配色）**:
```python
def generate_triad_color_scheme(base_color_rgb):
    color_scheme = generate_color_scheme(base_color_rgb, [120, 240])
    return color_scheme,
```

**ヘキサード配色（六色配色）**:
```python
def generate_hexad_color_scheme(base_color_rgb):
    color_scheme = generate_color_scheme(base_color_rgb, [60, 120, 180, 240, 300])
    return color_scheme,
```

#### 4.1.4 推薦生成の統合

```python
# color_recommendation.py: Line 89-116
def generate_recommend_hues_by_illustrator(data, sort_type, illustrator_name):
    output_data = []

    for illust_data in data:
        if not illust_data:
            continue

        # 使用配色のRGB形式のリストを取得
        used_color_scheme_rgb = []
        for color_scheme_data in illust_data:
            used_color_scheme_rgb.append(hex_to_rgb(color_scheme_data['color']))

        # 17パターンの推薦配色生成
        recommend_color_schemes_rgb = get_recommendations(
            used_color_scheme_rgb, "hue", sort_type, illustrator_name, None
        )

        new_illust_data = {
            "illust_name": illust_data[0]['illustName'],
            "color_scheme": illust_data,
            "recommend_color_schemes": convert_color_schemes_to_color_data(
                transform_color_schemes_rgb_to_hex(recommend_color_schemes_rgb)
            ),
        }

        output_data.append(new_illust_data)

    return output_data
```

### 4.2 トーン推薦（Tone Recommendation）

#### 概要

ベースカラーの明度・彩度を変化させたバリエーションを生成する。

**実装ファイル**: `add_variations_color_scheme.py`, `color_recommendation.py`

#### 4.2.1 バリエーション生成パラメータ

```python
# 典型的な設定（sandbox.pyより）
diff_values = [-40, -20, 0, +20, +40]  # 明度・彩度の差分値（%）

# 生成される配色数
配色数 = len(diff_values) × len(diff_values) = 5 × 5 = 25パターン
```

#### 4.2.2 トーン推薦生成関数

```python
# color_recommendation.py: Line 183-207
def generate_recommend_tones_by_illustrator(data, sort_type, illustrator_name, diff_values):
    output_data = []

    for illust_data in data:
        if not illust_data:
            continue

        used_color_scheme_rgb = []
        for color_scheme_data in illust_data:
            used_color_scheme_rgb.append(hex_to_rgb(color_scheme_data['color']))

        # トーン推薦生成
        recommend_color_schemes_rgb = get_recommendations(
            used_color_scheme_rgb, "tone", sort_type, illustrator_name, diff_values
        )

        new_illust_data = {
            "illust_name": illust_data[0]['illustName'],
            "color_scheme": illust_data,
            "recommend_color_schemes": convert_color_schemes_to_color_data(
                transform_color_schemes_rgb_to_hex(recommend_color_schemes_rgb)
            ),
        }

        output_data.append(new_illust_data)

    return output_data
```

#### 4.2.3 バリエーション生成アルゴリズム

```python
# add_variations_color_scheme.py: Line 33-46
def add_saturation_and_lightness_variations_color_scheme(color_scheme, saturation_diff, lightness_diff):
    new_color_scheme = []

    for color_rgb in color_scheme:
        color_hsl = rgb_to_hsl(color_rgb)
        new_color = hsl_to_rgb(
            color_hsl[0],
            color_hsl[1] + saturation_diff,
            color_hsl[2] + lightness_diff
        )

        if is_valid_color(new_color):  # RGB値が有効範囲内か確認
            new_color_scheme.append(new_color)

    return new_color_scheme
```

**数式表現**:
```
バリエーション生成: C'_ij = (H_base, S_base + ΔS_i, L_base + ΔL_j)

where:
  C'_ij: (i,j)番目のバリエーション色
  ΔS_i ∈ {-40, -20, 0, +20, +40}  (彩度変化)
  ΔL_j ∈ {-40, -20, 0, +20, +40}  (明度変化)

有効性条件:
  0 ≤ R, G, B ≤ 255
  無効な場合は配色から除外
```

#### 4.2.4 生成フロー

```python
# color_recommendation.py: Line 61-77
recommend_base_color_schemes_rgb = generate_one_color_schemes(base_color_rgb)  # 1色配色
recommend_color_schemes_rgb = recommend_base_color_schemes_rgb.copy()

# 明度彩度が異なる色を追加
for lightness_diff in diff_values:
    for saturation_diff in diff_values:
        recommend_color_schemes_rgb += get_variations_for_color_schemes(
            recommend_base_color_schemes_rgb,
            lightness_diff,
            saturation_diff,
            "saturation_and_lightness"
        )

# 空の配色を削除
recommend_color_schemes_rgb = remove_empty_color_scheme_from_color_schemes(recommend_color_schemes_rgb)

# 無彩色を削除
recommend_color_schemes_rgb = remove_monochrome_color_from_color_schemes(recommend_color_schemes_rgb)
```

### 4.3 色推薦（Color Recommendation）

#### 概要

色相推薦とトーン推薦を組み合わせた統合推薦。17種配色技法に対してそれぞれ明度彩度バリエーションを生成。

**実装ファイル**: `color_recommendation.py`

#### 4.3.1 色推薦生成フロー

```python
# color_recommendation.py: Line 210-261
def generate_recommend_colors_by_illustrator(data, sort_type, illustrator_name, diff_values):
    output_data = []

    for illust_data in data:
        if not illust_data:
            continue

        used_color_scheme_rgb = []
        for color_scheme_data in illust_data:
            used_color_scheme_rgb.append(hex_to_rgb(color_scheme_data['color']))

        # ベース配色生成（17パターン）
        base_color_rgb = hex_to_rgb(illust_data[0]['color'])
        recommend_base_color_schemes_rgb = generate_all_color_schemes(base_color_rgb)
        recommend_color_schemes_rgb = recommend_base_color_schemes_rgb.copy()

        # 各ベース配色に対してバリエーション追加
        for lightness_diff in diff_values:
            for saturation_diff in diff_values:
                recommend_color_schemes_rgb += get_variations_for_color_schemes(
                    recommend_base_color_schemes_rgb,
                    lightness_diff,
                    saturation_diff,
                    "saturation_and_lightness"
                )

        # 無彩色と空配色を削除
        recommend_color_schemes_rgb = remove_monochrome_color_from_color_schemes(recommend_color_schemes_rgb)
        recommend_color_schemes_rgb = remove_empty_color_scheme_from_color_schemes(recommend_color_schemes_rgb)

        # 並び替え
        recommend_color_schemes_rgb = sort_recommend_color_schemes_rgb(
            recommend_color_schemes_rgb, used_color_scheme_rgb, sort_type, illustrator_name
        )

        new_illust_data = {
            "illust_name": illust_data[0]['illustName'],
            "color_scheme": illust_data,
            "recommend_color_schemes": convert_color_schemes_to_color_data(
                transform_color_schemes_rgb_to_hex(recommend_color_schemes_rgb)
            ),
        }

        output_data.append(new_illust_data)

    return output_data
```

**数式表現**:
```
色推薦配色数: N_color = N_hue × N_tone

where:
  N_hue = 17  (配色技法数)
  N_tone = 25  (diff_values = [-40, -20, 0, +20, +40]の場合)
  N_color ≈ 17 × 25 = 425配色（無効配色除去前）
```

---

## 5. 推薦順序計算

### 5.1 概要

生成された推薦配色を、イラストレーターの色使用傾向に基づいて並び替える。

**実装ファイル**: `sort_color_scheme.py`, `color_recommendation.py`

### 5.2 並び替え方式一覧

| 方式 | 概要 | 統計データ | 実装行 |
|-----|------|-----------|--------|
| `random` | ランダム並び替え | 不要 | 312-317 |
| `color_diff` | 色差順（ΔE昇順） | 不要 | 12-42 |
| `used_color_count` | 使用色数順 | chromatic_colors_count_distribution | 134-158 |
| `mean_resultant_length` | 平均結果長順 | mean_resultant_length_distribution | 69-100 |
| `used_tone` | トーン使用頻度順 | saturation_lightness_count_distribution | 227-278 |
| `custom_v0` | カスタム評価関数 | 複合 | 190-225 |
| `no_sort` | 並び替えなし | 不要 | - |

### 5.3 色差順並び替え（color_diff）

#### アルゴリズム

```python
# sort_color_scheme.py: Line 12-42
def sort_color_schemes_by_color_difference(base_color_scheme, color_schemes):
    color_schemes.sort(
        key=lambda color_scheme: calc_color_scheme_difference_delta_e_cie2000(
            base_color_scheme, color_scheme
        )
    )
    return color_schemes
```

**数式表現**:
```
ソートキー: ΔE_scheme(C_used, C_rec)

where:
  ΔE_scheme = (1/n) Σ min_j ΔE(C_used_i, C_rec_j)

  C_used: 使用配色
  C_rec: 推薦配色
  n: 使用色数
```

### 5.4 使用色数順並び替え（used_color_count）

#### アルゴリズム

イラストレーターが頻繁に使用する色数の配色を上位に配置。

```python
# sort_color_scheme.py: Line 134-158
def sort_color_schemes_by_used_color_count(color_schemes, illustrator_name):
    # 統計データ取得
    chromatic_colors_count_distribution = _get_analysis_data(illustrator_name)[4]

    # 使用頻度順に色相数を並べ替え
    chromatic_colors_count_list_sorted = sorted(
        [i for i in range(len(chromatic_colors_count_distribution))],
        key=lambda i: chromatic_colors_count_distribution[i],
        reverse=True
    )

    new_color_schemes = []

    # よく使われた色相数の順で配色を追加
    for colors_count in chromatic_colors_count_list_sorted:
        for color_scheme in color_schemes:
            if len(color_scheme) == colors_count:
                new_color_schemes.append(color_scheme)

    return new_color_schemes
```

**数式表現**:
```
ソート順序: D[n_1] ≥ D[n_2] ≥ ... ≥ D[n_k]

where:
  D[n]: n色を使用したイラスト数
  n_i: 色数（1色, 2色, ...）

推薦配色の順位:
  rank(C_rec) = rank(|C_rec|)  (色数でグループ化)
```

**例**:
```
使用頻度: D[3] = 50, D[2] = 30, D[4] = 20, D[5] = 10

推薦順位:
1位グループ: 3色配色（トライアド、ドミナント、スプリット補色）
2位グループ: 2色配色（アナロジー、補色、対立色等）
3位グループ: 4色配色（テトラード）
4位グループ: 5色配色（ペンタード）
```

### 5.5 平均結果長順並び替え（mean_resultant_length）

#### アルゴリズム

イラストレーターが頻繁に使用する色相関係（色相差）を持つ配色を上位に配置。

```python
# sort_color_scheme.py: Line 69-100
def sort_color_schemes_by_mean_resultant_length(color_schemes, illustrator_name):
    new_color_schemes = []

    mean_resultant_length_distribution = get_statistics_by_illustrator(
        illustrator_name, "mean_resultant_length_distribution"
    )

    # 使用頻度降順にPCCS色相差をソート
    pccs_sorted_used_count = sorted(
        range(len(mean_resultant_length_distribution)),
        key=lambda i: mean_resultant_length_distribution[i],
        reverse=True
    )

    # 頻繁に使用される色相差を持つ配色を優先
    for pccs in pccs_sorted_used_count:
        for color_scheme in color_schemes:
            if _is_included_pccs_diff_in_color_scheme(color_scheme, pccs):
                new_color_schemes.append(color_scheme)
                color_schemes.remove(color_scheme)

    return new_color_schemes
```

**数式表現**:
```
平均結果長分布: MRL[R_i] = |{j | R_j ≈ R_i}|

where:
  R_i = i / DIV_NUMBER  (0.0 ~ 1.0, DIV_NUMBER=12)
  R_j: イラストjの平均結果長

ソート順序: MRL[R_1] ≥ MRL[R_2] ≥ ... ≥ MRL[R_k]

推薦配色の優先度:
  priority(C_rec) = MRL[R(C_rec)]

  R(C_rec): 推薦配色の平均結果長
```

**学術的意義**:

色相環（360度）上での色の集中度を平均結果長Rで数値化：
- R ≈ 1: 色が似た位置に集中（類似色の多用）
- R ≈ 0: 色が円全体に散らばる（多様な色相の使用）

イラストレーターが好む色相関係（類似色重視 or 対比色重視）を学習し、その傾向に合致する配色を優先推薦。

### 5.6 トーン使用頻度順並び替え（used_tone）

#### アルゴリズム

イラストレーターが頻繁に使用するトーン（明度彩度領域）を持つ配色を上位に配置。

```python
# sort_color_scheme.py: Line 227-311
def sort_color_schemes_by_used_tone(color_schemes, illustrator_name):
    # 統計データ取得
    saturation_lightness_count_distribution = _get_analysis_data(illustrator_name)[7]

    # 各配色のトーン使用頻度スコアを計算
    color_schemes_with_score = []

    for color_scheme in color_schemes:
        tone_score = _calc_color_scheme_tone_score(
            color_scheme, saturation_lightness_count_distribution
        )
        color_schemes_with_score.append((tone_score, color_scheme))

    # スコアの降順でソート
    color_schemes_with_score.sort(key=lambda x: x[0], reverse=True)

    # ソート済み配色リストを作成
    sorted_color_schemes = [color_scheme for _, color_scheme in color_schemes_with_score]

    return sorted_color_schemes


def _calc_color_scheme_tone_score(color_scheme, saturation_lightness_count_distribution):
    total_score = 0

    for hex_color in color_scheme:
        rgb_color = hex_to_rgb(hex_color)
        h, s, l = rgb_to_hsl(rgb_color)

        # HSL値をマトリックス座標に変換
        saturation_index = min(4, s // 20)  # 0-100を0-4にマッピング
        lightness_index = min(4, l // 20)

        # トーン使用頻度を取得
        if (lightness_index < len(saturation_lightness_count_distribution) and
            saturation_index < len(saturation_lightness_count_distribution[lightness_index])):
            tone_usage = saturation_lightness_count_distribution[lightness_index][saturation_index]
            total_score += tone_usage

    # 配色内の平均スコアを返す
    return total_score / len(color_scheme) if color_scheme else 0
```

**数式表現**:
```
座標変換:
  idx_S = ⌊S / 20⌋  (0 ≤ idx_S ≤ 4)
  idx_L = ⌊L / 20⌋  (0 ≤ idx_L ≤ 4)

トーンスコア:
  score(C_rec) = (1/|C_rec|) Σ M[idx_L(c_i)][idx_S(c_i)]

where:
  C_rec: 推薦配色
  c_i: 推薦配色内のi番目の色
  M: トーン分布マトリックス（正規化済み）
  |C_rec|: 推薦配色内の色数

ソート順序: score(C_1) ≥ score(C_2) ≥ ... ≥ score(C_k)
```

**学術的意義**:

明度彩度空間を5×5の25領域に分割し、各イラストレーターが好むトーン領域を特定。推薦配色の各色が頻繁に使用されるトーン領域に含まれるほど高スコアとなり、上位に配置される。

### 5.7 カスタム評価関数（custom_v0）

#### アルゴリズム

複数の評価指標を組み合わせたカスタムスコアリング。

```python
# sort_color_scheme.py: Line 190-225
def sort_color_schemes_by_custom_v0(used_color_scheme, rec_color_schemes, illustrator_name):
    rec_color_schemes_info = []

    # 推薦配色ごとにスコアを計算
    for rec_color_scheme in rec_color_schemes:
        score = _calc_rec_color_scheme_score(used_color_scheme, rec_color_scheme)

        rec_color_schemes_info.append({
            "rec_color_scheme": rec_color_scheme,
            "score": score
        })

    # スコアの降順でソート
    rec_color_schemes_info = sorted(rec_color_schemes_info, key=lambda x: x['score'], reverse=True)

    sorted_rec_color_schemes = []
    for rec_color_scheme_info in rec_color_schemes_info:
        sorted_rec_color_schemes.append(rec_color_scheme_info['rec_color_scheme'])

    return sorted_rec_color_schemes


def _calc_rec_color_scheme_score(used_color_scheme, rec_color_scheme):
    # 同じ色相かどうかでスコアを計算
    same_hue_score = calc_same_hue_score(used_color_scheme, rec_color_scheme)
    return same_hue_score
```

**数式表現**:
```
カスタムスコア: score(C_used, C_rec) = f(hue_match, tone_match, ...)

where:
  hue_match: 色相一致度
  tone_match: トーン一致度
  ...: 拡張可能な評価指標

現在実装（v0）: score = same_hue_score
```

### 5.8 並び替え統合フロー

```python
# color_recommendation.py: Line 26-49
def sort_recommend_color_schemes_rgb(recommend_color_schemes_rgb, used_color_scheme_rgb,
                                      sort_type, illustrator_name):
    # 推薦配色群の並び替え
    if sort_type == "color_diff":
        recommend_color_schemes_rgb = sort_color_schemes_by_color_difference(
            used_color_scheme_rgb, recommend_color_schemes_rgb
        )
    elif sort_type == "random":
        recommend_color_schemes_rgb = shuffle_color_schemes(recommend_color_schemes_rgb)
    elif sort_type == "used_color_count":
        recommend_color_schemes_rgb = sort_color_schemes_by_used_color_count(
            recommend_color_schemes_rgb, illustrator_name
        )
    elif sort_type == "mean_resultant_length":
        recommend_color_schemes_rgb = sort_color_schemes_by_mean_resultant_length(
            recommend_color_schemes_rgb, illustrator_name
        )
    elif sort_type == "custom_v0":
        recommend_color_schemes_rgb = sort_color_schemes_by_custom_v0(
            used_color_scheme_rgb, recommend_color_schemes_rgb, illustrator_name
        )
    elif sort_type == "used_tone":
        recommend_color_schemes_rgb = sort_color_schemes_by_used_tone(
            recommend_color_schemes_rgb, illustrator_name
        )
    elif sort_type == "no_sort":
        pass
    else:
        print("ソートの種類が間違っているため，推薦配色は並び替えられずに挿入されます．")

    return recommend_color_schemes_rgb
```

---

## 6. 評価方法

### 6.1 概要

推薦配色の有効性をRecall@kで評価する。ユーザーが次に選択した色が推薦配色の上位k個に含まれているかを判定。

**実装ファイル**: `check_data_is_contained_next_color.py`

### 6.2 評価対象

| 評価対象 | 判定基準 | 閾値 | 実装行 |
|---------|---------|-----|--------|
| 色（color） | ΔE（CIE2000） | 10 | 11-32 |
| 色相（hue） | 色相角度差 | 15° | 35-73 |
| トーン（tone） | 明度彩度ユークリッド距離 | 15 | 76-111 |

### 6.3 色（color）の判定

```python
# check_data_is_contained_next_color.py: Line 11-32
def is_contained_color(next_color, color_schemes):
    for i in range(len(color_schemes)):
        for j in range(len(color_schemes[i])):
            recommend_color = color_schemes[i][j]["color"]

            diff = calculate_color_difference_delta_e_cie2000(
                hex_to_rgb(next_color),
                hex_to_rgb(recommend_color)
            )

            if diff <= 10:
                return True, i + 1  # (含まれている, 配色番号)

    return False, -1
```

**数式表現**:
```
判定条件: ΔE(C_next, C_rec_ij) ≤ 10

where:
  C_next: 次に選択された色
  C_rec_ij: i番目の推薦配色のj番目の色
  ΔE: CIE2000色差

Recall@k: R@k = (1/N) Σ I(min_i≤k ΔE(C_next, C_rec_i) ≤ 10)
```

### 6.4 色相（hue）の判定

```python
# check_data_is_contained_next_color.py: Line 35-73
def is_contained_hue(next_color, color_schemes_data):
    for i in range(len(color_schemes_data)):
        for j in range(len(color_schemes_data[i])):
            recommend_color = color_schemes_data[i][j]["color"]

            next_color_rgb = hex_to_rgb(next_color)
            recommend_color_rgb = hex_to_rgb(recommend_color)
            next_color_hsl = rgb_to_hsl(next_color_rgb)
            recommend_color_hsl = rgb_to_hsl(recommend_color_rgb)

            hue_diff = calc_angle_diff(next_color_hsl[0], recommend_color_hsl[0])

            if hue_diff <= 15:
                return True, i + 1

    return False, -1
```

**数式表現**:
```
色相角度差: Δh = min(|h_1 - h_2|, 360 - |h_1 - h_2|)

判定条件: Δh(C_next, C_rec_ij) ≤ 15°

Recall@k: R@k = (1/N) Σ I(min_i≤k Δh(C_next, C_rec_i) ≤ 15°)
```

### 6.5 トーン（tone）の判定

```python
# check_data_is_contained_next_color.py: Line 76-111
def is_contained_next_tone(next_color, color_schemes):
    for i in range(len(color_schemes)):
        for j in range(len(color_schemes[i])):
            recommend_color = color_schemes[i][j]["color"]

            next_color_rgb = hex_to_rgb(next_color)
            recommend_color_rgb = hex_to_rgb(recommend_color)
            next_color_hsl = rgb_to_hsl(next_color_rgb)
            recommend_color_hsl = rgb_to_hsl(recommend_color_rgb)

            tone_diff = calc_distance_diff(
                next_color_hsl[1], next_color_hsl[2],
                recommend_color_hsl[1], recommend_color_hsl[2]
            )

            if tone_diff <= 15:
                return True, i + 1

    return False, -1
```

**数式表現**:
```
トーン距離: d_tone = √[(S_1 - S_2)² + (L_1 - L_2)²]

判定条件: d_tone(C_next, C_rec_ij) ≤ 15

where:
  S: 彩度（0-100）
  L: 明度（0-100）

Recall@k: R@k = (1/N) Σ I(min_i≤k d_tone(C_next, C_rec_i) ≤ 15)
```

### 6.6 Recall@k評価フロー

```python
# check_data_is_contained_next_color.py: Line 162-243
def check_data_is_contained_next(data, check_subject):
    data_recall_at_k = []

    for illust_data in data:
        if not illust_data:
            continue

        used_color_scheme_data = illust_data["color_scheme"]
        recommend_color_schemes = illust_data["recommend_color_schemes"]

        recall_at_k_per_illust = []

        # 2番目以降の使用色について判定
        for i in range(1, len(used_color_scheme_data)):
            next_color = used_color_scheme_data[i]["color"]

            # 判定
            if check_subject == "color":
                is_contained, scheme_index = is_contained_color(next_color, recommend_color_schemes)
            elif check_subject == "hue":
                is_contained, scheme_index = is_contained_hue(next_color, recommend_color_schemes)
            elif check_subject == "tone":
                is_contained, scheme_index = is_contained_next_tone(next_color, recommend_color_schemes)

            # recall@kのデータの作成
            is_contained_data = {
                "next_color_index": i + 1,
                "k": scheme_index,  # 何番目の推薦配色に含まれていたか（-1: 含まれていない）
                "is_contained_next_color": is_contained
            }
            recall_at_k_per_illust.append(is_contained_data)

        data_recall_at_k_per_illust = {
            "illust_name": illust_data["illust_name"],
            "recommendations_count": len(recommend_color_schemes),
            "recall_at_k": recall_at_k_per_illust,
        }
        data_recall_at_k.append(data_recall_at_k_per_illust)

    return data_recall_at_k
```

### 6.7 Recall@k計算式

**定義**:
```
Recall@k = (上位k個の推薦配色に次の色が含まれていた回数) / (次の色の総数)

数式表現:
R@k = (1/N_total) Σ I(k_i ≤ k ∧ k_i ≠ -1)

where:
  N_total: 全イラストの次の色の総数
  k_i: i番目の次の色が含まれていた推薦配色の順位（-1: 含まれていない）
  I(): 指示関数（条件が真なら1、偽なら0）
```

**評価メトリクス**:
- Recall@1: 最上位の推薦配色に含まれていた割合
- Recall@5: 上位5個の推薦配色に含まれていた割合
- Recall@10: 上位10個の推薦配色に含まれていた割合
- Recall@k (k=1,2,...,N): 各kにおけるRecall値

### 6.8 出力データ形式

```json
{
  "illust_name": "path/to/image.jpg",
  "recommendations_count": 17,
  "recall_at_k": [
    {
      "next_color_index": 2,
      "k": 3,
      "is_contained_next_color": true
    },
    {
      "next_color_index": 3,
      "k": -1,
      "is_contained_next_color": false
    }
  ]
}
```

---

## 7. システムフローチャート

### 7.1 全体フロー

```
┌─────────────────────────────────────────────────────────────┐
│                    色推薦システム全体フロー                      │
└─────────────────────────────────────────────────────────────┘

[1. データ収集]
    ↓
┌───────────────────┐
│ イラスト画像       │
│ (Instagram等)     │
└───────────────────┘
    ↓
[2. 色抽出] (estimate_used_color_scheme.py)
    ↓
┌───────────────────┐
│ ColorThief抽出     │ ← quality=10, color_count=30
│ (30色抽出)        │
└───────────────────┘
    ↓
┌───────────────────┐
│ 類似色統合         │ ← ΔE閾値=10
│ (ΔE≤10で統合)     │
└───────────────────┘
    ↓
┌───────────────────┐
│ ピクセル再分類     │ ← ユークリッド距離<0.1
│ (使用率計算)      │
└───────────────────┘
    ↓
┌───────────────────┐
│ 有彩色フィルタ     │ ← S>10%, 10%<L<90%
└───────────────────┘
    ↓
┌───────────────────┐
│ 最終統合          │ ← ΔE閾値=5
│ (ΔE≤5で統合)      │
└───────────────────┘
    ↓
┌───────────────────┐
│ 使用率降順ソート   │
│ used_colors.json  │
└───────────────────┘
    ↓
[3. 統計分析] (analyze_illustrator_statistics.py)
    ↓
┌───────────────────────────────────────┐
│ イラストレーター別統計データ生成       │
│ - 色数分布                            │
│ - 色相使用頻度（PCCS 24色相）         │
│ - 平均結果長分布                      │
│ - 明度彩度分布（5×5マトリックス）     │
└───────────────────────────────────────┘
    ↓
┌───────────────────┐
│ statistics_for_   │
│ illustrators.json │
└───────────────────┘
    ↓
[4. 推薦配色生成] (color_recommendation.py, generate_color_scheme_method.py)
    ↓
┌─────────────────────────────────────┐
│ ベースカラー決定                      │ ← 使用率最高の有彩色
└─────────────────────────────────────┘
    ↓
    ├─────────────────────────────────┐
    │                                 │
[色相推薦]                         [トーン推薦]
    │                                 │
┌───────────────────┐         ┌───────────────────┐
│ 17種配色技法適用   │         │ 単色ベース生成     │
│ - アナロジー       │         └───────────────────┘
│ - トライアド       │                 ↓
│ - テトラード       │         ┌───────────────────┐
│ - etc.            │         │ 明度彩度変化適用   │
│ (17配色)          │         │ diff_values:      │
└───────────────────┘         │ [-40,-20,0,+20,+40]│
    │                         │ (5×5=25配色)      │
    │                         └───────────────────┘
    │                                 │
    └─────────┬───────────────────────┘
              ↓
      [色推薦（統合）]
              ↓
      ┌───────────────────┐
      │ 17配色 × 25バリエーション │
      │ = 425配色（理論値）        │
      └───────────────────┘
              ↓
      ┌───────────────────┐
      │ 無効配色除去              │
      │ - 無彩色除去              │
      │ - 空配色除去              │
      └───────────────────┘
              ↓
[5. 推薦順序計算] (sort_color_scheme.py)
              ↓
      ┌───────────────────────────────┐
      │ 並び替え方式選択               │
      ├───────────────────────────────┤
      │ □ random          (ランダム)   │
      │ □ color_diff      (色差順)     │
      │ □ used_color_count (色数順)    │
      │ □ mean_resultant_length        │
      │                   (平均結果長順) │
      │ □ used_tone       (トーン順)   │
      │ □ custom_v0       (カスタム)   │
      └───────────────────────────────┘
              ↓
      ┌───────────────────┐
      │ ソート済み推薦配色 │
      │ recommend_*.json  │
      └───────────────────┘
              ↓
[6. 評価] (check_data_is_contained_next_color.py)
              ↓
      ┌───────────────────────────────┐
      │ 次に選択された色との照合       │
      ├───────────────────────────────┤
      │ 色（color）    : ΔE≤10         │
      │ 色相（hue）    : 角度差≤15°    │
      │ トーン（tone）  : 距離≤15      │
      └───────────────────────────────┘
              ↓
      ┌───────────────────┐
      │ Recall@k計算      │
      │ - Recall@1        │
      │ - Recall@5        │
      │ - Recall@10       │
      │ - etc.            │
      └───────────────────┘
              ↓
      ┌───────────────────┐
      │ 評価結果出力       │
      │ is_contained_     │
      │ next_*.json       │
      └───────────────────┘
```

### 7.2 色抽出詳細フロー

```
[色抽出処理の詳細]

入力画像 (W×H pixels)
    ↓
ColorThief.get_palette(color_count=30, quality=10)
    ↓
抽出パレット: P = [C_1, C_2, ..., C_30]
    ↓
┌────────────────────────────────────┐
│ 類似色統合（ΔE閾値=10）            │
│                                    │
│ while |P| > 0:                     │
│   base = P[0]                      │
│   similar = {c ∈ P | ΔE(base,c)≤10}│
│   merged = average(similar)        │
│   P_merged.append(merged)          │
│   P = P \ similar                  │
└────────────────────────────────────┘
    ↓
統合パレット: P_merged = [M_1, M_2, ..., M_m] (m ≤ 30)
    ↓
┌────────────────────────────────────┐
│ ピクセル分類（全W×H pixels）       │
│                                    │
│ for each pixel p:                  │
│   find M_i where d_euclidean(p, M_i) < 0.1│
│   count[M_i] += 1                  │
└────────────────────────────────────┘
    ↓
使用率計算: rate[M_i] = count[M_i] / Σcount[M_j]
    ↓
┌────────────────────────────────────┐
│ 有彩色フィルタリング                │
│                                    │
│ for each M_i:                      │
│   HSL = rgb_to_hsl(M_i)            │
│   if S > 10% AND 10% < L < 90%:    │
│     keep M_i                        │
└────────────────────────────────────┘
    ↓
┌────────────────────────────────────┐
│ 最終統合（ΔE閾値=5）               │
│                                    │
│ 類似色統合処理（閾値=5で再実行）    │
└────────────────────────────────────┘
    ↓
使用率降順ソート
    ↓
出力: used_colors.json
[
  {"color": "#efeae3", "rate": 0.237894, ...},
  {"color": "#c9b8a8", "rate": 0.158342, ...},
  ...
]
```

### 7.3 推薦配色生成詳細フロー

```
[推薦配色生成の詳細]

ベースカラー: C_base (使用率最高の有彩色)
    ↓
┌──────────────────────────────────────┐
│ 色相推薦（17種配色技法）              │
├──────────────────────────────────────┤
│ ■ 1色配色                            │
│   - Identity (同一色)                │
│                                      │
│ ■ 2色配色                            │
│   - Analogy (+30°, -30°) → 2配色    │
│   - Intermediate (±90°) → 2配色      │
│   - Dyad (補色, 180°) → 1配色        │
│   - Oponent (±150°) → 2配色          │
│                                      │
│ ■ 3色配色                            │
│   - Dominant (3パターン) → 3配色     │
│   - Split Complementary (3パターン)  │
│     → 3配色                          │
│   - Triad (120°間隔) → 1配色         │
│                                      │
│ ■ 4色配色                            │
│   - Tetrad (90°間隔) → 1配色         │
│                                      │
│ ■ 5色配色                            │
│   - Pentad (72°間隔) → 1配色         │
│                                      │
│ ■ 6色配色                            │
│   - Hexad (60°間隔) → 1配色          │
│                                      │
│ 合計: 17配色                          │
└──────────────────────────────────────┘
    ↓
色相推薦配色群: CS_hue = [CS_1, CS_2, ..., CS_17]
    ↓
    ├───────────────────────────────────┐
    │                                   │
[色相推薦のみ]                      [トーン/色推薦]
    │                                   │
    │                           ┌───────────────────┐
    │                           │ バリエーション生成 │
    │                           └───────────────────┘
    │                                   ↓
    │                           diff_values = [-40, -20, 0, +20, +40]
    │                                   ↓
    │                           ┌───────────────────────────────┐
    │                           │ for ΔL in diff_values:        │
    │                           │   for ΔS in diff_values:      │
    │                           │     for CS_i in CS_hue:       │
    │                           │       CS'_ij = add_variation( │
    │                           │         CS_i, ΔL, ΔS          │
    │                           │       )                       │
    │                           │       CS_all.append(CS'_ij)   │
    │                           └───────────────────────────────┘
    │                                   ↓
    │                           CS_all: 17 × 25 = 425配色（理論値）
    │                                   ↓
    │                           ┌───────────────────┐
    │                           │ 無効配色除去       │
    │                           │ - RGB範囲外除去    │
    │                           │ - 無彩色除去       │
    │                           │ - 空配色除去       │
    │                           └───────────────────┘
    │                                   ↓
    └───────────┬───────────────────────┘
                ↓
        推薦配色群: CS_recommend
                ↓
        ┌───────────────────┐
        │ 並び替え処理       │
        │ (sort_type指定)   │
        └───────────────────┘
                ↓
        ソート済み推薦配色群
```

### 7.4 並び替え処理詳細フロー

```
[並び替え処理の詳細]

推薦配色群: CS_recommend = [CS_1, CS_2, ..., CS_N]
統計データ: statistics_for_illustrators.json
    ↓
sort_type選択
    ↓
    ├─→ [random]
    │       ↓
    │   ランダムシャッフル
    │
    ├─→ [color_diff]
    │       ↓
    │   各配色について色差計算:
    │   score[CS_i] = ΔE_scheme(C_used, CS_i)
    │       ↓
    │   昇順ソート（類似順）
    │
    ├─→ [used_color_count]
    │       ↓
    │   統計データから色数分布取得:
    │   D = [D[0], D[1], ..., D[19]]
    │       ↓
    │   使用頻度降順で色数順序作成:
    │   order = sorted([0,1,...,19], key=D, reverse=True)
    │       ↓
    │   色数順でグループ化して並べ替え:
    │   for n in order:
    │     append {CS_i | |CS_i| = n}
    │
    ├─→ [mean_resultant_length]
    │       ↓
    │   統計データから平均結果長分布取得:
    │   MRL_dist = [MRL[0], ..., MRL[12]]
    │       ↓
    │   使用頻度降順でPCCS色相差順序作成:
    │   pccs_order = sorted([0,...,12], key=MRL_dist, reverse=True)
    │       ↓
    │   色相差順で並べ替え:
    │   for pccs in pccs_order:
    │     append {CS_i | pccs ∈ CS_i}
    │
    ├─→ [used_tone]
    │       ↓
    │   統計データからトーン分布取得:
    │   M = saturation_lightness_count_distribution (5×5)
    │       ↓
    │   各配色のトーンスコア計算:
    │   for CS_i:
    │     score[CS_i] = (1/|CS_i|) Σ M[idx_L(c)][idx_S(c)]
    │       ↓
    │   スコア降順ソート
    │
    └─→ [custom_v0]
            ↓
        カスタム評価関数:
        for CS_i:
          score[CS_i] = f(C_used, CS_i)
            ↓
        スコア降順ソート
    ↓
ソート済み推薦配色群: CS_sorted
    ↓
JSON形式で保存:
recommend_hues/sort_by_{sort_type}/recommend_hues_{illustrator}.json
recommend_tones/{diff_values}/sort_by_{sort_type}/recommend_tones_{illustrator}.json
recommend_colors/sort_by_{sort_type}/recommend_colors_{illustrator}.json
```

### 7.5 評価処理詳細フロー

```
[Recall@k評価の詳細]

入力データ:
- 推薦配色: recommend_*.json
- 使用配色: used_colors.json (時系列順)
    ↓
┌────────────────────────────────────┐
│ イラストごとの評価                  │
└────────────────────────────────────┘
    ↓
for each illustration:
    ↓
  使用配色: C_used = [C_1, C_2, ..., C_m]
  推薦配色: CS_rec = [CS_1, CS_2, ..., CS_N]
    ↓
  for i = 2 to m:  # 2番目以降の色について
      ↓
    next_color = C_used[i]
      ↓
    ┌────────────────────────────────┐
    │ 推薦配色群との照合              │
    └────────────────────────────────┘
      ↓
    for k = 1 to N:
        ↓
      CS_k = k番目の推薦配色
        ↓
      for c in CS_k:
          ↓
        ┌─ check_subject = "color" ─┐
        │   判定: ΔE(next_color, c) ≤ 10 │
        ├─ check_subject = "hue" ─┐
        │   判定: Δh(next_color, c) ≤ 15° │
        └─ check_subject = "tone" ─┘
            判定: d_tone(next_color, c) ≤ 15
          ↓
        if 判定がTrue:
            ↓
          record: k番目の推薦配色に含まれていた
          break  # このイラスト・この次色の判定終了
      ↓
    if 全推薦配色で見つからない:
        ↓
      record: k = -1 (含まれていない)
    ↓
  結果保存:
  {
    "next_color_index": i,
    "k": k,  # 何番目の推薦配色に含まれていたか
    "is_contained_next_color": (k != -1)
  }
    ↓
全イラストの評価結果を集計
    ↓
┌────────────────────────────────────┐
│ Recall@k計算                       │
└────────────────────────────────────┘
    ↓
for k = 1, 2, 3, ..., N:
    ↓
  count = 0
  total = 0
    ↓
  for each 次色の評価結果:
      ↓
    total += 1
      ↓
    if (記録されたk値 ≤ k) AND (k値 != -1):
        ↓
      count += 1
    ↓
  Recall@k = count / total
    ↓
出力: is_contained_next_{check_subject}/{sort_type}/is_contained_next_{check_subject}_{illustrator}.json
    ↓
グラフ化: plot_graph.py
- Recall@kグラフ（k vs Recall値）
- エラーバー付きグラフ
- バイオリンプロット等
```

---

## 8. 論文用まとめ

### 8.1 システムの新規性

1. **17種配色技法の組織的適用**: 従来研究では個別技法のみの適用が多いが、本システムは複数技法を統合的に適用
2. **統計ベース個人化並び替え**: イラストレーター個人の色彩傾向を反映した推薦順位付け
3. **3段階色抽出プロセス**: ColorThief + ΔE統合 + 有彩色フィルタの組み合わせ
4. **トーン推薦のバリエーション生成**: 色相推薦に加え、明度彩度の組織的変化による推薦
5. **多面的評価指標**: 色・色相・トーンの3側面からの推薦性能評価

### 8.2 主要アルゴリズムの数式まとめ

**色抽出**:
```
1. ColorThief抽出: P = Extract(I, n=30, q=10)
2. 類似色統合: ΔE(C_i, C_j) ≤ τ → C_merged = (1/n)ΣC_k
3. ピクセル分類: d_euclidean(C_pixel, C_palette) < 0.1
4. 使用率計算: rate_i = count_i / Σcount_j
5. 有彩色判定: S > 10% ∧ 10% < L < 90%
```

**統計分析**:
```
1. 平均有彩色数: μ_chroma = (1/N)Σn_chroma_i
2. 色数分布: D[k] = |{i | n_chroma_i = k}|
3. 平均結果長: R = √[(1/n Σcos(θ_i))² + (1/n Σsin(θ_i))²]
4. トーン分布: M[idx_L][idx_S] = Σrate_k (正規化済み)
```

**推薦生成**:
```
1. 色相推薦: C_i = (H_base + Δh_i mod 360, S_base, L_base)
2. トーン推薦: C'_ij = (H_base, S_base + ΔS_i, L_base + ΔL_j)
3. 配色数: N_hue = 17, N_tone = 25, N_color ≈ 425
```

**並び替え**:
```
1. 色差順: score = (1/n)Σmin_j ΔE(C_used_i, C_rec_j)
2. 色数順: rank = rank_by_frequency(|CS_rec|)
3. 平均結果長順: priority = MRL_dist[R(CS_rec)]
4. トーン順: score = (1/|CS|)ΣM[idx_L(c)][idx_S(c)]
```

**評価**:
```
1. 色判定: ΔE(C_next, C_rec) ≤ 10
2. 色相判定: Δh(C_next, C_rec) ≤ 15°
3. トーン判定: d_tone(C_next, C_rec) ≤ 15
4. Recall@k: R@k = (1/N)ΣI(k_i ≤ k ∧ k_i ≠ -1)
```

### 8.3 実装詳細の定量的パラメータ

| パラメータ | 値 | 根拠 |
|-----------|---|------|
| ColorThief品質 | 10 | 処理速度と精度のバランス |
| ColorThief色数 | 30 | 詳細な色抽出と処理効率 |
| ΔE統合閾値（パレット） | 10 | 視覚的に識別困難な色差 |
| ΔE統合閾値（最終） | 5 | より厳密な類似色統合 |
| ユークリッド距離閾値 | 0.1 | 正規化RGB空間での近接性 |
| 彩度下限 | 10% | 有彩色と無彩色の境界 |
| 明度範囲 | 10-90% | 極端な明度の除外 |
| 配色技法数 | 17 | 主要な調和配色技法を網羅 |
| トーンバリエーション | 5×5=25 | 明度彩度の5段階変化 |
| トーンマトリックス分割 | 5×5 | 明度彩度空間の実用的分割 |
| 色判定閾値（ΔE） | 10 | 視覚的類似性の許容範囲 |
| 色相判定閾値 | 15° | PCCS色相の約半分（30°/2） |
| トーン判定閾値 | 15 | 明度彩度空間での許容距離 |

---

## 付録A: ファイルパス一覧

### 入力データ
- 使用色データ: `data/input/used_colors/{illustrator_name}.json`
- 使用色相データ: `data/input/used_hues/{illustrator_name}.json`
- 統計データ: `data/input/statistics_for_illustrators.json`
- イラスト画像: `data/input/illustration/{illustrator_name}/`

### 出力データ
- 推薦色相: `data/output/recommend_hues/sort_by_{sort_type}/recommend_hues_{illustrator_name}.json`
- 推薦トーン: `data/output/recommend_tones/{diff_values}/sort_by_{sort_type}/recommend_tones_{illustrator_name}.json`
- 推薦色: `data/output/recommend_colors/sort_by_{sort_type}/recommend_colors_{illustrator_name}.json`
- 評価結果: `data/output/is_contained_next_{check_subject}/{sort_type}/is_contained_next_{check_subject}_{illustrator_name}.json`

### ソースコード
- 定数定義: `utils/config/constants_dev.py`
- 色抽出: `utils/estimate_used_color_scheme.py`
- 統計分析: `utils/analyze_illustrator_statistics.py`
- 推薦メイン: `color_recommendation.py`
- 配色生成: `utils/generate_color_scheme_method.py`
- バリエーション: `utils/add_variations_color_scheme.py`
- 並び替え: `utils/sort_color_scheme.py`
- 評価: `utils/check_data_is_contained_next_color.py`

---

## 付録B: 主要関数リファレンス

### 色抽出関係
- `estimate_used_color_scheme_re(image_path)`: 画像から使用色抽出（推奨版）
- `estimate_used_colors_by_colorthief(image_path, color_count)`: ColorThief抽出
- `merge_same_color_palette(palette, threshold)`: パレット統合
- `merge_similar_color(color_scheme, threshold)`: 類似色統合
- `color_count_by_color_palette(color_palette, image_path)`: 使用率計算

### 統計分析関係
- `_extract_statistics_by_illustrator(illustrator_name)`: 統計データ抽出
- `get_statistics_by_illustrator(illustrator_name, keyword)`: 統計データ取得
- `save_statistics_for_illustrators(illustrator_list)`: 統計データ保存
- `_get_saturation_lightness_count_distribution(...)`: トーン分布計算
- `_mean_resultant_length(angles_deg)`: 平均結果長計算

### 推薦生成関係
- `get_recommendations(...)`: 推薦配色統一インターフェース
- `generate_recommend_hues_by_illustrator(...)`: 色相推薦生成
- `generate_recommend_tones_by_illustrator(...)`: トーン推薦生成
- `generate_recommend_colors_by_illustrator(...)`: 色推薦生成
- `generate_all_color_schemes(base_color_rgb)`: 17種配色技法適用
- `get_variations_for_color_schemes(...)`: バリエーション生成

### 並び替え関係
- `sort_recommend_color_schemes_rgb(...)`: 並び替え統一インターフェース
- `sort_color_schemes_by_color_difference(...)`: 色差順並び替え
- `sort_color_schemes_by_used_color_count(...)`: 色数順並び替え
- `sort_color_schemes_by_mean_resultant_length(...)`: 平均結果長順並び替え
- `sort_color_schemes_by_used_tone(...)`: トーン順並び替え
- `shuffle_color_schemes(color_schemes)`: ランダムシャッフル

### 評価関係
- `check_data_is_contained_next(data, check_subject)`: 次色含有判定
- `is_contained_color(next_color, color_schemes)`: 色判定（ΔE≤10）
- `is_contained_hue(next_color, color_schemes)`: 色相判定（角度差≤15°）
- `is_contained_next_tone(next_color, color_schemes)`: トーン判定（距離≤15）

---

**ドキュメント作成日**: 2026-01-09
**対象バージョン**: 最新版（feature/experiment-analysis-enhancements ブランチ）
**作成者**: AI Assistant（Claude Sonnet 4.5）
