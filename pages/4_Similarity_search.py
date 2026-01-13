"""
Search Page
"""

import streamlit as st
import os
import json
from pathlib import Path
from utils import ensure_workspace, run_shell_command
import pandas as pd
def plot_basic_line_chart(list1,list2,list3):
    # 创建DataFrame（最常用方式）
    chart_data = pd.DataFrame({
        "query": list1,
        "location": list2,
        "distance": list3
    })
    # # 显示数据表格
    with st.expander("📋 查看数据"):
        st.dataframe(chart_data)

def modify_nth_line(file_path, n, new_content, line_start=1):
    """
    修改文件的第n行内容

    Args:
        file_path: 文件路径
        n: 要修改的行号（从line_start开始计数）
        new_content: 新的内容
        line_start: 行号起始值（默认从1开始，也可设为0）
    """
    # 调整行号搜索
    line_index = n - line_start

    # 读取所有行
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 检查行号是否有效
    if line_index < 0 or line_index >= len(lines):
        print(f"错误：行号{n}超出文件范围（1-{len(lines)}）")
        return False

    # 修改指定行
    lines[line_index] = new_content + '\n' if not new_content.endswith('\n') else new_content

    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    return True
st.set_page_config(page_title="搜索模块", layout="wide")
st.title("搜索模块")

st.subheader("搜索模块")
st.subheader("Searching")
with st.expander("Load target data series collection", expanded=False):
    # 256维原始数据集输入框
    v_original = st.text_input(
        label="Original query dataset",
        key="Load target query data series collection",
        value="/data/user_jialinhan/data_big/astro_query.bin"
    )
    # embed之后的数据集输入框
    v_embed = st.text_input(
        label="Embedded query dataset",
        key="Load target embed query data series collection",
        value="/data/user_jialinhan/SEAnet-main-yuanban/SEAnet/astro_query.bin"
    )
# Load index
Load_index= st.selectbox(
    "Load index",
    options=['astro', 'deep1b', 'sald'],
    key="Load index already"
)

index_method = st.selectbox(
    "搜索算法",
    options=['iSAX', 'DIDS', 'Dumpy'],
    key="index_method"
)
if index_method=='iSAX':
    txt_path="/data/user_jialinhan/jiemian/isax/search.txt"
    with st.expander("Configuration", expanded=False):
        v = st.text_input("query_num",key="query_num",value="100")
        modify_nth_line(txt_path, 1, v)
        v = st.text_input("k",    key="k",value="1")
        modify_nth_line(txt_path, 2, v)
        # v = st.text_input("data_name",key="data_name",value="astro")
        v ="astro"
        modify_nth_line(txt_path, 3, v)
        # v = st.text_input("origin_input_directory",key="origin_input_directory",value="/data/user_jialinhan/data_big/")
        v="/data/user_jialinhan/data_big/"
        modify_nth_line(txt_path, 4, v)
        # v = st.text_input("embed_input_directory",      key="embed_input_directory",value="/data/user_jialinhan/SEAnet-main-yuanban/SEAnet/")
        v="/data/user_jialinhan/SEAnet-main-yuanban/SEAnet/"
        modify_nth_line(txt_path, 5, v)
        v = st.text_input("ts_length",      key="ts_length",value="256")
        modify_nth_line(txt_path, 6, v)
        v = st.text_input("max_search_leaf_nodes_num",      key="max_search_leaf_nodes_num",value="500")


else:
    pass

if st.button("开始搜索", key="start_search"):
    if index_method=='iSAX':
        cmd = (
            f"cd /data/user_jialinhan/jiemian/isax/build && "
            f"./search "
        )
        run_shell_command(cmd, workdir="./")
        res_file_location = "/data/user_jialinhan/jiemian/isax/build/1stBSF/astro.txt"

        # 使用pandas读取
        df = pd.read_csv(res_file_location, header=None, names=['col1', 'col2', 'col3'])

        # 转换为列表
        list1 = df['col1'].astype(int).tolist()    # 第一列
        list2 = df['col2'].astype(int).tolist()    # 第二列
        list3 = df['col3'].astype(float).tolist()  # 第三列
        plot_basic_line_chart(list1,list2,list3)
