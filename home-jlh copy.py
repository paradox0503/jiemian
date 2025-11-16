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

# Workspace selection - 全局统一工作区变量
workspace = st.text_input("工作区文件夹", value=DEFAULT_WORKSPACE)
if st.button("开始创建工作区"):
    workspace = ensure_workspace(workspace)
    st.success(f"工作区准备完成: {workspace}")

tabs = st.tabs(["数据集和模型加载", "模型训练与嵌入", "搜索模块", "工作区浏览器"])

# ---------------------- Dataset & model loading Tab ----------------------
with tabs[0]:
    st.header("数据集和模型加载")
    st.subheader("文件上传")
    uploaded_files = st.file_uploader("拖拽或选择文件/文件夹（支持多个文件）", accept_multiple_files=True)
    if uploaded_files and workspace:
        for uploaded_file in uploaded_files:
            st.write(f"上传文件: {uploaded_file.name}")
            # 修复：确保工作区存在后再保存文件
            file_save_path = os.path.join(workspace, uploaded_file.name)
            with open(file_save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
        st.success("文件上传完成")
    elif uploaded_files and not workspace:
        st.warning("请先创建工作区再上传文件")

# ---------------------- Training & Embedding Tab ----------------------
with tabs[1]:
    st.subheader("模型训练与嵌入模块")
    col1, col2, col3 = st.columns(3)

    # 修复跨列变量：每个列单独添加 gpu_id 输入框（避免变量未定义）
    with col1:
        st.write("**训练配置**")
        train_gpu_id = st.text_input("NVIDIA 卡号（训练）", value="0")  # 单独命名，默认值0
        if st.button("开始训练") and workspace:
            # 修复路径：去掉 /pretrain 前的斜杠，确保相对工作区
            conf_dir = ensure_workspace(os.path.join(workspace, "pretrain/conf"))
            conf_path = os.path.join(conf_dir, "pretrain.json")
            config = {
                "gpu_id": train_gpu_id,
                "mode": "pretrain"
            }
            with open(conf_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
            st.success(f"配置文件已保存：{conf_path}")
            # 统一 cmd 格式：加载 .bashrc + 激活 conda 环境
            cmd = (
                f"source ~/.bashrc && "
                f"conda activate jlh && "
                f"export CUDA_VISIBLE_DEVICES={train_gpu_id} && "
                f"export LD_LIBRARY_PATH=/mnt/data/user_liangzhiyu/envs/jlh/lib:$LD_LIBRARY_PATH && "
                f"python pretrain/run.py -C {conf_path}"
            )
            run_shell_command(cmd, workdir=workspace)
        elif not workspace:
            st.warning("请先创建工作区再开始训练")

    with col2:
        st.write("**微调配置**")
        fine_model_path = st.text_input("模型路径（微调）", value="")
        fine_gpu_id = st.text_input("NVIDIA 卡号（微调）", value="0")  # 补全 gpu_id 输入框
        if st.button("开始微调") and workspace:
            conf_dir = ensure_workspace(os.path.join(workspace, "conf"))
            conf_path = os.path.join(conf_dir, "fine_tune.json")
            config = {
                "model_path": fine_model_path,
                "gpu_id": fine_gpu_id,
                "mode": "fine"
            }
            with open(conf_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
            st.success(f"配置文件已保存：{conf_path}")
            # 统一 cmd 格式
            cmd = (
                f"source ~/.bashrc && "
                f"conda activate jlh && "
                f"export CUDA_VISIBLE_DEVICES={fine_gpu_id} && "
                f"export LD_LIBRARY_PATH=/mnt/data/user_liangzhiyu/envs/jlh/lib:$LD_LIBRARY_PATH && "
                f"python pretrain/run.py -C {conf_path}"
            )
            run_shell_command(cmd, workdir=workspace)
        elif not workspace:
            st.warning("请先创建工作区再开始微调")

    with col3:
        st.write("**嵌入配置**")
        embed_model_path = st.text_input("用于嵌入的模型路径", value="")
        embed_gpu_id = st.text_input("NVIDIA 卡号（嵌入）", value="0")  # 补全 gpu_id 输入框
        if st.button("生成 Embeddings") and workspace:
            conf_dir = ensure_workspace(os.path.join(workspace, "conf"))
            conf_path = os.path.join(conf_dir, "embedding.json")
            config = {
                "model_path": embed_model_path,
                "gpu_id": embed_gpu_id,
                "mode": "embed"
            }
            with open(conf_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
            st.success(f"配置文件已保存：{conf_path}")
            # 统一 cmd 格式
            cmd = (
                f"source ~/.bashrc && "
                f"conda activate jlh && "
                f"export CUDA_VISIBLE_DEVICES={embed_gpu_id} && "
                f"export LD_LIBRARY_PATH=/mnt/data/user_liangzhiyu/envs/jlh/lib:$LD_LIBRARY_PATH && "
                f"python pretrain/run.py -C {conf_path}"
            )
            run_shell_command(cmd, workdir=workspace)
        elif not workspace:
            st.warning("请先创建工作区再生成 Embeddings")

# ---------------------- Search Tab ----------------------
with tabs[2]:
    st.subheader("搜索模块")
    # 补全 gpu_id 输入框（之前缺失）
    search_gpu_id = st.text_input("NVIDIA 卡号（搜索）", value="0")
    embeddings_file = st.text_input("已有 Embeddings 文件", value=os.path.join(workspace, 'embeddings', 'embeddings.npy'))
    approx_vs_exact = st.radio("近似 / 精确", options=['近似', '精确'], index=0)
    index_method = st.selectbox("搜索算法", options=['faiss_flat', 'faiss_ivf', 'annoy_angular', 'bruteforce_npy'])
    n_trees = st.number_input("Annoy n_trees", value=10)
    leaf_nodes = st.number_input("叶节点 / nlist", value=100)
    index_out = st.text_input("索引输出路径", value=os.path.join(workspace, 'indexes', 'index.faiss'))

    if st.button("开始搜索") and workspace:
        embeddings_file = os.path.join(workspace, embeddings_file) if not Path(embeddings_file).is_absolute() else embeddings_file
        if not Path(embeddings_file).exists():
            st.error(f"找不到 embeddings 文件：{embeddings_file}")
        else:
            conf_dir = ensure_workspace(os.path.join(workspace, "conf"))
            conf_path = os.path.join(conf_dir, "search.json")
            config = {
                "index_path": index_out,
                "embedding_file": embeddings_file,
                "method": index_method,
                "n_trees": n_trees,
                "leaf_nodes": leaf_nodes,
                "gpu_id": search_gpu_id,
                "mode": "search"  # 修复 mode 错误（之前是 embed）
            }
            with open(conf_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
            st.success(f"搜索配置文件已保存：{conf_path}")
            # 统一 cmd 格式
            cmd = (
                f"source ~/.bashrc && "
                f"conda activate jlh && "
                f"export CUDA_VISIBLE_DEVICES={search_gpu_id} && "
                f"export LD_LIBRARY_PATH=/mnt/data/user_liangzhiyu/envs/jlh/lib:$LD_LIBRARY_PATH && "
                f"python pretrain/run.py -C {conf_path}"
            )
            run_shell_command(cmd, workdir=workspace)
    elif not workspace:
        st.warning("请先创建工作区再开始搜索")

# ---------------------- Workspace Browser Tab ----------------------
with tabs[3]:
    st.subheader("工作区浏览器")
    st.write(f"当前工作区: {workspace}")
    if Path(workspace).exists():
        files = list(Path(workspace).rglob('*'))
        files_display = [str(f.relative_to(workspace)) for f in files if f.is_file()][:500]
        st.write(f"文件数: {len(files_display)}")
        st.dataframe({'路径': files_display})
    else:
        st.info("工作区不存在，请先创建工作区")