"""
Streamlit app: Embedding + Searching Framework
Home Page

Run: streamlit run home.py
"""
# streamlit run home.py --server.port 8502 --server.enableCORS=false --server.enableXsrfProtection=false
# conda activate KDSelector-jlh
import streamlit as st

# ---------------------- Streamlit App ----------------------
st.set_page_config(page_title="AGENDA: A General Deep Approximation Framework for Data Series Similarity Search", layout="wide")
st.markdown(
    """
    <h1 style='font-size:2.2rem; font-weight:700; margin-bottom: 1rem;'>AGENDA: A General Deep Approximation Framework for Data Series Similarity Search</h1>
    """,
    unsafe_allow_html=True
)

# st.write("请使用左侧导航栏选择功能页面。")

# Set default workspace
if 'workspace' not in st.session_state:
    st.session_state.workspace = "./"

