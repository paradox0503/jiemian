

import numpy as np
import pandas as pd
import streamlit as st
import json
import os
import glob
import sys
import re
from datetime import datetime

import zipfile
import rarfile
import shutil
from pathlib import Path

from utils import ensure_workspace, run_shell_command, display_directory_tree, DEFAULT_OUTPUT_FILE


# =========================
# 0) 样式 & 页面总标题
# =========================
st.markdown("""
<style>
/* 页面背景 */
.stApp { background-color: #f7f9fc; }
h1 { font-weight: 700; }

.center-btn{
  display:flex;
  justify-content:center;
  margin: 18px 0 12px 0;
}


div[data-testid="stContainer"][data-border="true"]{
  border: 2px solid #222 !important;
  border-radius: 0px !important;
  background: white !important;
  padding: 12px !important;
  min-height: 240px;
}
</style>
""", unsafe_allow_html=True)

st.title("Pre Training")
st.markdown("---")

# =========================
# 1) Load data series collections（同级标题 1）
# =========================
st.header("Load data series collections")

current_dir = Path(DEFAULT_OUTPUT_FILE)
st.session_state["temp_dir"] = str(current_dir)

if current_dir.exists():
    shutil.rmtree(current_dir)
current_dir.mkdir(parents=True, exist_ok=True)

