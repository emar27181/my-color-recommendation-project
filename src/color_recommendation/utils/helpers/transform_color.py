import numpy as np


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])


def rgb_to_hsl(rgb):
    r = rgb[0] / 255.0
    g = rgb[1] / 255.0
    b = rgb[2] / 255.0

    max_val = max(r, g, b)
    min_val = min(r, g, b)
    l = (max_val + min_val) / 2

    if max_val == min_val:
        h = s = 0  # achromatic
    else:
        d = max_val - min_val
        s = d / (2.0 - max_val - min_val) if l > 0.5 else d / (max_val + min_val)

        if max_val == r:
            h = (g - b) / d + (6 if g < b else 0)
        elif max_val == g:
            h = (b - r) / d + 2
        else:
            h = (r - g) / d + 4
        h /= 6

    return int(h * 360), int(s * 100), int(l * 100)


def hsl_to_rgb(h, s, l):
    s /= 100
    l /= 100

    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = l - c / 2

    if 0 <= h < 60:
        r, g, b = c, x, 0
    elif 60 <= h < 120:
        r, g, b = x, c, 0
    elif 120 <= h < 180:
        r, g, b = 0, c, x
    elif 180 <= h < 240:
        r, g, b = 0, x, c
    elif 240 <= h < 300:
        r, g, b = x, 0, c
    elif 300 <= h < 360:
        r, g, b = c, 0, x
    else:
        r, g, b = 0, 0, 0

    r = (r + m) * 255
    g = (g + m) * 255
    b = (b + m) * 255

    return [int(r), int(g), int(b)]


def transform_color_scheme_rgb_to_hex(color_scheme_rgb):
    color_scheme_hex = []
    # print(color_scheme_rgb)

    for color_rgb in color_scheme_rgb:
        color_scheme_hex.append(rgb_to_hex(color_rgb))
    return color_scheme_hex


def transform_color_schemes_rgb_to_hex(color_schemes_method_rgb):
    color_schemes_hex = []
    for color_scheme_method_rgb in color_schemes_method_rgb:
        for color_scheme_rgb in color_scheme_method_rgb:
            # print("color_scheme_rgb: ", color_scheme_rgb)
            color_schemes_hex.append(transform_color_scheme_rgb_to_hex(color_scheme_rgb))
    return color_schemes_hex


def main():
    """
      print(rgb_to_hex((255, 0, 0)))
      print(hex_to_rgb("#FF0000"))
      print(rgb_to_hsl((255, 0, 0)))
      print(hsl_to_rgb(0, 100, 50))
      """


if __name__ == "__main__":
    main()
