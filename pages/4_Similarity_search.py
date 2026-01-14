"""
Similarity_search Page
"""

import streamlit as st
import os
import json
from pathlib import Path
from utils import ensure_workspace, run_shell_command
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def plot_basic_line_chart(list1, list2, list3):
    """Display search results in a DataFrame"""
    chart_data = pd.DataFrame({
        "query": list1,
        "location": list2,
        "distance": list3
    })
    with st.expander("Search Results Table"):
        st.dataframe(chart_data)
    return chart_data

def modify_nth_line(file_path, n, new_content, line_start=1):
    """
    Modify the nth line of a file

    Args:
        file_path: Path to the file
        n: Line number to modify (starting from line_start)
        new_content: New content for the line
        line_start: Starting line number (default 1, can be set to 0)
    """
    line_index = n - line_start

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    if line_index < 0 or line_index >= len(lines):
        print(f"Error: Line number {n} out of range (1-{len(lines)})")
        return False

    lines[line_index] = new_content + '\n' if not new_content.endswith('\n') else new_content

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    return True

def read_sequence_from_file(file_path, index, dim):
    """Read sequence from binary file at specified index"""
    try:
        with open(file_path, 'rb') as f:
            f.seek(index * dim * 4)  # Each float32 occupies 4 bytes
            data = np.fromfile(f, dtype=np.float32, count=dim)
        return data
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return np.zeros(dim)

def plot_sequences(query_sequence, database_sequences, query_orig, kv):
    """Plot query and database sequences comparison"""
    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot query sequence (red)
    ax.plot(query_sequence, label=f'Query {query_orig+1}', color='red', linewidth=2.5)

    # Plot database sequences (blue)
    for i, db_seq in enumerate(database_sequences):
        ax.plot(db_seq, label=f'Database {i+1}', color='blue', linestyle='--', alpha=0.7)

    # Configure plot properties
    ax.set_title(f'Query {query_orig+1} vs {len(database_sequences)} Database Sequences (k={kv})')
    ax.set_xlabel('Dimension')
    ax.set_ylabel('Value')
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(True, alpha=0.3)

    # Set y-axis limits for better visualization
    all_data = np.concatenate([query_sequence] + database_sequences)
    y_min, y_max = all_data.min(), all_data.max()
    y_range = y_max - y_min
    ax.set_ylim(y_min - 0.1*y_range, y_max + 0.1*y_range)

    st.pyplot(fig)

# Page configuration
st.set_page_config(page_title="Similarity Search Module", layout="wide")
st.markdown(
    """
<style>
.stApp { background-color: #f7f9fc; }
.center-btn { display:flex; justify-content:center; margin: 18px 0 12px 0; }

/* black bordered boxes: st.container(border=True) */
div[data-testid="stContainer"][data-border="true"]{
  border: 2px solid #222 !important;
  border-radius: 0px !important;
  background: white !important;
  padding: 12px !important;
  min-height: 240px;
}
</style>
""",
    unsafe_allow_html=True,
)

st.title("Similarity Search Module")

# Initialize session state
if 'search_results' not in st.session_state:
    st.session_state.search_results = None
if 'kv' not in st.session_state:
    st.session_state.kv = "1"
if 'search_done' not in st.session_state:
    st.session_state.search_done = False

# Section 1: Load queries
st.markdown("---")
st.header("Load Queries")

with st.expander("Load Target Data Series Collection", expanded=False):
    v_original = st.text_input(
        label="Original Query Dataset",
        key="Load_target_query_data_series_collection",
        value="/data/user_jialinhan/data_big/astro_query.bin"
    )

    v_embed = st.text_input(
        label="Embedded Query Dataset",
        key="Load_target_embed_query_data_series_collection",
        value="/data/user_jialinhan/SEAnet-main-yuanban/SEAnet/astro_query.bin"
    )

# Section 2: Load Index
st.markdown("---")
st.header("Load Index")

Load_index = st.selectbox(
    "Load Index of Dataset",
    options=['astro', 'deep1b', 'sald'],
    key="Load_index_already"
)

index_method = st.selectbox(
    "Search Algorithm",
    options=['iSAX', 'DIDS', 'Dumpy'],
    key="index_method"
)

