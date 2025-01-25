import json


def convert_color_schemes_to_color_data(color_schemes):
    output_color_data = []

    for color_scheme in color_schemes:
        # print(color_scheme)
        new_color_scheme = []

        for color in color_scheme:
            new_color_data = {
                "color": color,
                "rate": -1
            }
            # print(new_color_data)
            new_color_scheme.append(new_color_data)
            # print(color_scheme_methods)

        output_color_data.append(new_color_scheme)

    # print(output_color_data)

    return (output_color_data)


def get_json_length(file_path):
    with open(file_path, 'r') as json_file:
        json_data = json.load(json_file)

    return (len(json_data))
