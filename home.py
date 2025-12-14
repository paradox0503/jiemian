"""
Streamlit app: Embedding + Searching Framework
Home Page

Run: streamlit run home.py
"""
# streamlit run home.py --server.port 8502 --server.enableCORS=false --server.enableXsrfProtection=false
# conda activate KDSelector-jlh
import streamlit as st

# ---------------------- Streamlit App ----------------------
st.set_page_config(page_title="Embedding + Searching Framework", layout="wide")
st.title("Embedding + Searching Framework")

st.write("欢迎使用嵌入 + 搜索框架。")
st.write("请使用左侧导航栏选择功能页面。")

# Set default workspace
if 'workspace' not in st.session_state:
    st.session_state.workspace = "./"

