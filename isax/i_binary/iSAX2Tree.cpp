//
// Created by seth on 5/22/23.
//
#include <vector>
#include <algorithm>
#include <malloc.h>
#include "iSAX2Tree.h"
#include "RootNode.h"
#include "../util/TopKHeap.h"
#include "CntRecord.h"
#include "TimeRecord.h"
#include "unordered_set"
using namespace std;
//static uint64_t num1 = 0;
namespace isax {
    // int test=0;
    LeafNode* other_node;

    void iSAX2Tree::dfs(void *node, bool is_leaf) {
        if (!is_leaf) {
//            num1 ++;
            InternalNode* internal_node = (InternalNode*) node;
            dfs(internal_node->left, internal_node->is_left_leaf);
            dfs(internal_node->right, internal_node->is_right_leaf);
        }
        else {
            LeafNode* leaf_node = (LeafNode*) node;
            leaf_nodes.push_back(leaf_node);
        }
    }

    void iSAX2Tree::buildLow(const string &input_filename) {
        this->BuildTree();

        FILE * data_file = fopen(input_filename.c_str(),"r");
        if (!data_file) {
            cout << "找不到文件" << input_filename << endl;
            exit(-1);
        }

        vector<LeafKey> leaf_keys(TEST_BUILD_BATCH);
        vector<TS> ts_vec(TEST_BUILD_BATCH);
        cout<<"insert"<<endl;

        uint64_t now_read_pos = 0;
        for (int i = 0; i < (TOTAL_TS - 1) / TEST_BUILD_BATCH + 1; i++) {
            uint64_t read_batch = TEST_BUILD_BATCH;
            if (TOTAL_TS % TEST_BUILD_BATCH && i == (TOTAL_TS - 1) / TEST_BUILD_BATCH) {
                read_batch = TOTAL_TS % TEST_BUILD_BATCH;
            }
            fread(ts_vec.data(), sizeof(TS), read_batch, data_file);
            for (int j = 0; j < read_batch; j++) {
                sax_from_ts(ts_vec[j].ts, leaf_keys[j].sax_.sax);
                leaf_keys[j].p = now_read_pos++;
            }
            for (int j = 0; j < read_batch; j++) {
                insert(leaf_keys[j]);
            }
            cout<<now_read_pos<<endl;
        }


        cout<<"save index and ts"<<endl;
        // save index and ts
        FILE *index_data_file = fopen(index_filename.c_str(), "w");
        if (!index_data_file) {
            cout << "找不到文件" << index_data_file << endl;
            exit(-1);
        }
        FILE *ts_data_file = fopen(ts_filename.c_str(), "w");
        if (!ts_data_file) {
            cout << "找不到文件" << ts_filename << endl;
            exit(-1);
        }
        FILE *sax_data_file = fopen(sax_filename.c_str(), "w");
        if (!sax_data_file) {
            cout << "找不到文件" << sax_filename << endl;
            exit(-1);
        }


        dfs(root->node, root->root_is_leaf);

        fseek(data_file, 0, SEEK_SET);
        fread(ts_vec.data(), sizeof(TS), TEST_BUILD_BATCH, data_file);
        uint64_t new_p = 0;
        uint64_t file_pos = 0;
        const uint64_t store_num = 10000000;
        vector<TS> store_ts_vec(store_num);
        uint64_t tmp_ts_size = 0;

        // 一轮
        for(int i=0;i<leaf_nodes.size();i++) {
            leaf_nodes[i]->id = i;
            uint32_t node_len = leaf_nodes[i]->len;
            for(int j=0;j<node_len;j++) {
                if (leaf_nodes[i]->leaf_keys[j].p < TEST_BUILD_BATCH) {
                    store_ts_vec[tmp_ts_size] = ts_vec[leaf_nodes[i]->leaf_keys[j].p];
                }
                tmp_ts_size++;
                if (tmp_ts_size == store_num) {
                    fwrite(store_ts_vec.data(), sizeof(TS), store_num, ts_data_file);
                    tmp_ts_size = 0;
                }
            }
        }
        if(tmp_ts_size != 0) {
            fwrite(store_ts_vec.data(), sizeof(TS), tmp_ts_size, ts_data_file);
        }
        store_ts_vec = vector<TS>();
        // n 论
        for (u_int64_t kk = TEST_BUILD_BATCH; kk < TOTAL_TS; kk += TEST_BUILD_BATCH) {
            for(int j=0;j< TEST_BUILD_BATCH && kk + j < TOTAL_TS;j++) {
                fread(&ts_vec[j], sizeof(TS), 1, data_file);
            }
            cout<<kk<<endl;
            new_p = 0;
            for(int i=0;i<leaf_nodes.size();i++) {
                leaf_nodes[i]->id = i;
                uint32_t node_len = leaf_nodes[i]->len;
                for(int j=0;j<node_len;j++) {
                    if (leaf_nodes[i]->leaf_keys[i].p < kk + TEST_BUILD_BATCH && leaf_nodes[i]->leaf_keys[i].p >= kk) {
                        fseek(ts_data_file, new_p * sizeof(TS), SEEK_SET);
                        fwrite(&ts_vec[leaf_nodes[i]->leaf_keys[i].p-kk], sizeof(TS), 1, ts_data_file);
                    }
                    new_p++;
                }
            }
        }

        new_p = 0;
        file_pos = 0;
        for(int i=0;i<leaf_nodes.size();i++) {
            leaf_nodes[i]->id = i;
            uint32_t node_len = leaf_nodes[i]->len;
            leaf_nodes[i]->file_pos = file_pos;
            file_pos += node_len;
            for(int j=0;j<node_len;j++) {
//                store_ts_vec[j] = ts_vec[leaf_nodes[i]->leaf_keys[j].p];
                leaf_nodes[i]->leaf_keys[j].p = new_p++;
                fwrite(&leaf_nodes[i]->leaf_keys[j].sax_, sizeof(SAX), 1, sax_data_file);
            }
            vector<LeafKey>().swap(leaf_nodes[i]->leaf_keys);
        }
        fwrite(leaf_keys.data(), sizeof(LeafKey), TOTAL_TS, index_data_file);
        fclose(data_file);
        fclose (index_data_file);
        fclose (ts_data_file);
        fclose(sax_data_file);
    }


