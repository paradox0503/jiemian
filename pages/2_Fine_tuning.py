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
import time

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
# 新增：实时监控功能
# =========================
def init_fine_monitoring_state():
    """初始化fine-tuning监控状态"""
    if 'fine_train_loss_data' not in st.session_state:
        st.session_state.fine_train_loss_data = []
    if 'fine_val_loss_data' not in st.session_state:
        st.session_state.fine_val_loss_data = []
    if 'fine_log_position' not in st.session_state:
        st.session_state.fine_log_position = 0
    if 'fine_monitoring_active' not in st.session_state:
        st.session_state.fine_monitoring_active = False
    if 'fine_log_file_path' not in st.session_state:
        st.session_state.fine_log_file_path = None
    if 'fine_target_epochs' not in st.session_state:
        st.session_state.fine_target_epochs = None
    if 'fine_training_started' not in st.session_state:
        st.session_state.fine_training_started = False

def parse_fine_loss_line(line):
    """解析日志行，提取训练和验证损失"""
    # 训练损失模式: t1 loss = 0.2109
    train_match = re.search(r't(\d+)\s+loss\s*=\s*([\d.]+)', line)
    if train_match:
        return {
            'type': 'train',
            'task': int(train_match.group(1)),
            'value': float(train_match.group(2)),
            'timestamp': datetime.now()
        }

    # 验证损失模式: v1 loss = 0.1318
    val_match = re.search(r'v(\d+)\s+loss\s*=\s*([\d.]+)', line)
    if val_match:
        return {
            'type': 'val',
            'task': int(val_match.group(1)),
            'value': float(val_match.group(2)),
            'timestamp': datetime.now()
        }

    return None

def read_fine_incremental_log(file_path, last_position):
    """增量读取日志文件"""
    if not os.path.exists(file_path):
        return [], last_position

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            f.seek(last_position)
            new_content = f.read()
            new_lines = new_content.strip().split('\n') if new_content else []
            return new_lines, f.tell()
    except Exception:
        return [], last_position

def update_fine_loss_data():
    """更新损失数据"""
    if not st.session_state.fine_log_file_path:
        return False

    # 检查日志文件是否存在
    if not os.path.exists(st.session_state.fine_log_file_path):
        return False

    # 读取新的日志行
    new_lines, new_position = read_fine_incremental_log(
        st.session_state.fine_log_file_path,
        st.session_state.fine_log_position
    )

    if not new_lines:
        st.session_state.fine_log_position = new_position
        return False

    # 解析新的日志行
    for line in new_lines:
        loss_info = parse_fine_loss_line(line)
        if loss_info:
            if loss_info['type'] == 'train':
                st.session_state.fine_train_loss_data.append({
                    'epoch': len(st.session_state.fine_train_loss_data) + 1,
                    'loss': loss_info['value'],
                    'task': loss_info['task']
                })
            else:
                st.session_state.fine_val_loss_data.append({
                    'epoch': len(st.session_state.fine_val_loss_data) + 1,
                    'loss': loss_info['value'],
                    'task': loss_info['task']
                })

    st.session_state.fine_log_position = new_position
    return True

def start_fine_monitoring(log_path, target_epochs=None):
    """开始监控日志文件"""
    st.session_state.fine_log_file_path = log_path
    st.session_state.fine_log_position = 0
    st.session_state.fine_train_loss_data = []
    st.session_state.fine_val_loss_data = []
    st.session_state.fine_monitoring_active = True
    st.session_state.fine_target_epochs = target_epochs
    st.session_state.fine_training_started = True

def should_stop_fine_monitoring():
    """检查是否应该停止监控"""
    if not st.session_state.fine_target_epochs:
        return False

    # 检查验证损失点数是否达到目标epochs
    if len(st.session_state.fine_val_loss_data) >= st.session_state.fine_target_epochs:
        return True

    return False

# 初始化监控状态
init_fine_monitoring_state()


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

