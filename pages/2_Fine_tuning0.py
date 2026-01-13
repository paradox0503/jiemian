"""
Fine-tuning Page (UI aligned with the figure)
- Right-side layout only: sections + centered Start button + two bordered loss boxes
- Keeps your original: config save, update dataset_configs.py FINE_SELECTED_DATASETS, run fine/run.py, read fit.log
"""

import os
import sys
import json
import re
from datetime import datetime

import pandas as pd
import streamlit as st

from utils import run_shell_command  # keep your util import


# =========================
# Utils: log parsing
# =========================
def read_log_file_basic(file_path: str) -> str:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""
    except UnicodeDecodeError:
        with open(file_path, "r", encoding="gbk") as f:
            return f.read()

def extract_loss_values_from_log(log_content: str):
    # matches: loss = 0.123 (does not cover scientific notation, keep same as yours)
    pattern = r"loss\s*=\s*([-\d.]+)"
    loss_values = re.findall(pattern, log_content, re.IGNORECASE)
    out = []
    for v in loss_values:
        try:
            out.append(float("nan") if v.lower() == "nan" else float(v))
        except ValueError:
            continue
    return out


# =========================
# Safe import dataset_configs
# =========================
def load_dataset_config():
    if "pretrain.util.dataset_configs" in sys.modules:
        del sys.modules["pretrain.util.dataset_configs"]
    try:
        import pretrain.util.dataset_configs as dataset_config
        return dataset_config
    except ImportError as e:
        st.error(f"Failed to import dataset configuration module: {e}")
        return None

dc = load_dataset_config()


# =========================
# Styles: black boxes + center button
# =========================
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

# ===== Page title (top) =====
st.title("Fine-tuning")
st.markdown("---")


# =========================
# Config paths
# =========================
config_file = "conf/example.json"
full_config_path = os.path.abspath(os.path.join("fine", config_file))
os.makedirs(os.path.dirname(full_config_path), exist_ok=True)