    void iSAX2Tree::build(const string &input_filename) {
        this->BuildTree();

        FILE * data_fileq = fopen(embed_input_filename.c_str(),"r");
        if (!data_fileq) {
            cout << "找不到文件" << embed_input_filename << endl;
            exit(-1);
        }
        vector<LeafKey> leaf_keys(TOTAL_TS);
        vector<TS_emb> ts_vecq(TOTAL_TS);
        fread(ts_vecq.data(), sizeof(TS_emb), TOTAL_TS, data_fileq);

        for (int i = 0; i < TOTAL_TS; i++) {
            sax_from_ts(ts_vecq[i].ts, leaf_keys[i].sax_.sax);
            leaf_keys[i].p = i;
            leaf_keys[i].ORI = i;
            // }
            // cout<<"insert"<<endl;
            // for (int i = 0; i < TOTAL_TS; i++) {
            if (i % 100000 == 0) cout<<i<<endl;
            // if (i == 881471 ){
            //     test=1;
            //     for(auto i: leaf_keys[i].sax_.sax){
            //         cout<< int(i)<<" ";
            //     }
            //     cout<<endl;
            // }
            insert(leaf_keys[i]);
        }

        FILE * data_file = fopen(input_filename.c_str(),"r");
        if (!data_file) {
            cout << "找不到文件input_filename" << input_filename << endl;
            exit(-1);
        }
        vector<TS> ts_vec(TOTAL_TS);
        fread(ts_vec.data(), sizeof(TS), TOTAL_TS, data_file);

        cout<<"save index and ts"<<endl;
        // save index and ts
        FILE *index_data_file = fopen(index_filename.c_str(), "w");
        if (!index_data_file) {
            cout << "找不到文件" << index_data_file << endl;
            exit(-1);
        }
        FILE *ts_data_file = fopen(ts_filename.c_str(), "w");
        if (!ts_data_file) {
            cout << "找不到文件" << ts_filename << endl;
            exit(-1);
        }
        FILE *sax_data_file = fopen(sax_filename.c_str(), "w");
        if (!sax_data_file) {
            cout << "找不到文件" << sax_filename << endl;
            exit(-1);
        }

        vector<TS> store_ts_vec(LEAF_MAX_NUM);


        dfs(root->node, root->root_is_leaf);
        uint64_t new_p = 0;
        uint64_t file_pos = 0;
        ORI_count = vector<uint64_t>(TOTAL_TS);
        for(int i=0;i<leaf_nodes.size();i++) {
            // cout<<i<<"/"<<leaf_nodes.size()<<endl;
            leaf_nodes[i]->id = i;
            uint32_t node_len = leaf_nodes[i]->len;
            leaf_nodes[i]->file_pos = file_pos;
            file_pos += node_len;
            for(int j=0;j<node_len;j++) {
                if (MEMORY_ENOUGH==0){
                    vector<TS> ets_vec(1);
                    fseek(data_file, leaf_nodes[i]->leaf_keys[j].ORI * TS_LENGTH * sizeof(ts_type), SEEK_SET);
                    fwrite(&ets_vec, sizeof(TS), 1, data_file);
                    store_ts_vec[j] = ets_vec[0];
                }
                else{
                    store_ts_vec[j] = ts_vec[leaf_nodes[i]->leaf_keys[j].ORI];
                }
                leaf_nodes[i]->leaf_keys[j].p = new_p++;
                ORI_count[leaf_nodes[i]->leaf_keys[j].p]= leaf_nodes[i]->leaf_keys[j].ORI;
                // cout<<ORI_count[leaf_nodes[i]->leaf_keys[j].p]<<endl;
                fwrite(&leaf_nodes[i]->leaf_keys[j].sax_, sizeof(SAX), 1, sax_data_file);
            }
            fwrite(store_ts_vec.data(), sizeof(TS), node_len, ts_data_file);
            vector<LeafKey>().swap(leaf_nodes[i]->leaf_keys);
        }
        fclose (data_file);
        fclose (data_fileq);
        fclose (ts_data_file);
        fclose(sax_data_file);
        // exit(1);
    }

