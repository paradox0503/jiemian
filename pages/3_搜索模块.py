"""
Search Page
"""

import streamlit as st
import os
import json
from pathlib import Path
from utils import ensure_workspace, run_shell_command
st.set_page_config(page_title="搜索模块", layout="wide")
st.title("搜索模块")

"""Handle the search tab."""
st.subheader("搜索模块")
search_gpu_id = st.text_input("NVIDIA 卡号（搜索）", value="0", key="search_gpu_id")
embeddings_file = st.text_input(
    "已有 Embeddings 文件",
    value="",
    key="embeddings_file"
)
approx_vs_exact = st.radio("近似 / 精确", options=['近似', '精确'], index=0, key="approx_vs_exact")
index_method = st.selectbox(
    "搜索算法",
    options=['faiss_flat', 'faiss_ivf', 'annoy_angular', 'bruteforce_npy'],
    key="index_method"
)
n_trees = st.number_input("Annoy n_trees", value=10, key="n_trees")
leaf_nodes = st.number_input("叶节点 / nlist", value=100, key="leaf_nodes")
index_out = st.text_input(
    "索引输出路径",
    value="",
    key="index_out"
)

if st.button("开始搜索", key="start_search"):
    if not Path(embeddings_file).exists():
        st.error(f"找不到 embeddings 文件：{embeddings_file}")
    else:
        output_dir = st.session_state.get('output_dir', "./")
        conf_dir = ensure_workspace(os.path.join(output_dir, "conf"))
        conf_path = os.path.join(conf_dir, "search.json")
        config = {
            "index_path": index_out,
            "embedding_file": embeddings_file,
            "method": index_method,
            "n_trees": n_trees,
            "leaf_nodes": leaf_nodes,
            "gpu_id": search_gpu_id,
            "mode": "search"
        }
        with open(conf_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        st.success(f"搜索配置文件已保存：{conf_path}")

        cmd = (
            f"source ~/.bashrc && "
            f"conda activate jlh && "
            f"export CUDA_VISIBLE_DEVICES={search_gpu_id} && "
            f"export LD_LIBRARY_PATH=/mnt/data/user_liangzhiyu/envs/jlh/lib:$LD_LIBRARY_PATH && "
            f"python run.py -C {conf_path}"
        )
        run_shell_command(cmd, workdir="./")