# load config
if os.path.exists(full_config_path):
    try:
        with open(full_config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except json.JSONDecodeError:
        st.warning(f"Config file invalid: {full_config_path}. Using default config.")
        config = {}
else:
    config = {}

# output path for this run
fine_result_model_path = os.path.abspath(f"./app/fine/fine_{datetime.now().strftime('%Y%m%d_%H%M%S')}/")
config["output_path"] = fine_result_model_path
config["result_path"] = fine_result_model_path

DATA_ROOT = os.path.abspath("./app/data")
os.makedirs(DATA_ROOT, exist_ok=True)

# dataset name list from pretrain configs
if "all_dataset_names" not in st.session_state:
    if dc and hasattr(dc, "DATASET_CONFIGS"):
        st.session_state["all_dataset_names"] = [ds.name for ds in dc.DATASET_CONFIGS]
    else:
        st.session_state["all_dataset_names"] = []


# =========================
# Section 1: Load target data series collection for fine-tuning
# =========================
st.header("Load target data series collection for fine-tuning")

dataset_names = st.session_state.get("all_dataset_names", [])
if not dataset_names:
    st.warning("No datasets found. Please add datasets in Pre-training page first.")
    selected_dataset = None
    selected_index = None
else:
    # default selection
    if "FINE_SELECTED_DATASETS" not in st.session_state:
        st.session_state["FINE_SELECTED_DATASETS"] = dataset_names[0]

    selected_dataset = st.selectbox(
        "Select fine-tuning dataset",
        options=dataset_names,
        index=dataset_names.index(st.session_state["FINE_SELECTED_DATASETS"])
        if st.session_state["FINE_SELECTED_DATASETS"] in dataset_names else 0,
        key="FINE_SELECTED_DATASETS",
    )
    selected_index = dataset_names.index(selected_dataset)
    config["selected_dataset_index"] = selected_index
    st.caption(f"Selected dataset: {selected_dataset}  (index: {selected_index})")

st.markdown("---")


# =========================
# Section 2: Load model
# =========================
st.header("Load model")

# model path input (kept from your logic)
if "fine_model_path" not in st.session_state:
    st.session_state["fine_model_path"] = config.get("pkl_file", "")

fine_model_path = st.text_input(
    "Model checkpoint path (.pkl / .pt etc.)",
    value=st.session_state["fine_model_path"],
    key="fine_model_path_input",
)
config["pkl_file"] = fine_model_path

st.markdown("---")


# =========================
# Section 3: Configuration (JSON + key controls)
# =========================
st.header("Configuration")

# init session state defaults
if "fine_gpu_id" not in st.session_state:
    st.session_state["fine_gpu_id"] = config.get("gpu_id", "0")
if "fine_dim_series" not in st.session_state:
    st.session_state["fine_dim_series"] = int(config.get("dim_series", 256) or 256)
if "fine_encoder" not in st.session_state:
    st.session_state["fine_encoder"] = config.get("encoder", "transformer")
if "fine_epoch" not in st.session_state:
    st.session_state["fine_epoch"] = int(config.get("fine_epoch", 1) or 1)

# a row of common parameters (like your old fine config)
c1, c2, c3 = st.columns(3)
with c1:
    fine_gpu_id = st.text_input("GPU ID", value=str(st.session_state["fine_gpu_id"]), key="fine_gpu_id_input")
    config["gpu_id"] = fine_gpu_id
with c2:
    fine_dim_series = st.number_input("dim_series", value=int(st.session_state["fine_dim_series"]), step=1, key="fine_dim_series_input")
    config["dim_series"] = int(fine_dim_series)
with c3:
    fine_epoch = st.number_input("fine_epoch", value=int(st.session_state["fine_epoch"]), step=1, key="fine_epoch_input")
    config["fine_epoch"] = int(fine_epoch)

c4, c5 = st.columns(2)
with c4:
    fine_use_decoder = st.toggle(
        "Use Decoder",
        value=bool(config.get("decoder", False)),
        key="fine_use_decoder_toggle",
    )
    config["decoder"] = bool(fine_use_decoder)
with c5:
    fine_encoder = st.selectbox(
        "Encoder",
        options=["transformer", "timemixer", "timesnet"],
        index=["transformer", "timemixer", "timesnet"].index(st.session_state["fine_encoder"])
        if st.session_state["fine_encoder"] in ["transformer", "timemixer", "timesnet"] else 0,
        key="fine_encoder_select",
    )
    config["encoder"] = fine_encoder

# JSON editor (for other fine-tuning parameters)
st.markdown("### Config JSON (other parameters)")
default_json_text = json.dumps(config, indent=2)
config_json_text = st.text_area("Edit configuration JSON", value=default_json_text, height=220, key="fine_config_json_editor")

st.markdown("---")


# =========================
# Center Start button + two black curve boxes (placeholders)
# =========================
st.markdown("<div class='center-btn'>", unsafe_allow_html=True)
start_finetune = st.button("Start fine-tuning", key="start_fine_tuning_btn", type="primary")
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


# =========================
# Run fine-tuning
# =========================
if start_finetune:
    # 1) merge JSON editor into config
    try:
        user_cfg = json.loads(config_json_text)
        config.update(user_cfg)
    except json.JSONDecodeError:
        st.error("Invalid JSON in configuration editor. Please fix it before starting.")
        st.stop()

    # 2) save fine config to fine/conf/example.json
    os.makedirs(os.path.dirname(full_config_path), exist_ok=True)
    with open(full_config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    st.success(f"Saved fine-tuning config to: {full_config_path}")

    # 3) update dataset_configs.py with FINE_SELECTED_DATASETS index (keep your original behavior)
    if (dc is not None) and (selected_index is not None):
        dataset_config_path = dc.__file__
        try:
            with open(dataset_config_path, "r", encoding="utf-8") as f:
                content = f.read()
            new_line = f"FINE_SELECTED_DATASETS = [{selected_index}]"
            new_content = re.sub(r"FINE_SELECTED_DATASETS\s*=\s*\[.*?\]", new_line, content, flags=re.DOTALL)
            with open(dataset_config_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            st.success("Updated FINE_SELECTED_DATASETS in dataset_configs.py")
        except Exception as e:
            st.error(f"Failed to update dataset_configs.py: {e}")

    # 4) run fine-tuning script
    cmd = (
        "cd fine && "
        f"export CUDA_VISIBLE_DEVICES={config.get('gpu_id', fine_gpu_id)} && "
        f"export PYTHONPATH=/data/user_jialinhan/jiemian:$PYTHONPATH && "
        f"python /data/user_jialinhan/jiemian/fine/run.py -C {config_file} && "
        "cd .."
    )
    run_shell_command(cmd, workdir="./")

    # 5) read log and plot curves INSIDE the black boxes
    log_path = os.path.join(fine_result_model_path, "fit.log")
    log_content = read_log_file_basic(log_path)
    loss_list = extract_loss_values_from_log(log_content)

    train_list = loss_list[0::2]
    valid_list = loss_list[1::2]

    if len(train_list) > 0:
        train_curve_ph.line_chart(pd.DataFrame({"loss": train_list}))
    if len(valid_list) > 0:
        eval_curve_ph.line_chart(pd.DataFrame({"loss": valid_list}))