    void iSAX2Tree::buildDisk(const string &input_filename) {
        this->BuildTree();

        FILE * data_file = fopen(input_filename.c_str(),"r");
        if (!data_file) {
            cout << "找不到文件" << input_filename << endl;
            exit(-1);
        }
        FILE *index_data_file = fopen(index_filename.c_str(), "w");
        if (!index_data_file) {
            cout << "找不到文件" << index_data_file << endl;
            exit(-1);
        }
        vector<LeafKey> leaf_keys(TEST_BUILD_BATCH);
        vector<TS> ts_vec(TEST_BUILD_BATCH);
        cout<<"insert"<<endl;

        uint64_t now_read_pos = 0;
        for (int i = 0; i < (TOTAL_TS - 1) / TEST_BUILD_BATCH + 1; i++) {
            uint64_t read_batch = TEST_BUILD_BATCH;
            if (TOTAL_TS % TEST_BUILD_BATCH && i == (TOTAL_TS - 1) / TEST_BUILD_BATCH) {
                read_batch = TOTAL_TS % TEST_BUILD_BATCH;
            }
            fread(ts_vec.data(), sizeof(TS), read_batch, data_file);
            for (int j = 0; j < read_batch; j++) {
                sax_from_ts(ts_vec[j].ts, leaf_keys[j].sax_.sax);
                leaf_keys[j].p = now_read_pos++;
            }
            for (int j = 0; j < read_batch; j++) {
                insert(leaf_keys[j]);
            }
            fwrite(leaf_keys.data(), sizeof(LeafKey), TEST_BUILD_BATCH, index_data_file);
            cout<<now_read_pos<<endl;
        }
        fclose (index_data_file);
        fclose (data_file);
        leaf_keys = vector<LeafKey>();
        cout<<"save index and ts"<<endl;
        // save index and ts
        FILE *ts_data_file = fopen(ts_filename.c_str(), "w");
        if (!ts_data_file) {
            cout << "找不到文件" << ts_filename << endl;
            exit(-1);
        }
        FILE *sax_data_file = fopen(sax_filename.c_str(), "w");
        if (!sax_data_file) {
            cout << "找不到文件" << sax_filename << endl;
            exit(-1);
        }


        dfs(root->node, root->root_is_leaf);
        uint64_t new_p = 0;
        uint64_t file_pos = 0;
        for(int i=0;i<leaf_nodes.size();i++) {
            leaf_nodes[i]->id = i;
            uint32_t node_len = leaf_nodes[i]->len;
            leaf_nodes[i]->file_pos = file_pos;
            file_pos += node_len;
            for(int j=0;j<node_len;j++) {
                fwrite(&leaf_nodes[i]->leaf_keys[j].sax_, sizeof(SAX), 1, sax_data_file);
            }
        }
        fclose(sax_data_file);

        // read ts
        data_file = fopen(input_filename.c_str(),"r");
        if (!data_file) {
            cout << "找不到文件" << input_filename << endl;
            exit(-1);
        }

        // read first batch
        fread(ts_vec.data(), sizeof(TS), TEST_BUILD_BATCH, data_file);

        vector<TS> tmp_ts(1000000);
        new_p = 0;
        uint64_t tmp_ts_size = 0;
        for(int j=0;j<leaf_nodes.size();j++) {
            auto leaf_node = leaf_nodes[j];
            for (int i=0;i<leaf_node->len;i++) {
                if (leaf_node->leaf_keys[i].p < TEST_BUILD_BATCH) {
                    tmp_ts[tmp_ts_size] = ts_vec[leaf_node->leaf_keys[i].p];
                }
                tmp_ts_size++;
                if(tmp_ts_size == 1000000) {
                    cout<<new_p<<endl;
                    fwrite(tmp_ts.data(), sizeof(TS), 1000000, ts_data_file);
                    tmp_ts_size = 0;
                }
                new_p++;
            }
        }
        fwrite(tmp_ts.data(), sizeof(TS), tmp_ts_size, ts_data_file);


        //
        for (u_int64_t kk = TEST_BUILD_BATCH; kk < TOTAL_TS; kk += TEST_BUILD_BATCH) {
            for (int j = 0; j < TEST_BUILD_BATCH && kk + j < TOTAL_TS; j++) {
                fread(ts_vec.data() + j, sizeof(TS), 1, data_file);
            }
            cout << "new_batch" << endl;
            new_p = 0;
            for(int j=0;j<leaf_nodes.size();j++) {
                auto leaf_node = leaf_nodes[j];
                for (int i=0;i<leaf_node->len;i++) {
                    if (leaf_node->leaf_keys[i].p < kk + TEST_BUILD_BATCH && leaf_node->leaf_keys[i].p >= kk) {
                        fseek(ts_data_file, new_p * TS_LENGTH * sizeof(ts_type), SEEK_SET);
                        fwrite(&ts_vec[leaf_node->leaf_keys[i].p-kk], sizeof(TS), 1, ts_data_file);
                    }
                    new_p++;
                }
            }
        }


        fclose(data_file);
        fclose(ts_data_file);
        fclose(sax_data_file);
    }

