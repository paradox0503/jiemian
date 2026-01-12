"""
Search Page
"""

import streamlit as st
import os
import json
from pathlib import Path
from utils import ensure_workspace, run_shell_command
def modify_nth_line(file_path, n, new_content, line_start=1):
    """
    修改文件的第n行内容

    Args:
        file_path: 文件路径
        n: 要修改的行号（从line_start开始计数）
        new_content: 新的内容
        line_start: 行号起始值（默认从1开始，也可设为0）
    """
    # 调整行号索引
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
st.set_page_config(page_title="索引模块", layout="wide")
st.title("索引模块")

"""Handle the search tab."""
st.subheader("索引模块")
# embeddings_file = st.text_input(
#     "已有 Embeddings 文件",
#     value="",
#     key="embeddings_file"
# )
index_method = st.selectbox(
    "索引算法",
    options=['iSAX', 'DIDS', 'Dumpy'],
    key="index_method"
)
if index_method=='iSAX':
    txt_path="/data/user_jialinhan/jiemian/isax/index.txt"
    v = st.text_input("query_num",key="query_num",value="100")
    modify_nth_line(txt_path, 1, v)
    v = st.text_input("k",    key="k",value="1")
    modify_nth_line(txt_path, 2, v)
    v = st.text_input("data_name",key="data_name",value="astro")
    modify_nth_line(txt_path, 3, v)
    v = st.text_input("origin_input_directory",key="origin_input_directory",value="/data/user_jialinhan/data_big/")
    modify_nth_line(txt_path, 4, v)
    v = st.text_input("embed_input_directory",      key="embed_input_directory",value="/data/user_jialinhan/SEAnet-main-yuanban/SEAnet/")
    modify_nth_line(txt_path, 5, v)
    v = st.text_input("ts_length",      key="ts_length",value="256")
    modify_nth_line(txt_path, 6, v)
    v = st.text_input("ts_num",     key="ts_num",value="10000000")
    modify_nth_line(txt_path, 7, v)
    v = st.text_input("ref_objs_size",      key="ref_objs_size",value="1000")
    modify_nth_line(txt_path, 8, v)
    v = st.text_input("approximate_leaf_size",     key="approximate_leaf_size",value="10000")
    modify_nth_line(txt_path, 9, v)
    v = st.text_input("ts_buffer_size_for_read",
      key="ts_buffer_size_for_read",value="10000")
    modify_nth_line(txt_path, 10, v)
    v = st.text_input("ts_buffer_size_per_ref_obj",key="ts_buffer_size_per_ref_obj",value="100")
    modify_nth_line(txt_path, 11, v)

else:
    pass


if st.button("开始搜索", key="start_search"):
    if index_method=='iSAX':

        cmd = (
            f"cd /data/user_jialinhan/jiemian/isax/build && "
            f"make && "
            f"./index "
        )
        run_shell_command(cmd, workdir="./")
    else:
        print("error")
else:
    pass