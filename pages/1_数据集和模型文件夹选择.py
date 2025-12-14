"""
Dataset and Model Loading Page
"""

import streamlit as st
import zipfile
import rarfile
import shutil
from pathlib import Path
import os
from utils import ensure_workspace, display_directory_tree, DEFAULT_OUTPUT_FILE

st.set_page_config(page_title="数据集和模型文件夹选择", layout="wide")
st.title("数据集和模型文件夹选择")

st.markdown("""
    <h2 style='text-align: center; color: #000000;'> 数据集上传器</h2>
    <p style='text-align: center;'>上传您的数据集（支持 .zip 和 .rar 格式）进行处理。</p>
    <hr style='border:1px solid #000000;'>
""", unsafe_allow_html=True)

# 设置数据目录，与1_Dataset.py一致
current_dir = Path(DEFAULT_OUTPUT_FILE)
st.session_state["temp_dir"] = str(current_dir)

if current_dir.exists():
    shutil.rmtree(current_dir)
current_dir.mkdir(parents=True, exist_ok=True)

uploaded_files = st.file_uploader(
    "上传数据集（支持 .zip 和 .rar）",
    type=["zip", "rar"],
    accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        st.warning(f"正在处理文件: {uploaded_file.name}")

        local_file_path = current_dir / uploaded_file.name
        with open(local_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # 假设有extract_file函数，如果没有，需要实现简单的解压
        # 这里简化：直接解压zip或rar
        if uploaded_file.name.endswith('.zip'):
            with zipfile.ZipFile(local_file_path, 'r') as zip_ref:
                zip_ref.extractall(current_dir)
        elif uploaded_file.name.endswith('.rar'):
            with rarfile.RarFile(local_file_path, 'r') as rar_ref:
                rar_ref.extractall(current_dir)

        if local_file_path.exists():
            local_file_path.unlink()

if not os.listdir(current_dir):
    st.warning(" No timeseries uploaded yet. Please upload your metrics to proceed.")
else:
    st.success("数据集已上传并解压。")
    # 移除显示文件夹树的代码