    void iSAX2Tree::buildFromDis() {
        this->BuildTree();

        FILE *index_data_file = fopen(index_filename.c_str(), "r");
        if (!index_data_file) {
            cout << "找不到文件" << index_data_file << endl;
            exit(-1);
        }
        cout<<"read sax"<<endl;
//        vector<LeafKey> leaf_keys(TOTAL_TS);
        LeafKey* leaf_keys = new LeafKey[TOTAL_TS];

        fread(leaf_keys, sizeof(LeafKey), TOTAL_TS, index_data_file);
        fclose (index_data_file);
        cout<<"insert sax"<<endl;
        for (int i = 0; i < TOTAL_TS; i++) {
            insert(leaf_keys[i]);
            if (i % 1000000 == 0) {
                cout<<i<<endl;
            }
        }
        dfs(root->node, root->root_is_leaf);


        uint64_t file_pos = 0;
        for(int i=0;i<leaf_nodes.size();i++) {
            leaf_nodes[i]->id = i;
            uint32_t node_len = leaf_nodes[i]->len;
            leaf_nodes[i]->file_pos = file_pos;
            file_pos += node_len;
            leaf_nodes[i]->del();
        }

        delete[] leaf_keys;
//        cout<<num1<<endl;
//        cout<<sizeof(InternalNode)*num1<<endl;
//        cout<<sizeof(LeafNode)*leaf_nodes.size()<<endl;
    }


    /**
     * 构建第一层
     */
    void iSAX2Tree::BuildTree() {
        root = new RootNode();
        SAX sax;
        CARD card;
        sax.set_min_value();
        card.set_min_card();
        root->node = new LeafNode(sax, card);
    }