uploaded_files = st.file_uploader(
    "Upload the dataset (supporting .zip and .rar and .bin formats)",
    type=["zip", "rar", "bin"],
    accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        st.warning(f"File is being processed: {uploaded_file.name}")

        local_file_path = current_dir / uploaded_file.name
        with open(local_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # zip/rar 解压到 current_dir；bin 只保存不解压
        if uploaded_file.name.endswith('.zip'):
            with zipfile.ZipFile(local_file_path, 'r') as zip_ref:
                zip_ref.extractall(current_dir)
            if local_file_path.exists():
                local_file_path.unlink()

        elif uploaded_file.name.endswith('.rar'):
            with rarfile.RarFile(local_file_path, 'r') as rar_ref:
                rar_ref.extractall(current_dir)
            if local_file_path.exists():
                local_file_path.unlink()

        elif uploaded_file.name.endswith('.bin'):
            pass

if os.listdir(current_dir):
    st.success("The dataset has been uploaded and decompressed/saved.")

# st.markdown("---")


# =========================
# 2) 工具函数
# =========================
def read_log_file_basic(file_path: str) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return ""
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='gbk') as file:
            return file.read()

def extract_loss_values_from_log(log_content: str):
    pattern = r'loss\s*=\s*([-\d.]+)'
    loss_values = re.findall(pattern, log_content, re.IGNORECASE)

    loss_values_float = []
    for value in loss_values:
        try:
            if value.lower() == 'nan':
                loss_values_float.append(float('nan'))
            else:
                loss_values_float.append(float(value))
        except ValueError:
            continue
    return loss_values_float

def make_loss_df(loss_list, col_name="loss"):
    if not loss_list:
        return pd.DataFrame({col_name: []})
    return pd.DataFrame({col_name: loss_list})


# =========================
# 3) 安全加载 dataset_configs
# =========================
def load_dataset_config():
    if 'pretrain.util.dataset_configs' in sys.modules:
        del sys.modules['pretrain.util.dataset_configs']
    try:
        import pretrain.util.dataset_configs as dataset_config
        return dataset_config
    except ImportError as e:
        st.error(f"Failed to import dataset configuration module: {e}")
        return None

dc = load_dataset_config()

if "dataset_name_selected" not in st.session_state:
    st.session_state["dataset_name_selected"] = ""
if "dataset_path_selected" not in st.session_state:
    st.session_state["dataset_path_selected"] = ""
if "query_path_selected" not in st.session_state:
    st.session_state["query_path_selected"] = ""
if "all_dataset_names" not in st.session_state:
    if dc and hasattr(dc, 'DATASET_CONFIGS'):
        st.session_state["all_dataset_names"] = [ds.name for ds in dc.DATASET_CONFIGS]
    else:
        st.session_state["all_dataset_names"] = []
if "delete_confirm_temp" not in st.session_state:
    st.session_state["delete_confirm_temp"] = False

DATA_ROOT = os.path.abspath("./app/data/")
os.makedirs(DATA_ROOT, exist_ok=True)


# =========================
# 4) 主页面逻辑
# =========================
if dc is None:
    st.error("Failed to load dataset configuration module, pre-training functionality is unavailable!")
else:
    with st.container():
        config_file = "conf/example.json"
        full_config_path = os.path.abspath(os.path.join("pretrain", config_file))

        # 加载配置文件
        if os.path.exists(full_config_path):
            try:
                with open(full_config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except json.JSONDecodeError:
                st.warning(f"The configuration file {full_config_path} is invalid. Using the default configuration instead")
                config = {}
        else:
            config = {}

        # 设置输出路径
        result_model_path = os.path.abspath(f"./app/pretrain/pretrain_{datetime.now().strftime('%Y%m%d_%H%M%S')}/")
        config["output_path"] = result_model_path
        config["result_path"] = result_model_path

        # =========================
        # Dataset Management（同级标题 2）
        # =========================
        # st.header("Dataset Management")

        dataset_names = st.session_state["all_dataset_names"]
        valid_indices = [i for i in dc.SELECTED_DATASETS if isinstance(i, int) and 0 <= i < len(dc.DATASET_CONFIGS)]
        default_selected = [dc.DATASET_CONFIGS[i].name for i in valid_indices if i < len(dc.DATASET_CONFIGS)]
        selected_datasets = st.multiselect(
            "Select training datasets",
            options=dataset_names,
            default=default_selected,
            key="selected_datasets"
        )
        selected_indices = [dataset_names.index(name) for name in selected_datasets if name in dataset_names]

        ds_col1, ds_col2 = st.columns(2)

        with ds_col1:
            with st.expander("Add New Dataset", expanded=False):
                name_to_paths = {}
                all_files = [f for f in os.listdir(DATA_ROOT) if os.path.isfile(os.path.join(DATA_ROOT, f))]
                print(DATA_ROOT, all_files)
                dataset_files = [f for f in all_files if f.endswith("_dataset.bin")]
                query_files = [f for f in all_files if f.endswith("_query.bin")]

                prefix_set = set()
                dataset_path_map = {}
                query_path_map = {}

                for f in dataset_files:
                    prefix = f.replace("_dataset.bin", "")
                    prefix_set.add(prefix)
                    dataset_path_map[prefix] = os.path.join(DATA_ROOT, f)
                for f in query_files:
                    prefix = f.replace("_query.bin", "")
                    prefix_set.add(prefix)
                    query_path_map[prefix] = os.path.join(DATA_ROOT, f)

                name_options = sorted(list(prefix_set))
                for name in name_options:
                    dataset_path = dataset_path_map.get(name, "")
                    query_path = query_path_map.get(name, "")
                    name_to_paths[name] = (dataset_path, query_path)

                selected_name = st.selectbox(
                    "Dataset Name (showing only bin file prefixes in ./app/data)",
                    options=[""] + name_options,
                    key="new_dataset_name_select",
                    on_change=lambda: st.session_state.update({
                        "dataset_name_selected": st.session_state["new_dataset_name_select"],
                        "dataset_path_selected": name_to_paths.get(st.session_state["new_dataset_name_select"], ("", ""))[0],
                        "query_path_selected": name_to_paths.get(st.session_state["new_dataset_name_select"], ("", ""))[1]
                    })
                )

                if selected_name == "":
                    manual_name = st.text_input("Manually enter dataset name", key="manual_dataset_name")
                    final_name = manual_name
                else:
                    final_name = selected_name
                    st.session_state["dataset_name_selected"] = final_name

                bin_files = glob.glob(os.path.join(DATA_ROOT, "*.bin"))
                bin_file_names = [os.path.basename(f) for f in bin_files]
                bin_file_map = {os.path.basename(f): os.path.abspath(f) for f in bin_files}

                dataset_bin_files = [f for f in bin_file_names if f.endswith("_dataset.bin")]
                query_bin_files = [f for f in bin_file_names if f.endswith("_query.bin")]

                st.markdown("---")
                st.markdown("**Dataset File Selection (only _dataset.bin files within ./app/data can be selected)**")

                default_dataset_idx = 0
                if st.session_state["dataset_path_selected"]:
                    selected_dataset_filename = os.path.basename(st.session_state["dataset_path_selected"])
                    if selected_dataset_filename in dataset_bin_files:
                        default_dataset_idx = dataset_bin_files.index(selected_dataset_filename) + 1

                dataset_file_selector = st.selectbox(
                    "Select Dataset File (xxx_dataset.bin)",
                    options=[""] + dataset_bin_files,
                    key="dataset_file_selector",
                    index=default_dataset_idx
                )

                if dataset_file_selector != "":
                    dataset_path = bin_file_map[dataset_file_selector]
                    st.session_state["dataset_path_selected"] = dataset_path
                else:
                    dataset_path = ""

                st.markdown("---")
                st.markdown("**Query File Selection (only _query.bin files within ./app/data can be selected)**")

                default_query_idx = 0
                if st.session_state["query_path_selected"]:
                    selected_query_filename = os.path.basename(st.session_state["query_path_selected"])
                    if selected_query_filename in query_bin_files:
                        default_query_idx = query_bin_files.index(selected_query_filename) + 1

                query_file_selector = st.selectbox(
                    "Select Query File (xxx_query.bin)",
                    options=[""] + query_bin_files,
                    key="query_file_selector",
                    index=default_query_idx
                )

                if query_file_selector != "":
                    query_path = bin_file_map[query_file_selector]
                    st.session_state["query_path_selected"] = query_path
                else:
                    query_path = ""

                new_size_query = st.number_input("Query Size", value=1000, key="new_size_query")
                new_dim_seq = st.number_input("Sequence Dimension", value=256, key="new_dim_seq")

                if st.button("Add New Dataset", key="add_new_dataset", use_container_width=True):
                    if not final_name:
                        st.error("Please enter/select a dataset name!")
                    elif not dataset_path:
                        st.error("Please select a dataset file (xxx_dataset.bin)!")
                    else:
                        if not dataset_path.startswith(DATA_ROOT):
                            st.error(f"Dataset path must be under the {DATA_ROOT} directory!")
                        elif query_path and not query_path.startswith(DATA_ROOT):
                            st.error(f"Query path must be under the {DATA_ROOT} directory!")
                        else:
                            dataset_config_path = dc.__file__
                            try:
                                with open(dataset_config_path, 'r', encoding='utf-8') as f:
                                    content = f.read()

                                indices = re.findall(r'index_name=\s*(\d+)', content)
                                max_index = max([int(i) for i in indices]) if indices else -1
                                new_index = max_index + 1

                                new_config_line = (
                                    f'    DatasetConfig("{final_name}", "{dataset_path}", {new_dim_seq}, '
                                    f'size_train=conf_size_train, size_val=conf_size_val, size_db=conf_size_db, index_name={new_index})'
                                )

                                marker = "]# DATASET_CONFIGS"
                                insert_pos = content.rfind(marker)
                                if insert_pos != -1:
                                    before = content[:insert_pos].rstrip()
                                    after = content[insert_pos:]
                                    if not before.endswith(","):
                                        before += ","
                                    content = before + "\n" + new_config_line + "\n" + after

                                query_indices = re.findall(r'query_index_name=\s*(\d+)', content)
                                max_query_index = max([int(i) for i in query_indices]) if query_indices else -1
                                new_query_index = max_query_index + 1

                                new_embed_line = (
                                    f'    EmbedConfig("{final_name}", "{dataset_path}", "{query_path}", "{new_dim_seq}", '
                                    f'"{new_size_query}", query_index_name={new_query_index})'
                                )

                                embed_marker = "]# embed_CONFIGS"
                                embed_insert_pos = content.rfind(embed_marker)
                                if embed_insert_pos != -1:
                                    before_embed = content[:embed_insert_pos].rstrip()
                                    after_embed = content[embed_insert_pos:]
                                    if not before_embed.endswith(","):
                                        before_embed += ","
                                    content = before_embed + "\n" + new_embed_line + "\n" + after_embed

                                with open(dataset_config_path, 'w', encoding='utf-8') as f:
                                    f.write(content)

                                st.session_state["all_dataset_names"].append(final_name)
                                st.success(f"New dataset '{final_name}' has been successfully added! Absolute path written: {dataset_path}")

                                st.session_state["dataset_name_selected"] = ""
                                st.session_state["dataset_path_selected"] = ""
                                st.session_state["query_path_selected"] = ""
                            except Exception as e:
                                st.error(f"Failed to add dataset: {str(e)}")

        with ds_col2:
            with st.expander("Delete Dataset", expanded=False):
                st.markdown("**Delete an Added Dataset**")

                if st.session_state["all_dataset_names"]:
                    dataset_to_delete = st.selectbox(
                        "Select Dataset to Delete",
                        options=st.session_state["all_dataset_names"],
                        key="dataset_to_delete_select",
                        on_change=lambda: st.session_state.update({"delete_confirm_temp": False})
                    )

                    confirm_delete = st.checkbox(
                        f"Confirm Delete Dataset '{dataset_to_delete}'",
                        key="confirm_delete_checkbox",
                        value=st.session_state["delete_confirm_temp"]
                    )
                    st.session_state["delete_confirm_temp"] = confirm_delete

                    if st.button("Delete Selected Dataset", key="delete_dataset_btn", use_container_width=True):
                        if not confirm_delete:
                            st.error("Please check the confirm delete option!")
                        else:
                            dataset_config_path = dc.__file__
                            try:
                                with open(dataset_config_path, 'r', encoding='utf-8') as f:
                                    content = f.read()

                                dataset_pattern = re.compile(
                                    rf'\s*DatasetConfig\("{re.escape(dataset_to_delete)}",.*?index_name=\d+\)',
                                    re.DOTALL
                                )
                                if dataset_pattern.findall(content):
                                    content = dataset_pattern.sub('', content)
                                    content = re.sub(r',\s*,', ',', content)
                                    content = re.sub(r'\n\s*\n', '\n', content)
                                    content = re.sub(r'\],\s*]', ']', content)

                                embed_pattern = re.compile(
                                    rf'\s*EmbedConfig\("{re.escape(dataset_to_delete)}",.*?query_index_name=\d+\)',
                                    re.DOTALL
                                )
                                if embed_pattern.findall(content):
                                    content = embed_pattern.sub('', content)
                                    content = re.sub(r',\s*,', ',', content)
                                    content = re.sub(r'\n\s*\n', '\n', content)
                                    content = re.sub(r'\],\s*]', ']', content)

                                deleted_index = None
                                for i, ds in enumerate(dc.DATASET_CONFIGS):
                                    if ds.name == dataset_to_delete:
                                        deleted_index = i
                                        break

                                if deleted_index is not None:
                                    selected_pattern = re.compile(r'SELECTED_DATASETS\s*=\s*\[.*?\]', re.DOTALL)
                                    selected_match = selected_pattern.search(content)
                                    if selected_match:
                                        indices = re.findall(r'\d+', selected_match.group())
                                        indices = [int(i) for i in indices]
                                        new_indices = []
                                        for idx in indices:
                                            if idx < deleted_index:
                                                new_indices.append(idx)
                                            elif idx > deleted_index:
                                                new_indices.append(idx - 1)
                                        content = selected_pattern.sub(f"SELECTED_DATASETS = {new_indices}", content)

                                with open(dataset_config_path, 'w', encoding='utf-8') as f:
                                    f.write(content)

                                if dataset_to_delete in st.session_state["all_dataset_names"]:
                                    st.session_state["all_dataset_names"].remove(dataset_to_delete)

                                st.success(f"Dataset '{dataset_to_delete}' has been successfully deleted!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed to delete dataset: {str(e)}")
                else:
                    st.info("No datasets available for deletion")

        if st.button("Save Dataset Selection", key="save_dataset_selection", use_container_width=True):
            dataset_config_path = dc.__file__
            try:
                with open(dataset_config_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                new_line = f"SELECTED_DATASETS = {selected_indices}"
                new_content = re.sub(r'SELECTED_DATASETS\s*=\s*\[.*?\]', new_line, content, flags=re.DOTALL)
                with open(dataset_config_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                st.success(f"Dataset selection has been saved to {dataset_config_path}")
            except Exception as e:
                st.error(f"Failed to save: {e}")

        st.markdown("---")

        # =========================
        # Model configuration
        # =========================
        st.header("Model configuration")

        mode = st.selectbox(
            "Configuration mode",
            ["Load from file", "Manual configuration"],
            index=1,
            key="cfg_mode_select"
        )

        if "manual_patch_len" not in st.session_state:
            st.session_state["manual_patch_len"] = int(config.get("patch_len", 32) or 32)
        if "manual_embed_len" not in st.session_state:
            st.session_state["manual_embed_len"] = int(config.get("first_dim", 256) or 256)

        if mode == "Load from file":
            up = st.file_uploader("Upload config JSON", type=["json"], key="upload_cfg_json")
            if up is not None:
                try:
                    loaded = json.load(up)
                    config.update(loaded)
                    if "patch_len" in loaded:
                        st.session_state["manual_patch_len"] = int(loaded["patch_len"])
                    if "first_dim" in loaded:
                        st.session_state["manual_embed_len"] = int(loaded["first_dim"])
                    st.success("Config loaded from file.")
                except Exception as e:
                    st.error(f"Failed to load JSON: {e}")
        else:
            m1, m2 = st.columns(2)
            with m1:
                P = st.slider("patch length P", 4, 512, st.session_state["manual_patch_len"], step=4)
                st.session_state["manual_patch_len"] = P
                config["patch_len"] = int(P)
            with m2:
                l = st.slider("embedding length l", 16, 1024, st.session_state["manual_embed_len"], step=16)
                st.session_state["manual_embed_len"] = l
                config["first_dim"] = int(l)

        # st.markdown("### Configuration Preview")
        selected_keys = [
            'num_epoch', 'masking_ratio', 'stride', 'patch_len',
            'd_model', 'nhead', 'num_encoder_layers', 'dim_feedforward', 'first_dim'
        ]
        filtered_config = {k: config.get(k, '') for k in selected_keys}
        st.session_state["config_json_cache"] = json.dumps(filtered_config, indent=2)

        config_json = st.text_area(
            "Configuration JSON (other parameters can be edited here)",
            value=st.session_state["config_json_cache"],
            height=150,
            key="train_config_json"
        )

        # st.markdown("---")

        col1, col2, col3 = st.columns(3)
        with col1:
            train_gpu_id = st.text_input("GPU ID", value=config.get("gpu_id", "0"), key="train_gpu_id")
            config["gpu_id"] = train_gpu_id
        with col2:
            model_options = ["transformer", "timemixer", "timesnet"]
            selected_model = st.selectbox(
                "Select Model",
                options=model_options,
                index=model_options.index(config.get("encoder", "transformer")) if config.get("encoder") in model_options else 0,
                key="model_select"
            )
            config["encoder"] = selected_model
        with col3:
            use_decoder = st.toggle("Use Decoder", value=config.get("decoder", False), key="use_decoder_toggle")
            config["decoder"] = use_decoder

            use_curriculum_learning = st.toggle(
                "Use Curriculum Learning",
                value=config.get("use_curriculum_learning", False),
                key="use_curriculum_learning_toggle"
            )
            config["use_curriculum_learning"] = use_curriculum_learning
            if use_curriculum_learning:
                st.info("Curriculum learning requires the user to sort the dataset manually.")

        st.markdown("---")

        # =========================
        # Learning objective configuration
        # =========================
        st.header("Learning objective configuration")
        # st.header("Learning objective configuration (Configure regularization coefficients)")

        c1, c2, c3 = st.columns(3)

        with c1:
            masking_ratio = st.slider(
                "masking ratio",
                min_value=0.0,
                max_value=1.0,
                value=float(config.get("masking_ratio", 0.5) or 0.5),
                step=0.05
            )
           #config["masking_ratio"] = float(masking_ratio)

        with c2:
            func_a_values = np.logspace(-5, 1, num=1000)
            func_a = st.select_slider(
                "func_a parameter",
                options=func_a_values,
                value=float(config.get("func_a", 1e-3) or 1e-3)
            )
            config["func_a"] = float(func_a)
            st.caption(f"{func_a:.5e}")

        with c3:
            func_b_values = np.logspace(-5, 1, num=1000)
            func_b = st.select_slider(
                "func_b parameter",
                options=func_b_values,
                value=float(config.get("func_b", 1e-3) or 1e-3)
            )
            config["func_b"] = float(func_b)
            st.caption(f"{func_b:.5e}")


        st.markdown("---")

        # =========================
        # Data series orchestration configuration
        # =========================
        st.header("Data series orchestration configuration")

        orchestration_w = st.slider("w", 1, 20, 5)
        config["w"] = int(orchestration_w)

        # =========================
        # Start pre-training + Curves
        # =========================
        st.markdown("---")
        st.markdown("<div class='center-btn'>", unsafe_allow_html=True)
        start_pretrain = st.button("Start pre-training", key="start_pretrain_btn", type="primary")
        st.markdown("</div>", unsafe_allow_html=True)

        curve_left, curve_right = st.columns(2)
        with curve_left:
            with st.container(border=True):
                st.markdown("### Train loss curve")
                train_curve_ph = st.empty()
        with curve_right:
            with st.container(border=True):
                st.markdown("### Evaluation loss curve")
                eval_curve_ph = st.empty()

        # ===== 训练逻辑 =====
        if start_pretrain:
            # 1) 保存配置：把 text_area 的 JSON 合并进 config
            try:
                new_config = json.loads(config_json)
                config.update(new_config)
                os.makedirs(os.path.dirname(full_config_path), exist_ok=True)
                with open(full_config_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2)
                st.success(f"Configuration has been updated and saved to {full_config_path}")
            except json.JSONDecodeError:
                st.error("Invalid JSON format")

            # 2) 训练命令
            cmd = (
                "cd pretrain && "
                f"export CUDA_VISIBLE_DEVICES={train_gpu_id} && "
                f"python run.py -C {config_file} && "
                "cd .."
            )
            run_shell_command(cmd, workdir="./")

            # 3) 读 log → 抽 loss → 拆 train/val
            log_path = os.path.join(result_model_path, "fit.log")
            log_content = read_log_file_basic(log_path)
            loss_list = extract_loss_values_from_log(log_content)

            train_list = loss_list[0::2]
            valid_list = loss_list[1::2]

            # 4) 画图：画进 placeholder 内，保证在黑框里；没数据就保持空（只有黑框）
            if len(train_list) > 0:
                train_curve_ph.line_chart(pd.DataFrame({"loss": train_list}))

            if len(valid_list) > 0:
                eval_curve_ph.line_chart(pd.DataFrame({"loss": valid_list}))
