"""
Streamlit app: Embedding + Searching Framework
Features:
1) Workspace selection / creation
2) Dataset and model loading
3) Training and embedding
4) Searching and performing

Dependencies: streamlit, numpy, pandas, torch (optional), faiss (or faiss-cpu), annoy, sklearn
Run: streamlit run streamlit_app.py
"""

import streamlit as st
import os
import sys
import json
import time
import subprocess
from pathlib import Path
from typing import Optional

# ---------------------- Utilities ----------------------
DEFAULT_WORKSPACE = "./"
CONFIG_FILENAME = "app_config.json"

def ensure_workspace(path: str) -> str:
    p = Path(path).expanduser().resolve()
    p.mkdir(parents=True, exist_ok=True)
    return str(p)

def run_shell_command(cmd, workdir=None):
    st.write(f"运行命令: `{cmd}`")
    try:
        process = subprocess.Popen(
            cmd,
            shell=True,
            cwd=workdir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            executable="/bin/bash" if sys.platform != "win32" else None
        )
        output_container = st.empty()
        logs = ""
        for line in process.stdout:
            logs += line
            output_container.text_area("日志输出", logs, height=300)
        process.wait()
        if process.returncode == 0:
            st.success("命令执行成功")
        else:
            st.error(f"命令执行失败，返回码: {process.returncode}")
    except Exception as e:
        st.error(f"执行命令出错: {e}")

# ---------------------- Streamlit App ----------------------

st.set_page_config(page_title="Streamlit App", layout="wide")

st.title("Embedding + Searching Framework")

# Workspace selection
tabs = st.tabs(["数据集和模型加载", "模型训练与嵌入", "搜索模块", "工作区浏览器"])

# ---------------------- Dataset & model loading Tab ----------------------
with tabs[0]:
    st.header("数据集和模型加载")

    workspace = st.text_input("工作区文件夹", value=DEFAULT_WORKSPACE)
    if st.button("开始创建工作区"):
        workspace = ensure_workspace(workspace)
        st.success(f"工作区准备完成: {workspace}")

# ---------------------- Training & Embedding Tab ----------------------
with tabs[1]:
    st.subheader("模型训练与嵌入模块")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("**训练配置**")
        gpu_id = st.text_input("NVIDIA 卡号", value="")
        if st.button("开始训练"):
            # 占位函数
            conf_dir = ensure_workspace(os.path.join(workspace, "conf"))
            conf_path = os.path.join(conf_dir, "example.json")
            config = {
                "gpu_id": gpu_id
            }
            with open(conf_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
            st.success(f"配置文件已保存：{conf_path}")
            cmd = f"python run.py -C {conf_path}"
            run_shell_command(cmd, workdir=workspace)


    with col2:
        st.write("**微调配置**")
        model_path = st.text_input("模型路径", value="")
        if st.button("开始微调"):
            # 占位函数
            conf_dir = ensure_workspace(os.path.join(workspace, "conf"))
            conf_path = os.path.join(conf_dir, "example.json")
            config = {
                "model_path": model_path
            }
            with open(conf_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
            st.success(f"配置文件已保存：{conf_path}")
            cmd = f"conda activate jlh && export CUDA_VISIBLE_DEVICES={gpu_id or 0} && python pretrain/run.py -C {conf_path}"
            run_shell_command(cmd, workdir=workspace)

    with col3:
        st.write("**嵌入配置**")
        model_path = st.text_input("用于嵌入的模型路径", value=model_path or "")
        if st.button("生成 Embeddings"):
            # 占位函数
            conf_dir = ensure_workspace(os.path.join(workspace, "conf"))
            conf_path = os.path.join(conf_dir, "example.json")
            config = {
                "model_path": model_path
            }
            with open(conf_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
            st.success(f"配置文件已保存：{conf_path}")
            cmd = f"conda activate jlh && export CUDA_VISIBLE_DEVICES={gpu_id or 0} && python run.py -C {conf_path}"
            run_shell_command(cmd, workdir=workspace)

# ---------------------- Search Tab ----------------------
with tabs[2]:
    st.subheader("搜索模块")

    embeddings_file = st.text_input("已有 Embeddings 文件", value=os.path.join(workspace, 'embeddings', 'embeddings.npy'))
    approx_vs_exact = st.radio("近似 / 精确", options=['近似', '精确'], index=0)
    index_method = st.selectbox("搜索算法", options=['faiss_flat', 'faiss_ivf', 'annoy_angular', 'bruteforce_npy'])
    n_trees = st.number_input("Annoy n_trees", value=10)
    leaf_nodes = st.number_input("叶节点 / nlist", value=100)
    index_out = st.text_input("索引输出路径", value=os.path.join(workspace, 'indexes', 'index.faiss'))

    if st.button("开始搜索"):
        if not Path(embeddings_file).exists():
            st.error("找不到 embeddings 文件")
        # 占位函数
        conf_dir = ensure_workspace(os.path.join(workspace, "conf"))
        conf_path = os.path.join(conf_dir, "search.json")
        config = {
            "index_path": index_out,
            "embedding_file": embeddings_file,
            "method": index_method
        }
        with open(conf_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        st.success(f"搜索配置文件已保存：{conf_path}")
        cmd = f"conda activate jlh && export CUDA_VISIBLE_DEVICES=0 && python run.py -C {conf_path}"
        run_shell_command(cmd, workdir=workspace)


# ---------------------- Workspace Browser Tab ----------------------
with tabs[3]:
    st.subheader("工作区浏览器")
    st.write(f"当前工作区: {workspace}")
    if Path(workspace).exists():
        files = list(Path(workspace).rglob('*'))
        files_display = [str(f.relative_to(workspace)) for f in files if f.is_file()][:500]
        st.write(f"文件数: {len(files_display)}")
        st.dataframe({'path': files_display})
    else:
        st.info("工作区不存在")