    static LeafNode* SplitNode(LeafNode* leaf_node, void*& pre_node, bool& pre_is_root, const SAX* insert_sax) {
        int min_s = -1, min_s_bak = -1;
        float min_dis = MAXFLOAT, min_dis_bak = MAXFLOAT;

        for (int i = 0; i < SEGMENTS; i ++ ) {
            if (leaf_node->card_.card[i] >= BIT_CARDINALITY) continue;  // 该段已经不能再划分
            int mean = leaf_node->sum[i] / leaf_node->len;
            int stdev = std::sqrt((leaf_node->square_sum[i] / leaf_node->len) - mean * mean);

            float breakpoint = sax_a[leaf_node->sax_.sax[i] | (1 << (BIT_CARDINALITY - leaf_node->card_.card[i] - 1))];   // 前缀补100....，找下界

            if (min_dis_bak > dist_breakpoint_to_sax(breakpoint, mean)) {   // 记录所有方块都不包括分界线的情况
                min_dis_bak = dist_breakpoint_to_sax(breakpoint, mean);
                min_s_bak = i;
            }
            float avg_minus_var = sax_a[std::max(mean - 3 * stdev, 0)]; // 防止越界
            float avg_add_var = sax_a[std::min(mean + 3 * stdev + 1, 256)];
            if (avg_minus_var <= breakpoint && avg_add_var >= breakpoint) { // 方块包括分界线，找均值离分界线更近的
                if (min_dis > dist_breakpoint_to_sax(breakpoint, mean)) {
                    min_dis = dist_breakpoint_to_sax(breakpoint, mean);
                    min_s = i;
                }
            }
        }
        int s;
        if (min_s == -1) {
            s = min_s_bak;
        }
        else {
            s = min_s;
        }

        // 拆分节点
        CARD new_card = leaf_node->card_;
        new_card.card[s] ++ ;
        SAX left_sax = leaf_node->sax_;
        SAX right_sax = leaf_node->sax_;

        // 该节点拆分的那段，要拆分的位
        sax_type bit = (1 << (BIT_CARDINALITY - new_card.card[s]));
        right_sax.sax[s] |= bit;

        LeafNode* left_leaf_node = new LeafNode(left_sax, new_card);
        LeafNode* right_leaf_node = new LeafNode(right_sax, new_card);

        for (int i = 0; i < leaf_node->len; i ++ ) {

            if (leaf_node->leaf_keys[i].sax_.sax[s] & bit) { // 1分给右孩子
                right_leaf_node->leaf_keys.push_back(leaf_node->leaf_keys[i]);
                right_leaf_node->len ++ ;
            }
            else {  // 0分给左孩子
                left_leaf_node->leaf_keys.push_back(leaf_node->leaf_keys[i]);
                left_leaf_node->len ++ ;
            }
        }

        InternalNode* new_internal_node = new InternalNode(leaf_node->sax_, leaf_node->card_, left_leaf_node, right_leaf_node, s);
        if (pre_is_root) {  // 前一个节点是root，将root的map指向的leaf_node换成internal_node

            RootNode* root_node = (RootNode*) pre_node;
            root_node->node = new_internal_node;
            root_node->root_is_leaf = false;
        }
        else {
            InternalNode* internal_node = (InternalNode*) pre_node;
            if (internal_node->left == leaf_node) { // leaf_node是pre_node的左孩子
                internal_node->is_left_leaf = false;
                internal_node->left = new_internal_node;
            }
            else {
                internal_node->is_right_leaf = false;
                internal_node->right = new_internal_node;
            }
        }
        delete leaf_node;

        pre_node = new_internal_node;
        pre_is_root = false;
        if (insert_sax->sax[s] & bit) { // 1去右孩子
            other_node=left_leaf_node;
            return right_leaf_node;
        }
        else {  // 0去左孩子
            other_node=right_leaf_node;
            return left_leaf_node;
        }
    }

