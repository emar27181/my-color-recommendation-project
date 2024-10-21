import json
import matplotlib.pyplot as plt


def plot_recall_at_k(input_file_path, output_file_path):
    recalls = [0] * 100
    timing_count = 0

    with open(input_file_path, 'r') as f:
        data = json.load(f)

    print(f"{input_file_path} が読み込まれました．")

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

    # print(timing_count)
    # print(recalls)

    # プロット
    plt.plot(recalls, marker='o')
    plt.title('Recalls Plot')
    plt.ylim(0, 1)
    plt.xlim(0, 60)
    plt.xlabel('Index')
    plt.ylabel('Recall Values')
    plt.grid(True)

    # ファイルに保存
    plt.savefig(output_file_path)
    print(f"{output_file_path} が保存されました．")


def main():
    plot_recall_at_k("src/color_recommendation/data/output/test_is_contained_next_color_simple_data.json", 'src/color_recommendation/data/output/test_recall_at_k.png')


if __name__ == '__main__':
    main()
