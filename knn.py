import cupy as cp
import os

# 1️⃣ 确定当前脚本目录
current_dir = "/data/user_jialinhan/"
# file_dir = "Transnet-fine/fine-1"
file_dir = "/data/user_jialinhan/0kechegnxuexi/baseline/SEAnet-main-yuanban-F5/conf/pca20w/"

# 2️⃣ 数据集名称列表，将不同k值对应的对比文件信息合并
# datasets_combined = [
#     {"name": "astro", "compare_file": "data_big/原版knn/原版-astro-results-1.txt", "k": 1},
#     {"name": "deep1b", "compare_file": "data_big/原版knn/原版-deep1b-results-1.txt", "k": 1},
#     {"name": "F5", "compare_file": "data_big/原版knn/原版-F5-results-1.txt", "k": 1},
#     # {"name": "F10", "compare_file": "data_big/原版knn/原版-F10-results-1.txt", "k": 1},
#     {"name": "origin", "compare_file": "data_big/原版knn/原版-origin-results-1.txt", "k": 1},
#     {"name": "sald", "compare_file": "data_big/原版knn/原版-sald-results-1.txt", "k": 1},
#     {"name": "seismic", "compare_file": "data_big/原版knn/原版-seismic-results-1.txt", "k": 1},
#     {"name": "astro", "compare_file": "data_big/原版knn/原版-astro-results-10.txt", "k": 10},
#     {"name": "deep1b", "compare_file": "data_big/原版knn/原版-deep1b-results-10.txt", "k": 10},
#     {"name": "F5", "compare_file": "data_big/原版knn/原版-F5-results-10.txt", "k": 10},
#     # {"name": "F10", "compare_file": "data_big/原版knn/原版-F10-results-10.txt", "k": 10},
#     {"name": "origin", "compare_file": "data_big/原版knn/原版-origin-results-10.txt", "k": 10},
#     {"name": "sald", "compare_file": "data_big/原版knn/原版-sald-results-10.txt", "k": 10},
#     {"name": "seismic", "compare_file": "data_big/原版knn/原版-seismic-results-10.txt", "k": 10},
#     {"name": "astro", "compare_file": "data_big/原版knn/原版-astro-results-100.txt", "k": 100},
#     {"name": "deep1b", "compare_file": "data_big/原版knn/原版-deep1b-results-100.txt", "k": 100},
#     {"name": "F5", "compare_file": "data_big/原版knn/原版-F5-results-100.txt", "k": 100},
#     # {"name": "F10", "compare_file": "data_big/原版knn/原版-F10-results-100.txt", "k": 100},
#     {"name": "origin", "compare_file": "data_big/原版knn/原版-origin-results-100.txt", "k": 100},
#     {"name": "sald", "compare_file": "data_big/原版knn/原版-sald-results-100.txt", "k": 100},
#     {"name": "seismic", "compare_file": "data_big/原版knn/原版-seismic-results-100.txt", "k": 100},
#     {"name": "astro", "compare_file": "data_big/原版knn/原版-astro-results-1000.txt", "k": 1000},
#     {"name": "deep1b", "compare_file": "data_big/原版knn/原版-deep1b-results-1000.txt", "k": 1000},
#     {"name": "F5", "compare_file": "data_big/原版knn/原版-F5-results-1000.txt", "k": 1000},
#     # {"name": "F10", "compare_file": "data_big/原版knn/原版-F10-results-1000.txt", "k": 1000},
#     {"name": "origin", "compare_file": "data_big/原版knn/原版-origin-results-1000.txt", "k": 1000},
#     {"name": "sald", "compare_file": "data_big/原版knn/原版-sald-results-1000.txt", "k": 1000},
#     {"name": "seismic", "compare_file": "data_big/原版knn/原版-seismic-results-1000.txt", "k": 1000},
# ]

datasets_combined = [
    {"name": "astro", "compare_file": "data_big/原版knn/原版-astro-results-1.txt", "k": 1},
    {"name": "astro", "compare_file": "data_big/原版knn/原版-astro-results-10.txt", "k": 10},
    {"name": "astro", "compare_file": "data_big/原版knn/原版-astro-results-100.txt", "k": 100},
    {"name": "astro", "compare_file": "data_big/原版knn/原版-astro-results-1000.txt", "k": 1000},
]

# datasets_combined = [
#     {"name": "deep1b", "compare_file": "data_big/原版knn/原版-deep1b-results-1.txt", "k": 1},
#     {"name": "deep1b", "compare_file": "data_big/原版knn/原版-deep1b-results-10.txt", "k": 10},
#     {"name": "deep1b", "compare_file": "data_big/原版knn/原版-deep1b-results-100.txt", "k": 100},
#     {"name": "deep1b", "compare_file": "data_big/原版knn/原版-deep1b-results-1000.txt", "k": 1000},
# ]


# # 2️⃣ 数据集名称列表，将不同k值对应的对比文件信息合并
# datasets_combined = [
#     {"name": "seismic", "compare_file": "data_big/原版knn/原版-seismic-results-1.txt", "k": 1},
#     {"name": "seismic", "compare_file": "data_big/原版knn/原版-seismic-results-10.txt", "k": 10},
#     {"name": "seismic", "compare_file": "data_big/原版knn/原版-seismic-results-100.txt", "k": 100},
#     {"name": "seismic", "compare_file": "data_big/原版knn/原版-seismic-results-1000.txt", "k": 1000},
# ]