    static void insertNode(LeafKey& to_insert_leaf_key, void* pre_node, bool pre_is_root,
                    void* node, bool is_leaf, CARD* card_now) {
        if (!is_leaf) {
            InternalNode* internal_node = (InternalNode*) node;
            u_int8_t s = internal_node->split_segment;
            card_now->card[s] ++ ;

            // 该节点拆分的那段，要拆分的位是0还是1
            sax_type bit = to_insert_leaf_key.sax_.sax[s] & (1 << (BIT_CARDINALITY - card_now->card[s]));
            if (bit >> (BIT_CARDINALITY - card_now->card[s])) { // 为1去右孩子
                insertNode(to_insert_leaf_key, internal_node, false, internal_node->right, internal_node->is_right_leaf, card_now);
            }
            else {  // 为0去左孩子
                insertNode(to_insert_leaf_key, internal_node, false, internal_node->left, internal_node->is_left_leaf, card_now);
            }
        }
        else {
            LeafNode* leaf_node = (LeafNode*) node;
            int w=0;
            while (leaf_node->len >= LEAF_MAX_NUM) {
                w++;
                if (w>1)break;
                leaf_node = SplitNode(leaf_node, pre_node, pre_is_root, &to_insert_leaf_key.sax_);
            }
            // if (w==0){cout<<"skip~"<<endl;}
            // if(w>1){cout<<"dead loop!"<<endl;}
            // if(w==1){cout<<"get splt                   ***"<<endl;}
            // if(w>2){cout<<leaf_node->len<<" "<<other_node->len<<endl;}
            // 重新分裂
            if(w>1){
                int a=(leaf_node->len-other_node->len)/2;
                int num_trans=abs(a);
                if(leaf_node->len>other_node->len){
                    for(int i=0;i<num_trans;i++){
                        other_node->leaf_keys.push_back(leaf_node->leaf_keys.back());
                        other_node->len++;
                        leaf_node->leaf_keys.pop_back();
                        leaf_node->len--;
                    }
                }else{
                    for(int i=0;i<num_trans;i++){
                        leaf_node->leaf_keys.push_back(other_node->leaf_keys.back());
                        leaf_node->len++;
                        other_node->leaf_keys.pop_back();
                        other_node->len--;
                    }
                }
            }
            leaf_node->leaf_keys.push_back(to_insert_leaf_key);
            leaf_node->len ++ ;
            for (int i = 0; i < SEGMENTS; i ++ ) {
                leaf_node->sum[i] += to_insert_leaf_key.sax_.sax[i];
                leaf_node->square_sum[i] += to_insert_leaf_key.sax_.sax[i] * to_insert_leaf_key.sax_.sax[i];
            }
        }
    }


    void iSAX2Tree::insert(LeafKey &leaf_key) {
        CARD card_now;
        card_now.set_min_card();
        insertNode(leaf_key, root, true, root->node, root->root_is_leaf, &card_now);
    }

    void iSAX2Tree::DFS(const SAX* search_sax, void* node, bool is_leaf, vector<uint32_t> &leaf_ans, uint64_t &found_keys, CARD* card_now) const {
        if (!is_leaf) {
            InternalNode* internal_node = (InternalNode*) node;
            u_int8_t s = internal_node->split_segment;

    //        sax_print_bit(internal_node->sax_.sax, Segments, Bit_cardinality, card_now);

            card_now->card[s] ++ ;

            // 该节点拆分的那段，要拆分的位是0还是1
            sax_type bit = search_sax->sax[s] & (1 << (BIT_CARDINALITY - card_now->card[s]));

    //        cout << "bit: " << (int)bit << " " << (1 << (Bit_cardinality - card_now->card[s])) << " " << (bit >> (Bit_cardinality - card_now->card[s])) << endl;


            if (bit >> (BIT_CARDINALITY - card_now->card[s])) { // 为1去右孩子
                DFS(search_sax, internal_node->right, internal_node->is_right_leaf, leaf_ans, found_keys, card_now);
                if (found_keys < num_approximate_search_key) { // 不够也查左孩子
                    DFS(search_sax, internal_node->left, internal_node->is_left_leaf, leaf_ans, found_keys, card_now);
                }
            }
            else {  // 为0去左孩子
                DFS(search_sax, internal_node->left, internal_node->is_left_leaf, leaf_ans, found_keys, card_now);
                if (found_keys < num_approximate_search_key) { // 不够也查右孩子
                    DFS(search_sax, internal_node->right, internal_node->is_right_leaf, leaf_ans, found_keys, card_now);
                }
            }
        }
        else {
            LeafNode* leaf_node = (LeafNode*) node;

    //        sax_print_bit(leaf_node->sax_.sax, Segments, Bit_cardinality, card_now);
            leaf_ans.emplace_back(leaf_node->id);
            found_keys += leaf_node->len;
        }
    }

