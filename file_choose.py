"""
Dataset and Model Loading Tab
"""

import os
import streamlit as st
from utils import ensure_workspace, display_directory_tree, DEFAULT_OUTPUT_FILE


def dataset_and_model_loading_tab() -> None:
    """Handle the dataset and model loading tab."""
    st.header("数据集和模型文件夹选择")

    # output_file selection - using session_state for global output_file
    output_file_mode = st.radio(
        "文件夹模式",
        options=["选择现有文件夹","创建新文件夹"],
        index=0,
        key="output_file_mode"
    )
    output_dir = st.text_input("文件夹", value=DEFAULT_OUTPUT_FILE, key="output_dir_input")

    if output_file_mode == "创建新文件夹":
        if st.button("开始创建文件夹", key="create_output_dir"):
            output_dir = ensure_workspace(output_dir)
            st.session_state.output_dir = output_dir
            st.success(f"文件夹准备完成: {output_dir}")
    elif output_file_mode == "选择现有文件夹":
        if st.button("选择文件夹", key="select_output_dir"):
            if os.path.exists(output_dir):
                st.session_state.output_dir = output_dir
                st.success(f"文件夹已选择: {output_dir}")
            else:
                st.error("指定的文件夹不存在")

    st.subheader("文件夹文件浏览")
    if 'output_dir' in st.session_state and os.path.exists(st.session_state.output_dir):
        display_directory_tree(st.session_state.output_dir)
    else:
        st.info("请先创建文件夹以查看文件")