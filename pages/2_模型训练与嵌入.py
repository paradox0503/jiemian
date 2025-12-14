"""
Training and Embedding Page
"""

import streamlit as st
import json
import os
import glob
from utils import ensure_workspace, run_shell_command
import pretrain.util.dataset_configs as dc

# 配置页面基础样式
st.set_page_config(page_title="模型训练与嵌入", layout="wide")
st.markdown("<h1 style='text-align: center; color: #000000;'> 模型训练与嵌入</h1>", unsafe_allow_html=True)
st.markdown("<hr style='border:1px solid #000000;'>", unsafe_allow_html=True)

# 初始化Session State（管理路径选择状态）
if "dataset_name_selected" not in st.session_state:
    st.session_state["dataset_name_selected"] = ""
if "dataset_path_selected" not in st.session_state:
    st.session_state["dataset_path_selected"] = ""
if "query_path_selected" not in st.session_state:
    st.session_state["query_path_selected"] = ""
# 新增：保存数据集名称列表，确保实时更新
if "all_dataset_names" not in st.session_state:
    st.session_state["all_dataset_names"] = [ds.name for ds in dc.DATASET_CONFIGS]

# 限定文件选择根目录（转为绝对路径，避免相对路径嵌套）
DATA_ROOT = os.path.abspath("./app/data")
# 确保目录存在
os.makedirs(DATA_ROOT, exist_ok=True)

# 侧边栏模式选择
with st.sidebar:
    st.header("选择模式")
    mode = st.selectbox("选择", ["预训练", "微调", "嵌入"], key="mode_select")