    void iSAX2Tree::ApproximateSearch(TS *search_ts, ts_type* search_paa, TopKHeap &heap_, unordered_set<uint32_t> &approximate_found_nodes, FILE *file, FILE *sax_file, int ii,int search_max_num) const {

        FILE * query_data_file_embed = fopen(embed_query_filename.c_str(), "r");
        float query_embed_vec[SEGMENTS];
        vector<TS_emb> ts_vec(1);
        fseek(query_data_file_embed, ii * sizeof(TS_emb), SEEK_SET);
        fread(ts_vec.data(), sizeof(TS_emb), 1, query_data_file_embed);

        SAX search_sax;
        sax_from_ts(ts_vec[0].ts, search_sax.sax);

        vector<uint32_t> leaf_ans;
        CARD card_now;

        uint64_t found_keys = 0;

        card_now.set_min_card();
        DFS(&search_sax, root->node, root->root_is_leaf, leaf_ans, found_keys, &card_now);

        TS tmp_ts;
        SAX tmp_sax_vec[LEAF_MAX_NUM];

        FILE * ORI_data_file_INPUT = fopen(input_filename.c_str(), "r");
        ts_type INPUT_ORI_vec[TS_LENGTH];


        for (int i = 0; i < leaf_ans.size(); i++) {
            LeafNode* node = leaf_nodes[leaf_ans[i]];
            approximate_found_nodes.insert(leaf_ans[i]);
            const uint32_t node_len = node->len;
            COUNT_EXACT_ANS(node_len)
            long offset_sax = node->file_pos * sizeof(SAX);
            fseek(sax_file, offset_sax, SEEK_SET);
            fread(tmp_sax_vec, sizeof(SAX), node_len, sax_file);

            for (int j = 0; j < node_len; j++) {
                float dis = min_dist_paa_to_sax(search_paa, tmp_sax_vec[j]);

                if (!heap_.check_approximate(dis)) continue;
                long offset = (node->file_pos + j) * sizeof(TS);
                fseek(file, offset, SEEK_SET);
                fread(tmp_ts.ts, sizeof(TS), 1, file);
                COUNT_EXACT_READ_TS(1)
                // if(count_exact_read_ts%100000==0)cout<<count_exact_read_ts<<endl;
                fseek(ORI_data_file_INPUT, ORI_count[(node->file_pos + j)] * sizeof(ts_type)*TS_LENGTH, SEEK_SET);
                fread(INPUT_ORI_vec, sizeof(float)*TS_LENGTH, 1, ORI_data_file_INPUT);
                u_int64_t index_in_the_ori_file=ORI_count[(node->file_pos + j)];
                // cout<<index_in_the_ori_file<<endl;
                u_int64_t index_in_the_build_file=(node->file_pos + j);

                float true_dis = ts_euclidean_distance(search_ts->ts, tmp_ts.ts);
                // heap_.push_ans_approximate(true_dis, node->file_pos + j);
                heap_.push_ans_approximate(true_dis, index_in_the_ori_file);
                // cout<<dis<<" " <<heap_.pq.top().first<<endl;
                if (search_max_num!=-1 && count_exact_read_ts>= search_max_num){
                    // std::cout << "COUNT_EXACT_READ_TS 已经达到 100 次，停止处理。" << std::endl;
                    return; // 直接返回，终止当前函数的执行
                }
            }
        }

    }