# fine_model_path = st.text_input(
#     "Model checkpoint path (.pkl / .pt etc.)",
#     value="app/pretrain/**/pretrain.pkl",
#     key="fine_model_path_input",
# )
fine_model_path = st.selectbox(
    "Model checkpoint path (.pkl / .pt etc.)",
    options=["app/pretrain/pretrain_20260114_183922/pretrain.pkl",
    "app/pretrain/pretrain_20260114_184259/pretrain.pkl"],
    index=0,
    key="fine_model_path_input",
)
config["pkl_file"] = "/data/user_jialinhan/jiemian/"+fine_model_path
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
# st.markdown("### Config JSON (other parameters)")
# 2) save fine config to fine/conf/example.json
if st.button("other fine-tuning parameters", key="other_fine-tuning_parameters_btn"):
    os.makedirs(os.path.dirname(full_config_path), exist_ok=True)
    with open(full_config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    default_json_text = json.dumps(config, indent=2)
    config_json_text = st.text_area("Edit configuration JSON", value=default_json_text, height=220, key="fine_config_json_editor")
    if st.button("ok", key="other_fine-tuning_parameters_btn_ok"):
        user_cfg = json.loads(config_json_text)
        config.update(user_cfg)


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
    # 1) 保存配置到文件
    os.makedirs(os.path.dirname(full_config_path), exist_ok=True)
    with open(full_config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

    # 2) 更新dataset_configs.py中的FINE_SELECTED_DATASETS
    if (dc is not None) and (selected_index is not None):
        dataset_config_path = dc.__file__
        try:
            with open(dataset_config_path, "r", encoding="utf-8") as f:
                content = f.read()
            new_line = f"FINE_SELECTED_DATASETS = [{selected_index}]"
            new_content = re.sub(r"FINE_SELECTED_DATASETS\s*=\s*\[.*?\]", new_line, content, flags=re.DOTALL)
            with open(dataset_config_path, "w", encoding="utf-8") as f:
                f.write(new_content)
        except Exception as e:
            st.error(f"Failed to update dataset_configs.py: {e}")

    # 3) 设置日志路径
    log_path = os.path.join(fine_result_model_path, "fit.log")

    # 4) 获取目标epoch数
    target_epochs = config.get("fine_epoch", fine_epoch)
    if not target_epochs:
        target_epochs = 1  # 默认值

    # 5) 开始监控日志文件
    start_fine_monitoring(log_path, target_epochs)

    # 6) 运行fine-tuning命令
    cmd = f"""
    cd fine
    export CUDA_VISIBLE_DEVICES={config.get('gpu_id', fine_gpu_id)}
    export PYTHONPATH=/data/user_jialinhan/jiemian:$PYTHONPATH
    python /data/user_jialinhan/jiemian/fine/run.py -C {config_file}
    cd ..
    """

    run_shell_command(cmd, workdir="./")

    # 7) 显示初始消息
    train_curve_ph.info(f"Fine-tuning started. Target epochs: {target_epochs}. Monitoring log file...")
    eval_curve_ph.info(f"Fine-tuning started. Target epochs: {target_epochs}. Monitoring log file...")


# =========================
# 实时更新图表
# =========================
# 如果监控已激活，更新数据并绘制图表
if st.session_state.fine_monitoring_active:
    # 更新损失数据
    data_updated = update_fine_loss_data()

    # 绘制训练损失曲线
    if st.session_state.fine_train_loss_data:
        train_df = pd.DataFrame(st.session_state.fine_train_loss_data)
        train_curve_ph.line_chart(train_df[['loss']])
    else:
        # 检查日志文件是否存在
        if (st.session_state.fine_log_file_path and
            os.path.exists(st.session_state.fine_log_file_path)):
            train_curve_ph.info("Log file exists. Waiting for training loss data...")
        else:
            train_curve_ph.info("Log file not yet generated. Waiting...")

    # 绘制验证损失曲线
    if st.session_state.fine_val_loss_data:
        val_df = pd.DataFrame(st.session_state.fine_val_loss_data)
        eval_curve_ph.line_chart(val_df[['loss']])
    else:
        # 检查日志文件是否存在
        if (st.session_state.fine_log_file_path and
            os.path.exists(st.session_state.fine_log_file_path)):
            eval_curve_ph.info("Log file exists. Waiting for validation loss data...")
        else:
            eval_curve_ph.info("Log file not yet generated. Waiting...")

    # 检查是否应该停止监控
    if should_stop_fine_monitoring():
        st.session_state.fine_monitoring_active = False
    else:
        # 设置自动刷新（10秒间隔）
        time.sleep(10)
        st.rerun()
else:
    # 显示初始状态
    if not start_finetune and not st.session_state.fine_training_started:
        train_curve_ph.info("Click 'Start fine-tuning' to begin training and monitoring.")
        eval_curve_ph.info("Click 'Start fine-tuning' to begin training and monitoring.")