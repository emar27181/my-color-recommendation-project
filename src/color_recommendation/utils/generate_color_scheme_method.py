from transform_color import rgb_to_hsl, hsl_to_rgb, rgb_to_hex, hex_to_rgb


def generate_color_scheme(base_color_rgb, hue_differences):
    base_color_hsl = (rgb_to_hsl(base_color_rgb))
    base_color_hue = base_color_hsl[0]
    base_color_saturation = base_color_hsl[1]
    base_color_lightness = base_color_hsl[2]

    color_scheme = []
    color_scheme.append(base_color_rgb)

    for hue_difference in hue_differences:
        color_scheme.append(hsl_to_rgb((base_color_hue + hue_difference) % 360, base_color_saturation, base_color_lightness))
    return color_scheme


def generate_dominant_color_scheme(base_color_rgb):
    color_scheme = generate_color_scheme(base_color_rgb, [30, 60])
    return color_scheme


def main():
    print(generate_dominant_color_scheme([255, 0, 0]))
    print(generate_dominant_color_scheme([0, 255, 0]))
    print(generate_dominant_color_scheme([0, 0, 0]))

    print(-50 % 360)
    print(50 % 360)
    print((0 - 60) % 360)


if __name__ == '__main__':
    main()