    vector<pair<float, uint64_t>> iSAX2Tree::search(TS *search_ts, int k, int ii,int search_max_num) const {
        vector<pair<float, uint64_t>> res(k);
        FILE *file;
        file = fopen(ts_filename.c_str(), "r");
        if (!file) {
            cout << "找不到文件" << ts_filename << endl;
            exit(-1);
        }
        FILE *sax_file;
        sax_file = fopen(sax_filename.c_str(), "r");
        if (!sax_file) {
            cout << "找不到文件" << sax_filename << endl;
            exit(-1);
        }
        TopKHeap heap_(k);
        unordered_set<uint32_t> approximate_found_nodes;
        ts_type search_paa[SEGMENTS];

        FILE * query_data_file_embed = fopen(embed_query_filename.c_str(), "r");
        float query_embed_vec[SEGMENTS];
        vector<TS_emb> ts_vec(1);
        fseek(query_data_file_embed, ii * sizeof(TS_emb), SEEK_SET);
        fread(ts_vec.data(), sizeof(TS_emb), 1, query_data_file_embed);

        // paa_from_ts(search_ts->ts, search_paa);
        paa_from_ts(ts_vec[0].ts, search_paa);

        //近似
        ApproximateSearch(search_ts, search_paa, heap_, approximate_found_nodes, file, sax_file,ii,-1);

        cout<<"bsf ans: "<<heap_.pq.top().first<<endl;
        TS tmp_ts;
        SAX tmp_sax_vec[LEAF_MAX_NUM];
        //顺序跳表扫描
        vector<pair<float, LeafNode*>> search_node_vec;
        for(int i=0;i<leaf_nodes.size();i++) {
            if (approximate_found_nodes.count(i)) continue;
            search_node_vec.emplace_back(min_dist_paa_to_isax(search_paa, leaf_nodes[i]->sax_, leaf_nodes[i]->card_), leaf_nodes[i]);
        }
        sort(search_node_vec.begin(), search_node_vec.end());
        FILE* ori_file;
        ori_file=fopen(input_filename.c_str(), "r");

        for(int i=0;i<search_node_vec.size();i++) {
            if (approximate_found_nodes.count(i)) continue;
            if (search_node_vec[i].first >= heap_.pq.top().first) continue;
            uint32_t node_len = search_node_vec[i].second->len;
            COUNT_EXACT_ANS(node_len)

            long offset_sax = search_node_vec[i].second->file_pos * sizeof(SAX);
            fseek(sax_file, offset_sax, SEEK_SET);
            fread(tmp_sax_vec, sizeof(SAX), node_len, sax_file);

            for(int j=0;j<node_len;j++) {

                float dis = min_dist_paa_to_sax(search_paa, tmp_sax_vec[j]);
                if (heap_.check_exact(dis)) {
                    fseek(file, (search_node_vec[i].second->file_pos + j) * sizeof(TS), SEEK_SET);
                    fread(tmp_ts.ts, sizeof(TS), 1, file);
                    COUNT_EXACT_READ_TS(1)
                    float true_dis = ts_euclidean_distance(search_ts->ts, tmp_ts.ts);
                    heap_.push_ans_exact(true_dis, search_node_vec[i].second->file_pos + j);
                }
                if (search_max_num!=-1 && count_exact_read_ts>= search_max_num){

                    // std::cout << "COUNT_EXACT_READ_TS 已经达到 100 次，停止处理。" << std::endl;
                    fclose(sax_file);
                    fclose(file);
                    for(int mm=0;mm<k;mm++) {
                        res[mm] = heap_.pq.top();
                        heap_.pq.pop();
                    }
                    sort(res.begin(), res.end());
                    return res;

                }
            }
        }
        fclose(sax_file);
        fclose(file);
        for(int i=0;i<k;i++) {
            res[i] = heap_.pq.top();
            heap_.pq.pop();
        }
        sort(res.begin(), res.end());

        return res;
    }

    vector<pair<float, uint64_t>> iSAX2Tree::approximateSearch(TS *search_ts, int k, int ii,int search_max_num) const {
        vector<pair<float, uint64_t>> res(k);
        FILE *file;
        file = fopen(ts_filename.c_str(), "r");
        if (!file) {
            cout << "找不到文件" << ts_filename << endl;
            exit(-1);
        }
        FILE *sax_file;
        sax_file = fopen(sax_filename.c_str(), "r");
        if (!sax_file) {
            cout << "找不到文件" << sax_filename << endl;
            exit(-1);
        }
        TopKHeap heap_(k);
        unordered_set<uint32_t> approximate_found_nodes;
        ts_type search_paa[SEGMENTS];
        paa_from_ts(search_ts->ts, search_paa);

        //近似
        ApproximateSearch(search_ts, search_paa, heap_, approximate_found_nodes, file, sax_file,ii,search_max_num);

        fclose(sax_file);
        fclose(file);
        for(int i=0;i<k;i++) {
            res[i] = heap_.pq.top();
            heap_.pq.pop();
        }
        sort(res.begin(), res.end());

        return res;
    }


}
