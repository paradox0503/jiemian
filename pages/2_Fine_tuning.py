"""
Training and Embedding Page
"""
import pandas as pd
import streamlit as st
import json
import os
import glob
import sys
import importlib
from utils import ensure_workspace, run_shell_command
import re
from datetime import datetime

def plot_basic_line_chart(loss_list):
    """
    基本折线图绘制

    参数:
    loss_list: list - 必要参数，包含loss值的列表
    """
    st.title("📈 Loss变化趋势图")

    # 创建横坐标（1到列表长度）
    x_values = list(range(1, len(loss_list) + 1))

    # 创建DataFrame（最常用方式）
    chart_data = pd.DataFrame({
        "迭代次数": x_values,
        "Loss值": loss_list
    })

    # 使用st.line_chart绘制折线图
    # 设置索引为横坐标
    st.line_chart(chart_data.set_index("迭代次数"))

    # # 显示数据表格
    # with st.expander("📋 查看数据"):
    #     st.dataframe(chart_data)

def read_log_file_basic(file_path):
    """
    基本文件读取方法

    参数:
    file_path: str - 日志文件路径，必要参数

    返回:
    str - 文件内容字符串
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        print(f"错误: 文件 {file_path} 不存在")
        return ""
    except UnicodeDecodeError:
        # 如果utf-8失败，尝试其他编码
        with open(file_path, 'r', encoding='gbk') as file:
            content = file.read()
        return content

def extract_loss_values_from_log(log_content):
    """
    从日志内容中提取所有loss值

    参数:
    log_content: str - 日志内容字符串

    返回:
    list - 包含所有loss值的列表
    """
    # 正则表达式：匹配 "loss = " 后面的数字（包含小数点和负号）
    # pattern解释：loss\s*=\s*([-\d.]+)
    # - loss\s*=\s*: 匹配 "loss = "（允许有空格）
    # - ([-\d.]+): 捕获数字（包含负号和小数点）
    pattern = r'loss\s*=\s*([-\d.]+)'

    # 使用findall查找所有匹配
    loss_values = re.findall(pattern, log_content, re.IGNORECASE)

    # 将字符串转换为浮点数
    # 注意：nan会被转换为float('nan')，你可以选择如何处理
    loss_values_float = []
    for value in loss_values:
        try:
            if value.lower() == 'nan':
                loss_values_float.append(float('nan'))
            else:
                loss_values_float.append(float(value))
        except ValueError:
            # 如果转换失败，跳过该值
            continue

    return loss_values_float

# 基础样式
st.markdown("""
    <style>
    /* 页面背景 */
    .stApp {
        background-color: #f7f9fc;
    }

    /* 一级标题 */
    h1 {
        font-weight: 700;
    }

    /* 卡片容器 */
    .card {
        background: white;
        padding: 1.2rem;
        border-radius: 12px;
        border: 1px solid #e6eaf1;
        margin-bottom: 1rem;
    }

    /* 次级标题 */
    .section-title {
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }

    /* 危险区域 */
    .danger {
        border-left: 6px solid #ff4b4b;
        background: #fff5f5;
    }

    /* 成功区域 */
    .success {
        border-left: 6px solid #2ecc71;
        background: #f3fff7;
    }
    </style>
    """, unsafe_allow_html=True)

# 页面布局
st.markdown("<h1 style='text-align:center;'>模型训练与嵌入平台</h1>", unsafe_allow_html=True)
st.markdown("---")

# -------------------------- 核心修复：安全的模块加载函数 --------------------------
def load_dataset_config():
    """安全加载数据集配置模块，避免global声明问题"""
    # 先清除缓存
    if 'pretrain.util.dataset_configs' in sys.modules:
        del sys.modules['pretrain.util.dataset_configs']
    # 重新导入
    try:
        import pretrain.util.dataset_configs as dataset_config
        return dataset_config
    except ImportError as e:
        st.error(f"导入数据集配置模块失败：{e}")
        return None

# 首次加载配置模块
dc = load_dataset_config()

# 初始化Session State（管理路径选择状态）
if "dataset_name_selected" not in st.session_state:
    st.session_state["dataset_name_selected"] = ""
if "dataset_path_selected" not in st.session_state:
    st.session_state["dataset_path_selected"] = ""
if "query_path_selected" not in st.session_state:
    st.session_state["query_path_selected"] = ""
# 新增：保存数据集名称列表，确保实时更新
if "all_dataset_names" not in st.session_state:
    if dc and hasattr(dc, 'DATASET_CONFIGS'):
        st.session_state["all_dataset_names"] = [ds.name for ds in dc.DATASET_CONFIGS]
    else:
        st.session_state["all_dataset_names"] = []
# 新增：删除确认的临时状态（避免直接修改组件绑定的state）
if "delete_confirm_temp" not in st.session_state:
    st.session_state["delete_confirm_temp"] = False

# 限定文件选择根目录（转为绝对路径，避免相对路径嵌套）
DATA_ROOT = os.path.abspath("./app/data")
# 确保目录存在
os.makedirs(DATA_ROOT, exist_ok=True)
####---------------------------------------------------------------------------------------------
config_file = "conf/example.json"
full_config_path = os.path.abspath(os.path.join("fine", config_file))
print("ts",full_config_path)

if os.path.exists(full_config_path):
    try:
        with open(full_config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except json.JSONDecodeError:
        st.warning(f"配置文件 {full_config_path} 无效，使用默认配置")
        config = {}
else:
    config = {}

####---------------------------------------------------------------------------------------------
##数据集
# 数据集选择区域
st.markdown('<div class="section-title">数据集选择</div>', unsafe_allow_html=True)
dataset_names = st.session_state.get("all_dataset_names", [])
if not dataset_names:
    st.warning("暂无可用数据集，请先在预训练模式中添加数据集！")
else:
    # 筛选有效的索引（原逻辑保留）
    valid_indices = []
    if dc and hasattr(dc, 'SELECTED_DATASETS') and hasattr(dc, 'DATASET_CONFIGS'):
        valid_indices = [
            i for i in dc.SELECTED_DATASETS
            if isinstance(i, int) and 0 <= i < len(dc.DATASET_CONFIGS)
        ]

    # 调整默认值：单选需要单个值
    default_selected_list = []
    if dc and hasattr(dc, 'DATASET_CONFIGS'):
        default_selected_list = [
            dc.DATASET_CONFIGS[i].name
            for i in valid_indices
            if i < len(dc.DATASET_CONFIGS)
        ]

    print("default_selected_list:", default_selected_list)

    # 单选默认值：有默认列表则取第一个，否则取第一个数据集名称
    default_selected = ""
    if default_selected_list:
        default_selected = default_selected_list[0]
    elif dataset_names:
        default_selected = dataset_names[0]

    print("default_selected:", default_selected)




    if "FINE_SELECTED_DATASETS" not in st.session_state:
        st.session_state["FINE_SELECTED_DATASETS"] = default_selected

    # 数据集单选框
    selected_dataset = st.selectbox(
        "选择微调数据集",
        options=dataset_names,
        index=dataset_names.index(st.session_state["FINE_SELECTED_DATASETS"])
        if st.session_state["FINE_SELECTED_DATASETS"] in dataset_names else 0,
        key="FINE_SELECTED_DATASETS",
        disabled=not dataset_names,
        help="选择用于微调的数据集"
    )

    # 计算选中的单个索引
    selected_index = None
    if dataset_names and selected_dataset in dataset_names:
        selected_index = dataset_names.index(selected_dataset)
        # 将选中的数据集索引保存到配置中
        config["selected_dataset_index"] = selected_index

    print("selected_index:", selected_index)
    st.info(f"当前选中数据集：{selected_dataset} (索引：{selected_index})")

st.markdown('</div>', unsafe_allow_html=True)  # 关闭卡片
### -----------------------------------------------------------------------------------------------------

st.markdown("---")

####---------------------------------------------------------------------------------------------
## 微调配置
st.subheader("微调配置")
fine_result_model_path = os.path.abspath(f"./app/fine/fine_{datetime.now().strftime('%Y%m%d_%H%M%S')}/")
config["output_path"] = fine_result_model_path
config["result_path"] = fine_result_model_path
# 初始化Session State
if "fine_model_path" not in st.session_state:
    st.session_state["fine_model_path"] = config.get("pkl_file", "")
if "fine_gpu_id" not in st.session_state:
    st.session_state["fine_gpu_id"] = config.get("gpu_id", "0")
if "fine_dim_series" not in st.session_state:
    st.session_state["fine_dim_series"] = config.get("dim_series", 256)
if "fine_decoder" not in st.session_state:
    st.session_state["fine_decoder"] = config.get("decoder", "none")
if "fine_encoder" not in st.session_state:
    st.session_state["fine_encoder"] = config.get("encoder", "transformer")
if "fine_epoch" not in st.session_state:
    st.session_state["fine_epoch"] = config.get("fine_epoch", 1)

# 微调配置项
fine_model_path = st.text_input("模型路径（微调）", value=st.session_state["fine_model_path"], key="fine_model_path_input")
config["pkl_file"] = fine_model_path
fine_gpu_id = st.text_input("NVIDIA 卡号（微调）", value=st.session_state["fine_gpu_id"], key="fine_gpu_id_input")
config["gpu_id"] = fine_gpu_id
fine_dim_series = st.number_input("序列维度（微调）", value=st.session_state["fine_dim_series"], key="fine_dim_series_input")
config["dim_series"] = fine_dim_series
# 选择 使用Decoder或者不使用Decoder
            # Decoder配置
fine_use_decoder = st.toggle(
    "是否使用 Decoder（微调）",
    value=config.get("decoder", False),  # 键名改为decoder，匹配JSON中的"decoder": false
    key="fine_use_decoder_toggle"
)
# 将切换结果赋值给config["decoder"]（键名一致）
config["decoder"] = fine_use_decoder
# 选择 Encoder
fine_encoder = st.selectbox(
    "选择 Encoder（微调）",
    options=["transformer", "timemixer", "timesnet"],
    index=["transformer", "timemixer", "timesnet"].index(st.session_state   ["fine_encoder"]) if st.session_state["fine_encoder"] in ["transformer", "timemixer", "timesnet"] else 0,
    key="fine_encoder_select"
)
config["encoder"] = fine_encoder
fine_epoch = st.number_input("微调轮数", value=st.session_state["fine_epoch"], key="fine_epoch_input")
config["fine_epoch"] = fine_epoch

button=st.button("开始微调", key="start_fine_tuning", type="primary")
# 然后执行脚本
# 开始微调
curve_left, curve_right = st.columns(2)
with curve_left:
    with st.container(border=True):
        st.markdown("### Train loss curve")
        train_curve_ph = st.empty()
with curve_right:
    with st.container(border=True):
        st.markdown("### Evaluation loss curve")
        eval_curve_ph = st.empty()
if button:
    with open(full_config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    # 同时更新dc中的FINE_SELECTED_DATASETS
    if selected_index is not None:
        dataset_config_path = dc.__file__
        try:
            with open(dataset_config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            import re
            new_line = f"FINE_SELECTED_DATASETS = [{selected_index}]"
            new_content = re.sub(r'FINE_SELECTED_DATASETS\s*=\s*\[.*?\]', new_line, content, flags=re.DOTALL)
            with open(dataset_config_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            st.success(f"配置已保存到 {full_config_path}，并更新了数据集配置")
        except Exception as e:
            st.error(f"更新数据集配置失败: {e}")
    else:
        st.success(f"配置已保存到 {full_config_path}")

    cmd = (
        "cd fine && "
        f"export CUDA_VISIBLE_DEVICES={fine_gpu_id} && "
        f"export PYTHONPATH=/data/user_jialinhan/jiemian:$PYTHONPATH && "
        f"python /data/user_jialinhan/jiemian/fine/run.py -C {config_file} && "
        "cd .."
    )
    run_shell_command(cmd, workdir="./")
    log_content=read_log_file_basic(fine_result_model_path+"/fit.log")
    loss_list=extract_loss_values_from_log(log_content)
    print("loss_list:",loss_list)
    train_list=[]
    valid_list=[]
    for i in range(0,len(loss_list),2):
        train_list.append(loss_list[i])
    for i in range(1,len(loss_list),2):
        valid_list.append(loss_list[i])
    if len(train_list) > 0:
        train_curve_ph.line_chart(pd.DataFrame({"loss": train_list}))
    if len(valid_list) > 0:
        eval_curve_ph.line_chart(pd.DataFrame({"loss": valid_list}))
    # plot_basic_line_chart(train_list)
    # plot_basic_line_chart(valid_list)


