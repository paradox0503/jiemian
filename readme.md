# 1.pretrain
在终端打开/data/user_jialinhan/jiemian/pretrain文件夹
nvidia-smi
conda activate jlh
export CUDA_VISIBLE_DEVICES=id
python run.py -C conf/example.json
# 2.fine
在终端打开/data/user_jialinhan/jiemian/fine文件夹
conda activate jlh
export CUDA_VISIBLE_DEVICES=id
python run.py -C conf/example.json
# 3.search(isax)
在终端打开/data/user_jialinhan/jiemian/isax/build
/home/liangzhiyu/miniconda3/bin/cmake ..
make
-选择./approx_isax
-选择./exact_isax

conda activate jlh
streamlit run home.py --server.port 8502

git remote -v
git branch