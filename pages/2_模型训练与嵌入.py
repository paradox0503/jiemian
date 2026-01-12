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

# 侧边栏模式选择
with st.sidebar:
    st.markdown("### 选择模式")
    mode = st.selectbox(
        "选择",
        ["预训练", "微调"],# , "嵌入"
        key="mode_select"
    )

# 主内容区 - 按模式渲染
if mode == "预训练":
    if dc is None:
        st.error("数据集配置模块加载失败，无法使用预训练功能！")
    else:
        with st.container():
            st.subheader("预训练配置")
            config_file = "conf/example.json"
            full_config_path = os.path.abspath(os.path.join("pretrain", config_file))

            # 加载配置文件
            if os.path.exists(full_config_path):
                try:
                    with open(full_config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                except json.JSONDecodeError:
                    st.warning(f"配置文件 {full_config_path} 无效，使用默认配置")
                    config = {}
            else:
                config = {}

            # 设置模型输出路径（转为绝对路径）
            result_model_path = os.path.abspath(f"./app/pretrain/pretrain_{datetime.now().strftime('%Y%m%d_%H%M%S')}/")
            config["output_path"] = result_model_path
            config["result_path"] = result_model_path

            # st.write(f"保存路径设置为: {result_model_path}")

            col1, col2, col3 = st.columns(3)
            with col1:
                # GPU ID配置
                train_gpu_id = st.text_input("GPU ID", value=config.get("gpu_id", "0"), key="train_gpu_id")
                config["gpu_id"] = train_gpu_id
            with col2:
                # 模型选择
                model_options = ["transformer", "timemixer", "timesnet"]
                selected_model = st.selectbox(
                    "选择模型",
                    options=model_options,
                    index=model_options.index(config.get("encoder", "transformer")) if config.get("encoder") in model_options else 0,
                    key="model_select"
                )
                config["encoder"] = selected_model
            with col3:
                # Decoder配置
                use_decoder = st.toggle(
                    "是否使用 Decoder",
                    value=config.get("decoder", False),  # 键名改为decoder，匹配JSON中的"decoder": false
                    key="use_decoder_toggle"
                )
                # 将切换结果赋值给config["decoder"]（键名一致）
                config["decoder"] = use_decoder

                # 课程学习配置
                use_curriculum_learning = st.toggle("是否使用课程学习", value=config.get("use_curriculum_learning", False), key="use_curriculum_learning_toggle")
                config["use_curriculum_learning"] = use_curriculum_learning
                # 如果用户选择课程学习，显示提示信息
                if use_curriculum_learning:
                    st.info("课程学习需要用户自行将数据集排序")

            st.markdown("---")
            st.markdown("### 数据集管理")
            # 已有数据集选择（使用Session State中的实时列表）
            dataset_names = st.session_state["all_dataset_names"]
            valid_indices = [i for i in dc.SELECTED_DATASETS if isinstance(i, int) and 0 <= i < len(dc.DATASET_CONFIGS)]
            default_selected = [dc.DATASET_CONFIGS[i].name for i in valid_indices if i < len(dc.DATASET_CONFIGS)]
            selected_datasets = st.multiselect("选择训练数据集", options=dataset_names, default=default_selected, key="selected_datasets")
            selected_indices = [dataset_names.index(name) for name in selected_datasets if name in dataset_names]

            col1, col2 = st.columns(2)
            with col1:
            # 新增数据集面板
                with st.expander("添加新数据集", expanded=False):
                    # -------------------------- 数据集名称选择（限定DATA_ROOT内文件） --------------------------
                    name_options = [""]  # 初始化名称选项（空值为默认）
                    name_to_paths = {}   # 映射：名称 → (dataset绝对路径, query绝对路径)

                    # 遍历限定的DATA_ROOT文件夹，提取xxx_dataset.bin/xxx_query.bin前缀
                    all_files = [f for f in os.listdir(DATA_ROOT) if os.path.isfile(os.path.join(DATA_ROOT, f))]
                    dataset_files = [f for f in all_files if f.endswith("_dataset.bin")]
                    query_files = [f for f in all_files if f.endswith("_query.bin")]

                    # 提取所有前缀名并建立绝对路径映射
                    prefix_set = set()
                    dataset_path_map = {}
                    query_path_map = {}

                    # 处理dataset文件（直接拼接绝对路径）
                    for f in dataset_files:
                        prefix = f.replace("_dataset.bin", "")
                        prefix_set.add(prefix)
                        dataset_path_map[prefix] = os.path.join(DATA_ROOT, f)  # 绝对路径拼接
                    # 处理query文件（直接拼接绝对路径）
                    for f in query_files:
                        prefix = f.replace("_query.bin", "")
                        prefix_set.add(prefix)
                        query_path_map[prefix] = os.path.join(DATA_ROOT, f)  # 绝对路径拼接

                    # 构建名称选项和路径映射
                    name_options = sorted(list(prefix_set))
                    for name in name_options:
                        dataset_path = dataset_path_map.get(name, "")
                        query_path = query_path_map.get(name, "")
                        name_to_paths[name] = (dataset_path, query_path)

                    # 数据集名称选择框
                    selected_name = st.selectbox(
                        "数据集名称（仅显示./app/data内bin文件前缀）",
                        options=[""] + name_options,
                        key="new_dataset_name_select",
                        # 选择名称后自动填充绝对路径到Session State
                        on_change=lambda: st.session_state.update({
                            "dataset_name_selected": st.session_state["new_dataset_name_select"],
                            "dataset_path_selected": name_to_paths.get(st.session_state["new_dataset_name_select"], ("", ""))[0],
                            "query_path_selected": name_to_paths.get(st.session_state["new_dataset_name_select"], ("", ""))[1]
                        })
                    )

                    # 手动输入名称逻辑
                    if selected_name == "":
                        manual_name = st.text_input("手动输入数据集名称", key="manual_dataset_name")
                        final_name = manual_name
                    else:
                        final_name = selected_name
                        st.session_state["dataset_name_selected"] = final_name

                    # -------------------------- 仅保留下拉框选择路径（核心修复：绝对路径） --------------------------
                    # 获取DATA_ROOT内的所有.bin文件（仅保留纯文件名，用于下拉框显示）
                    bin_files = glob.glob(os.path.join(DATA_ROOT, "*.bin"))
                    bin_file_names = [os.path.basename(f) for f in bin_files]  # 纯文件名（如 two_dataset.bin）

                    # 映射：纯文件名 → 绝对路径（关键修复：避免路径嵌套）
                    bin_file_map = {os.path.basename(f): os.path.abspath(f) for f in bin_files}

                    # 筛选出dataset和query类型的文件（用于下拉框分类）
                    dataset_bin_files = [f for f in bin_file_names if f.endswith("_dataset.bin")]
                    query_bin_files = [f for f in bin_file_names if f.endswith("_query.bin")]

                    st.markdown("---")
                    # ========== 数据集路径：仅下拉选择（绝对路径） ==========
                    st.markdown("**数据集文件选择（仅可选择./app/data内的_dataset.bin文件）**")
                    # 自动选中名称对应的dataset文件（如果存在）
                    default_dataset_idx = 0
                    if st.session_state["dataset_path_selected"]:
                        selected_dataset_filename = os.path.basename(st.session_state["dataset_path_selected"])
                        if selected_dataset_filename in dataset_bin_files:
                            default_dataset_idx = dataset_bin_files.index(selected_dataset_filename) + 1  # +1 因为第一个选项是空值

                    dataset_file_selector = st.selectbox(
                        "选择数据集文件（xxx_dataset.bin）",
                        options=[""] + dataset_bin_files,  # 仅显示纯文件名
                        key="dataset_file_selector",
                        index=default_dataset_idx
                    )
                    # 更新路径状态（直接取绝对路径）
                    if dataset_file_selector != "":
                        dataset_path = bin_file_map[dataset_file_selector]  # 绝对路径
                        st.session_state["dataset_path_selected"] = dataset_path
                    else:
                        dataset_path = ""

                    st.markdown("---")
                    # ========== 查询集路径：仅下拉选择（绝对路径） ==========
                    st.markdown("**查询集文件选择（仅可选择./app/data内的_query.bin文件）**")
                    # 自动选中名称对应的query文件（如果存在）
                    default_query_idx = 0
                    if st.session_state["query_path_selected"]:
                        selected_query_filename = os.path.basename(st.session_state["query_path_selected"])
                        if selected_query_filename in query_bin_files:
                            default_query_idx = query_bin_files.index(selected_query_filename) + 1  # +1 因为第一个选项是空值

                    query_file_selector = st.selectbox(
                        "选择查询集文件（xxx_query.bin）",
                        options=[""] + query_bin_files,  # 仅显示纯文件名
                        key="query_file_selector",
                        index=default_query_idx
                    )
                    # 更新路径状态（直接取绝对路径）
                    if query_file_selector != "":
                        query_path = bin_file_map[query_file_selector]  # 绝对路径
                        st.session_state["query_path_selected"] = query_path
                    else:
                        query_path = ""

                    # 其他配置项
                    new_size_query = st.number_input("查询集大小", value=1000, key="new_size_query")
                    new_dim_seq = st.number_input("序列维度", value=256, key="new_dim_seq")

                    # 新增数据集按钮逻辑（写入绝对路径）
                    if st.button("添加新数据集", key="add_new_dataset", use_container_width=True):
                        if not final_name:
                            st.error("请填写/选择数据集名称！")
                        elif not dataset_path:
                            st.error("请选择数据集文件（xxx_dataset.bin）！")
                        else:
                            # 路径校验（绝对路径直接校验）
                            if not dataset_path.startswith(DATA_ROOT):
                                st.error(f"数据集路径必须在 {DATA_ROOT} 目录下！")
                            elif query_path and not query_path.startswith(DATA_ROOT):
                                st.error(f"查询集路径必须在 {DATA_ROOT} 目录下！")
                            else:
                                dataset_config_path = dc.__file__
                                try:
                                    # 单次读取配置文件
                                    with open(dataset_config_path, 'r', encoding='utf-8') as f:
                                        content = f.read()

                                    # -------------------------- 1. 修改DatasetConfig（写入绝对路径） --------------------------
                                    import re
                                    # 查找最大index_name
                                    indices = re.findall(r'index_name=\s*(\d+)', content)
                                    max_index = max([int(i) for i in indices]) if indices else -1
                                    new_index = max_index + 1

                                    # 构建新的DatasetConfig行（填充绝对路径）
                                    new_config_line = (
                                        f'    DatasetConfig("{final_name}", "{dataset_path}", {new_dim_seq}, '
                                        f'size_train=conf_size_train, size_val=conf_size_val, size_db=conf_size_db, index_name={new_index})'
                                    )

                                    # 插入到DATASET_CONFIGS列表末尾
                                    marker = "]# DATASET_CONFIGS"
                                    insert_pos = content.rfind(marker)
                                    if insert_pos != -1:
                                        before = content[:insert_pos].rstrip()
                                        after = content[insert_pos:]
                                        if not before.endswith(","):
                                            before += ","
                                        content = before + "\n" + new_config_line + "\n" + after  # 更新content变量

                                    # -------------------------- 2. 修改EmbedConfig（写入绝对路径） --------------------------
                                    # 查找最大query_index_name
                                    query_indices = re.findall(r'query_index_name=\s*(\d+)', content)
                                    max_query_index = max([int(i) for i in query_indices]) if query_indices else -1
                                    new_query_index = max_query_index + 1

                                    # 构建新的EmbedConfig行（填充绝对路径）
                                    new_embed_line = (
                                        f'    EmbedConfig("{final_name}", "{dataset_path}", "{query_path}", "{new_dim_seq}", '
                                        f'"{new_size_query}", query_index_name={new_query_index})'
                                    )

                                    # 插入到embed_CONFIGS列表末尾
                                    embed_marker = "]# embed_CONFIGS"
                                    embed_insert_pos = content.rfind(embed_marker)
                                    if embed_insert_pos != -1:
                                        before_embed = content[:embed_insert_pos].rstrip()
                                        after_embed = content[embed_insert_pos:]
                                        if not before_embed.endswith(","):
                                            before_embed += ","
                                        content = before_embed + "\n" + new_embed_line + "\n" + after_embed  # 再次更新content

                                    # 单次写入文件（保存绝对路径）
                                    with open(dataset_config_path, 'w', encoding='utf-8') as f:
                                        f.write(content)

                                    # 更新Session State，同步数据集列表
                                    st.session_state["all_dataset_names"].append(final_name)
                                    st.success(f"新数据集 '{final_name}' 已成功添加！写入的绝对路径：{dataset_path}")

                                    # 重置状态
                                    st.session_state["dataset_name_selected"] = ""
                                    st.session_state["dataset_path_selected"] = ""
                                    st.session_state["query_path_selected"] = ""

                                except Exception as e:
                                    st.error(f"添加数据集失败：{str(e)}")
            with col2:
            # ========== 最终修复：删除数据集面板（完全移除global声明） ==========
                with st.expander("删除数据集", expanded=False):
                    st.markdown("**删除已添加的数据集**")

                    # 选择要删除的数据集
                    if st.session_state["all_dataset_names"]:
                        dataset_to_delete = st.selectbox(
                            "选择要删除的数据集",
                            options=st.session_state["all_dataset_names"],
                            key="dataset_to_delete_select",
                            # 切换数据集时自动重置确认状态
                            on_change=lambda: st.session_state.update({"delete_confirm_temp": False})
                        )

                        # 二次确认开关（绑定到临时state，避免直接修改组件state）
                        confirm_delete = st.checkbox(
                            f"确认删除数据集 '{dataset_to_delete}'",
                            key="confirm_delete_checkbox",
                            value=st.session_state["delete_confirm_temp"]
                        )
                        # 同步临时state
                        st.session_state["delete_confirm_temp"] = confirm_delete

                        if st.button("删除选中数据集", key="delete_dataset_btn", use_container_width=True):
                            if not confirm_delete:
                                st.error("请勾选确认删除选项！")
                            else:
                                dataset_config_path = dc.__file__
                                try:
                                    # 读取配置文件内容
                                    with open(dataset_config_path, 'r', encoding='utf-8') as f:
                                        content = f.read()

                                    import re
                                    # -------------------------- 1. 删除DatasetConfig配置 --------------------------
                                    # 匹配对应名称的DatasetConfig行（支持换行和空格）
                                    dataset_pattern = re.compile(
                                        rf'\s*DatasetConfig\("{re.escape(dataset_to_delete)}",.*?index_name=\d+\)',
                                        re.DOTALL
                                    )
                                    # 先找到匹配行
                                    dataset_matches = dataset_pattern.findall(content)
                                    if dataset_matches:
                                        # 删除匹配的行（包括前后的逗号）
                                        content = dataset_pattern.sub('', content)
                                        # 清理多余的逗号和空行
                                        content = re.sub(r',\s*,', ',', content)  # 连续逗号
                                        content = re.sub(r'\n\s*\n', '\n', content)  # 空行
                                        content = re.sub(r'\],\s*]', ']', content)  # 列表末尾逗号

                                    # -------------------------- 2. 删除EmbedConfig配置 --------------------------
                                    # 匹配对应名称的EmbedConfig行
                                    embed_pattern = re.compile(
                                        rf'\s*EmbedConfig\("{re.escape(dataset_to_delete)}",.*?query_index_name=\d+\)',
                                        re.DOTALL
                                    )
                                    embed_matches = embed_pattern.findall(content)
                                    if embed_matches:
                                        content = embed_pattern.sub('', content)
                                        # 清理多余的逗号和空行
                                        content = re.sub(r',\s*,', ',', content)
                                        content = re.sub(r'\n\s*\n', '\n', content)
                                        content = re.sub(r'\],\s*]', ']', content)

                                    # -------------------------- 3. 清理SELECTED_DATASETS中对应的索引 --------------------------
                                    # 找到被删除数据集的index
                                    deleted_index = None
                                    for i, ds in enumerate(dc.DATASET_CONFIGS):
                                        if ds.name == dataset_to_delete:
                                            deleted_index = i
                                            break

                                    # 如果找到索引，更新SELECTED_DATASETS
                                    if deleted_index is not None:
                                        # 匹配SELECTED_DATASETS行
                                        selected_pattern = re.compile(r'SELECTED_DATASETS\s*=\s*\[.*?\]', re.DOTALL)
                                        selected_match = selected_pattern.search(content)
                                        if selected_match:
                                            selected_content = selected_match.group()
                                            # 提取现有索引列表
                                            indices = re.findall(r'\d+', selected_content)
                                            indices = [int(i) for i in indices]
                                            # 过滤掉被删除的索引，并调整后续索引
                                            new_indices = []
                                            for idx in indices:
                                                if idx < deleted_index:
                                                    new_indices.append(idx)
                                                elif idx > deleted_index:
                                                    new_indices.append(idx - 1)  # 后续索引减1
                                            # 替换SELECTED_DATASETS内容
                                            new_selected_line = f"SELECTED_DATASETS = {new_indices}"
                                            content = selected_pattern.sub(new_selected_line, content)

                                    # 写入修改后的内容
                                    with open(dataset_config_path, 'w', encoding='utf-8') as f:
                                        f.write(content)

                                    # 更新Session State
                                    if dataset_to_delete in st.session_state["all_dataset_names"]:
                                        st.session_state["all_dataset_names"].remove(dataset_to_delete)

                                    # 核心修复：完全移除global声明，改用页面刷新来加载新配置
                                    st.success(f"数据集 '{dataset_to_delete}' 已成功删除！")

                                    # 刷新页面加载最新配置（无需手动更新dc变量）
                                    st.rerun()

                                except Exception as e:
                                    st.error(f"删除数据集失败：{str(e)}")

                        # 可选：删除对应的bin文件（谨慎操作，增加开关）
                        st.markdown("---")
                        st.markdown("**可选：删除数据集对应的文件**")
                        delete_files = st.checkbox("同时删除数据集对应的bin文件（不可逆）", key="delete_files_checkbox")

                        if delete_files and st.button("删除数据集文件", key="delete_dataset_files_btn"):
                            # 查找对应的bin文件
                            dataset_file = os.path.join(DATA_ROOT, f"{dataset_to_delete}_dataset.bin")
                            query_file = os.path.join(DATA_ROOT, f"{dataset_to_delete}_query.bin")

                            deleted_files = []
                            if os.path.exists(dataset_file):
                                os.remove(dataset_file)
                                deleted_files.append(dataset_file)
                            if os.path.exists(query_file):
                                os.remove(query_file)
                                deleted_files.append(query_file)

                            if deleted_files:
                                st.success(f"已删除文件：{', '.join(deleted_files)}")
                            else:
                                st.warning("未找到对应的bin文件，无需删除")

                    else:
                        st.info("暂无可删除的数据集")

            # 保存数据集选择
            if st.button("保存数据集选择", key="save_dataset_selection", use_container_width=True):
                dataset_config_path = dc.__file__
                try:
                    with open(dataset_config_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    # 替换SELECTED_DATASETS值
                    import re
                    new_line = f"SELECTED_DATASETS = {selected_indices}"
                    new_content = re.sub(r'SELECTED_DATASETS\s*=\s*\[.*?\]', new_line, content, flags=re.DOTALL)
                    with open(dataset_config_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    st.success(f"数据集选择已保存到 {dataset_config_path}")
                except Exception as e:
                    st.error(f"保存失败: {e}")

            st.markdown("---")
            st.markdown("### 配置预览")
            selected_keys = ['num_epoch', 'masking_ratio', 'stride', 'patch_len', 'd_model', 'nhead', 'num_encoder_layers', 'dim_feedforward', 'first_dim']
            filtered_config = {k: config.get(k, '') for k in selected_keys}
            config_json = st.text_area("配置 JSON", value=json.dumps(filtered_config, indent=2), height=150, key="train_config_json")
            # if st.button("确定", key="update_train_config", use_container_width=True):
            #     try:
            #         new_config = json.loads(config_json)
            #         config.update(new_config)
            #         os.makedirs(os.path.dirname(full_config_path), exist_ok=True)
            #         with open(full_config_path, 'w', encoding='utf-8') as f:
            #             json.dump(config, f, indent=2)
            #         st.success("配置已更新并保存到文件")
            #     except json.JSONDecodeError:
            #         st.error("无效的 JSON 格式")

            st.markdown("---")
            st.markdown("### 高级配置参数")
            # 修改滑动条为指数间隔，便于选择小的参数
            import numpy as np
            col1, col2 = st.columns(2)
            with col1:
                func_a_values = np.logspace(-5, 1, num=1000)
                func_a = st.select_slider("func_a 参数", options=func_a_values, value=1e-3)
                config["func_a"] = float(func_a)
                st.write(f"当前 func_a 值: {func_a:.5e}")
            with col2:
                func_b_values = np.logspace(-5, 1, num=1000)
                func_b = st.select_slider("func_b 参数", options=func_b_values, value=1e-3)
                config["func_b"] = float(func_b)
                st.write(f"当前 func_b 值: {func_b:.5e}")




            if st.button("开始训练", key="start_training", use_container_width=True):
                try:
                    new_config = json.loads(config_json)
                    config.update(new_config)
                    os.makedirs(os.path.dirname(full_config_path), exist_ok=True)
                    with open(full_config_path, 'w', encoding='utf-8') as f:
                        json.dump(config, f, indent=2)
                    st.success("配置已更新并保存到文件")
                except json.JSONDecodeError:
                    st.error("无效的 JSON 格式")
                cmd = (
                    "cd pretrain && "
                    f"export CUDA_VISIBLE_DEVICES={train_gpu_id} && "
                    f"python run.py -C {config_file} && "
                    "cd .."
                )
                run_shell_command(cmd, workdir="./")
                log_content=read_log_file_basic(result_model_path+"/fit.log")
                loss_list=extract_loss_values_from_log(log_content)
                print("loss_list:",loss_list)
                train_list=[]
                valid_list=[]
                for i in range(0,len(loss_list),2):
                    train_list.append(loss_list[i])
                for i in range(1,len(loss_list),2):
                    valid_list.append(loss_list[i])
                plot_basic_line_chart(train_list)
                plot_basic_line_chart(valid_list)

# 微调模式
elif mode == "微调":
    st.subheader("微调配置")
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

    # 数据集选择区域
    st.markdown("---")
    st.markdown('<div class="section-title">数据集选择</div>', unsafe_allow_html=True)

    # 获取数据集列表
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


# 然后执行脚本
    # 开始微调
    if st.button("开始微调", key="start_fine_tuning"):
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
        plot_basic_line_chart(train_list)
        plot_basic_line_chart(valid_list)




# # 嵌入模式
# elif mode == "嵌入":
#     st.subheader("嵌入配置")
#     config_file = "conf/example.json"
#     full_config_path = os.path.abspath(os.path.join("fine", config_file))
#     print("ts",full_config_path)

#     if os.path.exists(full_config_path):
#         try:
#             with open(full_config_path, 'r', encoding='utf-8') as f:
#                 config = json.load(f)
#         except json.JSONDecodeError:
#             st.warning(f"配置文件 {full_config_path} 无效，使用默认配置")
#             config = {}
#     else:
#         config = {}

#     # 初始化Session State
#     if "embed_model_path" not in st.session_state:
#         st.session_state["embed_model_path"] = config.get("pkl_file", "")
#     if "embed_gpu_id" not in st.session_state:
#         st.session_state["embed_gpu_id"] = config.get("gpu_id", "0")
#     if "embed_dim_series" not in st.session_state:
#         st.session_state["embed_dim_series"] = config.get("dim_series", 256)
#     if "embed_decoder" not in st.session_state:
#         st.session_state["embed_decoder"] = config.get("decoder", "none")
#     if "embed_encoder" not in st.session_state:
#         st.session_state["embed_encoder"] = config.get("encoder", "transformer")
#     if "embed_epoch" not in st.session_state:
#         st.session_state["embed_epoch"] = config.get("fine_epoch", 1)
#     # 微调配置项
#     embed_model_path = st.text_input("模型路径（嵌入）", value=st.session_state["embed_model_path"], key="embed_model_path_input")
#     config["pkl_file"] = embed_model_path
#     embed_gpu_id = st.text_input("NVIDIA 卡号（嵌入）", value=st.session_state["embed_gpu_id"], key="embed_gpu_id_input")
#     config["gpu_id"] = embed_gpu_id
#     embed_dim_series = st.number_input("序列维度（嵌入）", value=st.session_state["embed_dim_series"], key="embed_dim_series_input")
#     config["dim_series"] = embed_dim_series
#     # 选择 Encoder
#     embed_encoder = st.selectbox(
#         "选择 Encoder（嵌入）",
#         options=["transformer", "timemixer", "timesnet"],
#         index=["transformer", "timemixer", "timesnet"].index(st.session_state   ["embed_encoder"]) if st.session_state["embed_encoder"] in ["transformer", "timemixer", "timesnet"] else 0,
#         key="embed_encoder_select"
#     )
#     config["encoder"] = embed_encoder
#     embed_epoch = 0
#     config["embed_epoch"] = embed_epoch

#     # 数据集选择区域
#     st.markdown("---")
#     st.markdown('<div class="section-title">数据集选择</div>', unsafe_allow_html=True)

#     # 获取数据集列表
#     dataset_names = st.session_state.get("all_dataset_names", [])

#     if not dataset_names:
#         st.warning("暂无可用数据集，请先在预训练模式中添加数据集！")
#     else:
#         # 筛选有效的索引（原逻辑保留）
#         valid_indices = []
#         if dc and hasattr(dc, 'SELECTED_DATASETS') and hasattr(dc, 'DATASET_CONFIGS'):
#             valid_indices = [
#                 i for i in dc.SELECTED_DATASETS
#                 if isinstance(i, int) and 0 <= i < len(dc.DATASET_CONFIGS)
#             ]

#         # 调整默认值：单选需要单个值
#         default_selected_list = []
#         if dc and hasattr(dc, 'DATASET_CONFIGS'):
#             default_selected_list = [
#                 dc.DATASET_CONFIGS[i].name
#                 for i in valid_indices
#                 if i < len(dc.DATASET_CONFIGS)
#             ]

#         print("default_selected_list:", default_selected_list)

#         # 单选默认值：有默认列表则取第一个，否则取第一个数据集名称
#         default_selected = ""
#         if default_selected_list:
#             default_selected = default_selected_list[0]
#         elif dataset_names:
#             default_selected = dataset_names[0]

#         print("default_selected:", default_selected)




#         if "FINE_SELECTED_DATASETS" not in st.session_state:
#             st.session_state["FINE_SELECTED_DATASETS"] = default_selected

#         # 数据集单选框
#         selected_dataset = st.selectbox(
#             "选择嵌入数据集",
#             options=dataset_names,
#             index=dataset_names.index(st.session_state["FINE_SELECTED_DATASETS"])
#             if st.session_state["FINE_SELECTED_DATASETS"] in dataset_names else 0,
#             key="FINE_SELECTED_DATASETS",
#             disabled=not dataset_names,
#             help="选择用于嵌入的数据集"
#         )

#         # 计算选中的单个索引
#         selected_index = None
#         if dataset_names and selected_dataset in dataset_names:
#             selected_index = dataset_names.index(selected_dataset)
#             # 将选中的数据集索引保存到配置中
#             config["selected_dataset_index"] = selected_index

#         print("selected_index:", selected_index)
#         st.info(f"当前选中数据集：{selected_dataset} (索引：{selected_index})")

#     st.markdown('</div>', unsafe_allow_html=True)  # 关闭卡片

#     # 保存嵌入配置
#     if st.button("保存嵌入配置", key="save_embed_config"):
#         with open(full_config_path, 'w', encoding='utf-8') as f:
#             json.dump(config, f, indent=2)
#         # 同时更新dc中的FINE_SELECTED_DATASETS
#         if selected_index is not None:
#             dataset_config_path = dc.__file__
#             try:
#                 with open(dataset_config_path, 'r', encoding='utf-8') as f:
#                     content = f.read()
#                 import re
#                 new_line = f"FINE_SELECTED_DATASETS = [{selected_index}]"
#                 new_content = re.sub(r'FINE_SELECTED_DATASETS\s*=\s*\[.*?\]', new_line, content, flags=re.DOTALL)
#                 with open(dataset_config_path, 'w', encoding='utf-8') as f:
#                     f.write(new_content)
#                 st.success(f"配置已保存到 {full_config_path}，并更新了数据集配置")
#             except Exception as e:
#                 st.error(f"更新数据集配置失败: {e}")
#         else:
#             st.success(f"配置已保存到 {full_config_path}")



# # 然后执行脚本
#     # 开始微调
#     if st.button("开始微调", key="start_embed_tuning"):
#         cmd = (
#             "cd fine && "
#             f"export CUDA_VISIBLE_DEVICES={embed_gpu_id} && "
#             f"export PYTHONPATH=/data/user_jialinhan/jiemian:$PYTHONPATH && "
#             f"python /data/user_jialinhan/jiemian/fine/run.py -C {config_file} && "
#             "cd .."
#         )
#         run_shell_command(cmd, workdir="./")