# 主内容区 - 按模式渲染
if mode == "预训练":
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
    result_model_path = os.path.abspath("./app/data/pretrain")
    config["output_path"] = result_model_path
    st.write(f"保存路径设置为: {result_model_path}")

    # GPU ID配置
    train_gpu_id = st.text_input("GPU ID", value=config.get("gpu_id", "0"), key="train_gpu_id")
    config["gpu_id"] = train_gpu_id

    # 已有数据集选择（使用Session State中的实时列表）
    dataset_names = st.session_state["all_dataset_names"]
    valid_indices = [i for i in dc.SELECTED_DATASETS if isinstance(i, int) and 0 <= i < len(dc.DATASET_CONFIGS)]
    default_selected = [dc.DATASET_CONFIGS[i].name for i in valid_indices]
    selected_datasets = st.multiselect("选择训练数据集", options=dataset_names, default=default_selected, key="selected_datasets")
    selected_indices = [dataset_names.index(name) for name in selected_datasets]

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

        # ========== 数据集路径：仅下拉选择（绝对路径） ==========
        st.markdown("#### 数据集文件选择（仅可选择./app/data内的_dataset.bin文件）")
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

        # ========== 查询集路径：仅下拉选择（绝对路径） ==========
        st.markdown("#### 查询集文件选择（仅可选择./app/data内的_query.bin文件）")
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

        # 显示当前选中的绝对路径（供用户确认）
        # if dataset_path:
        #     st.info(f"当前选中数据集绝对路径：{dataset_path}")
        # if query_path:
        #     st.info(f"当前选中查询集绝对路径：{query_path}")

        # 其他配置项
        new_size_query = st.number_input("查询集大小", value=1000, key="new_size_query")
        new_dim_seq = st.number_input("序列维度", value=256, key="new_dim_seq")

        # 新增数据集按钮逻辑（写入绝对路径）
        if st.button("添加新数据集", key="add_new_dataset"):
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

    # 保存数据集选择
    if st.button("保存数据集选择", key="save_dataset_selection"):
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

    # 模型选择
    model_options = ["transformer", "timemixer", "timesnet"]
    selected_model = st.selectbox(
        "选择模型",
        options=model_options,
        index=model_options.index(config.get("encoder", "transformer")) if config.get("encoder") in model_options else 0,
        key="model_select"
    )
    config["encoder"] = selected_model

    # Decoder配置
    use_decoder = st.toggle("是否使用 Decoder", value=config.get("use_decoder", False), key="use_decoder_toggle")
    config["use_decoder"] = use_decoder
    if use_decoder:
        with st.expander("Decoder 参数调节", expanded=True):
            decoder_param = st.slider("Decoder 参数大小", min_value=1, max_value=1000, step=1, value=config.get("decoder_param", 256), key="decoder_param_slider")
            config["decoder_param"] = decoder_param

    # 课程学习配置
    use_curriculum_learning = st.toggle("是否使用课程学习", value=config.get("use_curriculum_learning", False), key="use_curriculum_learning_toggle")
    config["use_curriculum_learning"] = use_curriculum_learning

    # 配置预览与保存
    st.write("**当前配置**")
    selected_keys = ['encoder', 'num_epoch', 'decoder_param', 'use_curriculum_learning']
    filtered_config = {k: config.get(k, '') for k in selected_keys}
    config_json = st.text_area("配置 JSON", value=json.dumps(filtered_config, indent=2), height=150, key="train_config_json")

    if st.button("确定", key="update_train_config"):
        try:
            new_config = json.loads(config_json)
            config.update(new_config)
            os.makedirs(os.path.dirname(full_config_path), exist_ok=True)
            with open(full_config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            st.success("配置已更新并保存到文件")
        except json.JSONDecodeError:
            st.error("无效的 JSON 格式")

    # 开始训练按钮
    if st.button("开始训练", key="start_training"):
        cmd = (
            "cd pretrain && "
            f"export CUDA_VISIBLE_DEVICES={train_gpu_id} && "
            f"python run.py -C {config_file} && "
            "cd .."
        )
        run_shell_command(cmd, workdir="./")

# 微调模式
elif mode == "微调":
    st.subheader("微调配置")
    config_file = "conf/example.json"
    full_config_path = os.path.abspath(os.path.join("fine", config_file))

    if os.path.exists(full_config_path):
        try:
            with open(full_config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except json.JSONDecodeError:
            st.warning(f"配置文件 {full_config_path} 无效，使用默认配置")
            config = {}
    else:
        config = {}

    # 初始化Session State
    if "fine_model_path" not in st.session_state:
        st.session_state["fine_model_path"] = config.get("pkl_file", "")
    if "fine_gpu_id" not in st.session_state:
        st.session_state["fine_gpu_id"] = config.get("gpu_id", "0")

    # 微调配置项
    fine_model_path = st.text_input("模型路径（微调）", value=st.session_state["fine_model_path"], key="fine_model_path_input")
    fine_gpu_id = st.text_input("NVIDIA 卡号（微调）", value=st.session_state["fine_gpu_id"], key="fine_gpu_id_input")
    config["pkl_file"] = fine_model_path
    config["gpu_id"] = fine_gpu_id

    # 保存微调配置
    if st.button("保存微调配置", key="save_fine_config"):
        with open(full_config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        st.success(f"配置已保存到 {full_config_path}")

    # 开始微调
    if st.button("开始微调", key="start_fine_tuning"):
        cmd = (
            "cd fine && "
            f"export CUDA_VISIBLE_DEVICES={fine_gpu_id} && "
            f"python run.py -C {config_file} && "
            "cd .."
        )
        run_shell_command(cmd, workdir="./")

# 嵌入模式
elif mode == "嵌入":
    st.subheader("嵌入配置")
    embed_model_path = st.text_input("用于嵌入的模型路径", value="", key="embed_model_path")
    embed_gpu_id = st.text_input("NVIDIA 卡号（嵌入）", value="0", key="embed_gpu_id")

    if st.button("生成 Embeddings", key="generate_embeddings"):
        output_dir = st.session_state.get('output_dir', "./")
        conf_dir = ensure_workspace(os.path.join(output_dir, "conf"))
        conf_path = os.path.join(conf_dir, "embedding.json")
        config = {
            "model_path": embed_model_path,
            "gpu_id": embed_gpu_id,
            "mode": "embed"
        }
        with open(conf_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        st.success(f"配置文件已保存：{conf_path}")

        cmd = (
            f"source ~/.bashrc && "
            f"conda activate jlh && "
            f"export CUDA_VISIBLE_DEVICES={embed_gpu_id} && "
            f"export LD_LIBRARY_PATH=/mnt/data/user_liangzhiyu/envs/jlh/lib:$LD_LIBRARY_PATH && "
            f"python isax/run.py -C {conf_path}"
        )
        run_shell_command(cmd, workdir="./")