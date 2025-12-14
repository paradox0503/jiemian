"""
Training and Embedding Tab
"""

import json
import os
import streamlit as st
from utils import ensure_workspace, run_shell_command
import pretrain.util.dataset_configs as dc


def training_and_embedding_tab() -> None:
    """Handle the training and embedding tab."""
    st.subheader("模型训练与嵌入模块")
    col1, col2, col3 = st.columns(3)

    # Training Configuration
    with col1:
        st.write("**训练配置**")
        config_file = "conf/example.json"
        full_config_path = os.path.abspath(os.path.join("pretrain", config_file))

        if os.path.exists(full_config_path):
            try:
                with open(full_config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except json.JSONDecodeError:
                st.warning(f"配置文件 {full_config_path} 无效，使用默认配置")
                config = {}
        else:
            config = {}

        use_output_dir = st.checkbox("使用输出文件夹作为保存路径", value=False, key="use_output_dir")
        if use_output_dir and 'output_dir' in st.session_state:
            result_model_path = st.session_state.output_dir
            st.write(f"保存路径设置为: {st.session_state.output_dir}")
        else:
            result_model_path = st.text_input("当前预训练模型保存路径", value=config.get("output_path", ""), key="train_output_path")
        config["output_path"] = result_model_path

        if st.button("保存训练配置", key="save_train_config"):
            os.makedirs(os.path.dirname(full_config_path), exist_ok=True)
            with open(full_config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            st.success(f"配置已保存到 {full_config_path}")

        train_gpu_id = st.text_input("GPU ID", value=config.get("gpu_id", "0"), key="train_gpu_id")
        config["gpu_id"] = train_gpu_id

        # Dataset selection - read from imported configs
        dataset_names = [ds.name for ds in dc.DATASET_CONFIGS]
        # Filter SELECTED_DATASETS to only include integers
        valid_indices = [i for i in dc.SELECTED_DATASETS if isinstance(i, int) and 0 <= i < len(dc.DATASET_CONFIGS)]
        default_selected = [dc.DATASET_CONFIGS[i].name for i in valid_indices]

        selected_datasets = st.multiselect("选择训练数据集", options=dataset_names, default=default_selected, key="selected_datasets")
        selected_indices = [dataset_names.index(name) for name in selected_datasets]
        st.write(f"选中的数据集索引: {selected_indices}")

        # Add new dataset
        with st.expander("添加新数据集"):
            new_name = st.text_input("数据集名称", key="new_dataset_name")
            new_path_db = st.text_input("数据集路径", key="new_dataset_path")
            new_dim_seq = st.number_input("序列维度", value=256, key="new_dim_seq")
            new_size_train = st.number_input("训练集大小", value=2000, key="new_size_train")
            new_size_val = st.number_input("验证集大小", value=1000, key="new_size_val")
            new_size_db = st.number_input("数据库大小", value=100000, key="new_size_db")

            if st.button("添加新数据集", key="add_new_dataset"):
                if not new_name or not new_path_db:
                    st.error("请输入数据集名称和路径")
                else:
                    dataset_config_path = dc.__file__
                    try:
                        with open(dataset_config_path, 'r', encoding='utf-8') as f:
                            content = f.read()

                        # Find max index
                        import re
                        indices = re.findall(r'index_name,\s*(\d+)', content)
                        max_index = max([int(i) for i in indices]) if indices else -1
                        new_index = max_index + 1

                        # Create new DatasetConfig line
                        new_config_line = f'    DatasetConfig("{new_name}", "{new_path_db}", {new_dim_seq}, {new_size_train}, {new_size_val}, {new_size_db}, {new_index})'

                        # Insert into DATASET_CONFIGS
                        insert_pos = content.rfind("]")
                        if insert_pos != -1:
                            before = content[:insert_pos].rstrip()
                            if not before.endswith(","):
                                before += ","
                            new_content = before + "\n" + new_config_line + "\n]"
                            with open(dataset_config_path, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                            st.success(f"新数据集 '{new_name}' 已添加到 {dataset_config_path}")
                            # Update dataset_names
                            dataset_names.append(new_name)
                        else:
                            st.error("无法找到 DATASET_CONFIGS 列表")
                    except Exception as e:
                        st.error(f"添加失败: {e}")


        if st.button("保存数据集选择", key="save_dataset_selection"):
            # Update SELECTED_DATASETS in dataset_configs.py
            dataset_config_path = dc.__file__
            try:
                with open(dataset_config_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Replace SELECTED_DATASETS = [...] with new line
                import re
                new_line = f"SELECTED_DATASETS = {selected_indices}"
                new_content = re.sub(r'SELECTED_DATASETS\s*=\s*\[.*?\]', new_line, content, flags=re.DOTALL)

                with open(dataset_config_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                st.success(f"数据集选择已保存到 {dataset_config_path}")
            except Exception as e:
                st.error(f"保存失败: {e}")

        st.write("**当前配置**")
        # 只显示选定的配置项
        selected_keys = ['num_epoch', 'encoder','decoder']
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



        if st.button("开始训练", key="start_training"):
            cmd = (
                "cd pretrain && "
                f"export CUDA_VISIBLE_DEVICES={train_gpu_id} && "
                f"python run.py -C {config_file} && "
                "cd .."
            )
            run_shell_command(cmd, workdir="./")

    # Fine-tuning Configuration
    with col2:
        st.write("**微调配置**")
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

        if "fine_model_path" not in st.session_state:
            st.session_state["fine_model_path"] = config.get("pkl_file", "")
        if "fine_gpu_id" not in st.session_state:
            st.session_state["fine_gpu_id"] = config.get("gpu_id", "0")

        fine_model_path = st.text_input("模型路径（微调）", value=st.session_state["fine_model_path"], key="fine_model_path_input")
        fine_gpu_id = st.text_input("NVIDIA 卡号（微调）", value=st.session_state["fine_gpu_id"], key="fine_gpu_id_input")

        config["pkl_file"] = fine_model_path
        config["gpu_id"] = fine_gpu_id

        if st.button("保存微调配置", key="save_fine_config"):
            with open(full_config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            st.success(f"配置已保存到 {full_config_path}")

        if st.button("开始微调", key="start_fine_tuning"):
            cmd = (
                "cd fine && "
                f"export CUDA_VISIBLE_DEVICES={fine_gpu_id} && "
                f"python run.py -C {config_file} && "
                "cd .."
            )
            run_shell_command(cmd, workdir="./")

    # Embedding Configuration
    with col3:
        st.write("**嵌入配置**")
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