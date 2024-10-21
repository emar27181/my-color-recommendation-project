import json
import matplotlib.pyplot as plt


def plot_graph(plot_data, graph_name, output_file_path):
    # プロット
    plt.plot(plot_data, label=f'{graph_name}', marker='o')
    plt.title(f'{graph_name}')
    plt.ylim(0, 1)
    plt.xlim(0, 60)
    plt.xlabel('color_scheme')
    plt.ylabel(f'{graph_name}')
    plt.grid(True)

    # ファイルに保存
    plt.savefig(output_file_path)


def calculate_recall(file_path):

    recalls = [0] * 100
    timing_count = 0

    with open(file_path, 'r') as f:
        data = json.load(f)

    # print(len(data))

    for illust_data in data:
        # print(illust_data['recall_at_k'])

        for illust_data_at_timing in illust_data['recall_at_k']:
            timing_count += 1
            # print(illust_data_at_timing)
            if (illust_data_at_timing['is_contained_next_color']):
                # print(illust_data_at_timing["k"])
                for i in range(illust_data_at_timing["k"], len(recalls)):
                    recalls[i] += 1

    for i in range(len(recalls)):
        # print(recalls[i])
        recalls[i] = round(100 * (recalls[i] / timing_count)) / 100

    return recalls


def plot_recall_at_k(input_file_path, output_file_path):

    recalls = calculate_recall(input_file_path)
    plot_graph(recalls, 'recall', output_file_path)
    # print(timing_count)
    # print(recalls)


def main():
    plot_recall_at_k("src/color_recommendation/data/output/test_is_contained_next_color_simple_data.json", 'src/color_recommendation/data/output/test_recall_at_k.png')


if __name__ == '__main__':
    main()
