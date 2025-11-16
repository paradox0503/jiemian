# coding = utf-8

class DatasetConfig:
    def __init__(self, name, path_db, dim_seq, size_train, size_val, size_db, index_name):
        self.name = name
        self.path_db = path_db
        self.dim_seq = dim_seq
        self.size_train = size_train
        self.size_val = size_val
        self.size_db = size_db
        self.index_name = index_name


class EmbedConfig:
    def __init__(self, name, dataset_path, query_path, dim_seq, size_query):
        self.name = name
        self.dataset_path = dataset_path
        self.query_path = query_path
        self.dim_seq = dim_seq
        self.size_query = size_query

DATASET_CONFIGS = [
    DatasetConfig("Astro00", "/data/user_jialinhan/process_data_get_record/build/data/astro-dataset.bin", 256, 2000, 1000, 100000, 0),
    DatasetConfig("Deep1B", "/data/user_jialinhan/process_data_get_record/build/data/deep1b-dataset.bin", 96, 2000, 1000, 100000, 1),
    DatasetConfig("F5", "/data/user_jialinhan/process_data_get_record/build/data/F5-dataset.bin", 256, 2000, 1000, 100000, 2),
    DatasetConfig("F10", "/data/user_jialinhan/process_data_get_record/build/data/F10-dataset.bin", 256, 2000, 1000, 10000, 3),
    DatasetConfig("origin", "/data/user_jialinhan/process_data_get_record/build/data/origin-dataset.bin", 256, 2000, 1000, 100000, 4),
    DatasetConfig("sald", "/data/user_jialinhan/process_data_get_record/build/data/sald-dataset.bin", 128, 2000, 1000, 100000, 5),
    DatasetConfig("seismic", "/data/user_jialinhan/process_data_get_record/build/data/seismic-dataset.bin", 256, 2000, 1000, 100000, 6)
]

embed_CONFIGS = [
    EmbedConfig("astro", "data_big/astro-dataset.bin", "data_big/astro-query.bin", 256, 100),
    EmbedConfig("deep1b", "data_big/deep1b-dataset.bin", "data_big/deep1b-query.bin", 96, 1000),
    EmbedConfig("F5", "data_big/F5-dataset.bin", "data_big/F5-query.bin", 256, 1000),
    EmbedConfig("F10", "data_big/F10-dataset.bin", "data_big/F10-query.bin", 256, 1000),
    EmbedConfig("origin", "data_big/origin-dataset.bin", "data_big/origin-query.bin", 256, 1000),
    EmbedConfig("sald", "data_big/sald-dataset.bin", "data_big/sald-query.bin", 128, 1000),
    EmbedConfig("seismic", "data_big/seismic-dataset.bin", "data_big/seismic-query.bin", 256, 1000),
]