# datasets_combined = [
#     {"name": "F10", "compare_file": "data_big/原版knn/原版-F10-results-1.txt", "k": 1},
#     {"name": "sald", "compare_file": "data_big/原版knn/原版-sald-results-1.txt", "k": 1},
#     {"name": "seismic", "compare_file": "data_big/原版knn/原版-seismic-results-1.txt", "k": 1},
#     {"name": "F10", "compare_file": "data_big/原版knn/原版-F10-results-10.txt", "k": 10},
#     {"name": "sald", "compare_file": "data_big/原版knn/原版-sald-results-10.txt", "k": 10},
#     {"name": "seismic", "compare_file": "data_big/原版knn/原版-seismic-results-10.txt", "k": 10},
#     {"name": "F10", "compare_file": "data_big/原版knn/原版-F10-results-100.txt", "k": 100},
#     {"name": "sald", "compare_file": "data_big/原版knn/原版-sald-results-100.txt", "k": 100},
#     {"name": "seismic", "compare_file": "data_big/原版knn/原版-seismic-results-100.txt", "k": 100},
#     {"name": "F10", "compare_file": "data_big/原版knn/原版-F10-results-1000.txt", "k": 1000},
#     {"name": "sald", "compare_file": "data_big/原版knn/原版-sald-results-1000.txt", "k": 1000},
#     {"name": "seismic", "compare_file": "data_big/原版knn/原版-seismic-results-1000.txt", "k": 1000},
# ]


# 3️⃣ 其他参数，这里dim值固定
dim = 16

# 4️⃣ 数据读取函数
def load_data(data_file, query_file, dataset_name):
    data_offset = 0
    query_offset = 0
    data = cp.fromfile(data_file, dtype=cp.float32, count=20000 * dim, offset=data_offset).reshape(-1, dim)
    if dataset_name == "astro":
        query_count = 100
    else:
        query_count = 1000
    query = cp.fromfile(query_file, dtype=cp.float32, count=query_count * dim, offset=query_offset).reshape(-1, dim)
    return data, query

# 5️⃣ 计算最近邻
def knn_search(data, query, k):
    distances = cp.linalg.norm(data[:, cp.newaxis] - query, axis=2)
    knn_indices = cp.argsort(distances, axis=0)[:k]
    knn_distances = cp.take_along_axis(distances, knn_indices, axis=0)
    return knn_indices, knn_distances

# 6️⃣ 将结果写入文件
def write_results_to_file(knn_indices, knn_distances, k, output_file):
    with open(output_file, 'w') as f:
        for query_idx in range(knn_indices.shape[1]):
            for nn_idx in range(k):
                distance = knn_distances[nn_idx, query_idx]
                index = knn_indices[nn_idx, query_idx]
                f.write(f"the [{query_idx}] query [{nn_idx}] NN is {distance:.6f} at {index}\n")

# 7️⃣ 读取并解析文件
def read_nn_data(file_path):
    nn_data = {}
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split(' ')
            query_index = int(parts[1].strip('[]'))
            nn_index = int(parts[3].strip('[]'))
            nn_value = float(parts[6])
            nn_position = int(parts[8])
            if query_index not in nn_data:
                nn_data[query_index] = []
            nn_data[query_index].append((nn_index, nn_value, nn_position))
    return nn_data

# 8️⃣ 比较最近邻位置
def compare_nn_positions(nn_data1, nn_data2):
    similarity_ratios = {}
    for query_index in nn_data1:
        if query_index in nn_data2:
            nn_positions1 = [nn[2] for nn in nn_data1[query_index]]
            nn_positions2 = [nn[2] for nn in nn_data2[query_index]]
            common_positions = set(nn_positions1) & set(nn_positions2)
            similarity_ratio = len(common_positions) / len(nn_positions1)
            similarity_ratios[query_index] = similarity_ratio
    return similarity_ratios

# 9️⃣ 主程序
def main(data_file, query_file, k, output_file, compare_file, dataset_name):
    # 计算最近邻
    data, query = load_data(data_file, query_file, dataset_name)
    knn_indices, knn_distances = knn_search(data, query, k)
    write_results_to_file(knn_indices, knn_distances, k, output_file)

    # 读取并对比最近邻数据
    nn_data_file1 = read_nn_data(compare_file)
    nn_data_file2 = read_nn_data(output_file)
    similarity_ratios = compare_nn_positions(nn_data_file1, nn_data_file2)
    mean_similarity_ratio = sum(similarity_ratios.values()) / len(similarity_ratios)

    return similarity_ratios, mean_similarity_ratio

# 定义汇总文件路径
summary_file = os.path.join(current_dir, file_dir, "all_results_summary.txt")

# 循环处理每个数据集
with open(summary_file, 'w') as summary:
    for dataset in datasets_combined:
        dataset_name = dataset["name"]
        compare_file = os.path.join(current_dir, f'{dataset["compare_file"]}')
        data_file = os.path.join(current_dir, file_dir, f'{dataset_name}-database.bin')
        query_file = os.path.join(current_dir, file_dir, f'{dataset_name}-query.bin')
        k = dataset["k"]
        output_file = os.path.join(current_dir, file_dir, f'result-{k}/{dataset_name}-results-{k}.txt')

        # 创建结果文件夹（如果不存在）
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        print(f"Processing dataset: {dataset_name} with k={k}")
        similarity_ratios, mean_similarity_ratio = main(data_file, query_file, k, output_file, compare_file, dataset_name)

        # 只输出平均相似度比值到汇总文件
        summary.write(f"{mean_similarity_ratio:.6f}\t")
        if dataset_name=="seismic":
            summary.write("\n")

        print(f"Results written to {output_file}")
        print(f"Mean Similarity Ratio for {dataset_name} with k={k}: {mean_similarity_ratio:.6f}\n")
        print(f"Mean Similarity Ratio for {dataset_name} with k={k} written to summary file.\n")

print("All datasets processed. Summary results are in", summary_file)