if index_method == 'iSAX':
    txt_path = "/data/user_jialinhan/jiemian/isax/search.txt"

    st.markdown("---")
    st.header("Configuration")

    with st.expander("Parameter Settings", expanded=False):
        v = st.text_input("query_num", key="query_num", value="100")
        modify_nth_line(txt_path, 1, v)

        kv = st.text_input("k", key="k", value="1")
        st.session_state.kv = kv
        modify_nth_line(txt_path, 2, kv)

        v = "astro"
        modify_nth_line(txt_path, 3, v)

        v = "/data/user_jialinhan/data_big/"
        modify_nth_line(txt_path, 4, v)

        v = "/data/user_jialinhan/SEAnet-main-yuanban/SEAnet/"
        modify_nth_line(txt_path, 5, v)

        v = st.text_input("ts_length", key="ts_length", value="256")
        modify_nth_line(txt_path, 6, v)

        v = st.text_input("max_search_leaf_nodes_num", key="max_search_leaf_nodes_num", value="500")
        modify_nth_line(txt_path, 7, v)

st.markdown("---")

# Search button
search_button = st.button("Start Searching", key="start_search", type="primary")

# Section 3: Display Results
st.markdown("---")
st.header("Query Results")

if search_button:
    with st.spinner("Searching..."):
        if index_method == 'iSAX':
            cmd = (
                f"cd /data/user_jialinhan/jiemian/isax/build && "
                f"./search"
            )
            run_shell_command(cmd, workdir="./")

            res_file_location = "/data/user_jialinhan/jiemian/isax/build/1stBSF/astro.txt"

            try:
                df = pd.read_csv(res_file_location, header=None, names=['col1', 'col2', 'col3'])

                list1 = df['col1'].astype(int).tolist()
                list2 = df['col2'].astype(int).tolist()
                list3 = df['col3'].astype(float).tolist()

                st.session_state.search_results = {
                    'list1': list1,
                    'list2': list2,
                    'list3': list3
                }
                st.session_state.search_done = True

                st.success("Search completed successfully!")

            except Exception as e:
                st.error(f"Error reading result file: {e}")
                st.session_state.search_done = False

# If search is completed, display results and visualization options
if st.session_state.search_done and st.session_state.search_results:
    list1 = st.session_state.search_results['list1']
    list2 = st.session_state.search_results['list2']
    list3 = st.session_state.search_results['list3']

    # Display results table
    chart_data = plot_basic_line_chart(list1, list2, list3)

    # Section 4: Query Visualization
    st.markdown("---")
    st.header("Query Visualization")

    # Create two-column layout
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Select Query Number")
        max_query_num = len(set(list1))

        # Query number input
        query_num_options = list(range(1, max_query_num + 1))
        selected_query = st.selectbox(
            "Select query number to visualize",
            options=query_num_options,
            key="selected_query_vis",
            index=0
        )

        # Show current query statistics
        st.info(f"Total queries: {max_query_num}")
        st.info(f"K value per query: {st.session_state.kv}")

        # Visualization button
        plot_button = st.button("Generate Visualization", key="plot_button", type="secondary")

    with col2:
        if plot_button:
            # Calculate parameters
            query_orig = selected_query - 1
            kv = int(st.session_state.kv)
            locationo = kv * query_orig

            # Extract database sequence indices for the query
            list2_slice = list2[locationo:locationo + kv]

            # File paths
            origin_directory = "/data/user_jialinhan/data_big/"
            data_name = "astro"
            ori_database_filename = origin_directory + data_name + "-dataset.bin"
            ori_query_filename = origin_directory + data_name + "-query.bin"
            dim = 256

            # Read data
            query_sequence = read_sequence_from_file(ori_query_filename, query_orig, dim)
            database_sequences = [read_sequence_from_file(ori_database_filename, idx, dim) for idx in list2_slice]

            # Verify data
            if len(query_sequence) == dim and all(len(seq) == dim for seq in database_sequences):
                # Plot sequence comparison
                plot_sequences(query_sequence, database_sequences, query_orig, kv)

                # Display query details
                st.write(f"**Details for Query {selected_query}:**")
                st.write(f"- Query index: {query_orig}")
                st.write(f"- Matched database sequence indices: {list2_slice}")
                st.write(f"- Query sequence length: {len(query_sequence)}")
                st.write(f"- Number of database sequences: {len(database_sequences)}")
            else:
                st.error("Data reading error: Sequence length mismatch!")
                st.write(f"Query sequence length: {len(query_sequence)} (expected: {dim})")
                st.write(f"Number of database sequences: {len(database_sequences)}")
                for i, seq in enumerate(database_sequences):
                    st.write(f"  Sequence {i+1} length: {len(seq)} (expected: {dim})")