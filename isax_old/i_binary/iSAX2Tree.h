//
// Created by seth on 5/22/23.
//

#ifndef BSAX_ISAX2TREE_H
#define BSAX_ISAX2TREE_H

#include <vector>
#include "RootNode.h"
#include "TopKHeap.h"
#include <vector>
#include <unordered_set>
using namespace std;
namespace isax {
    class iSAX2Tree {
    private:

        void dfs(void* node, bool is_leaf);

        void DFS(const SAX *search_sax, void *node, bool is_leaf, vector<uint32_t> &leaf_ans, uint64_t &found_keys, CARD *card_now) const;

        void ApproximateSearch(TS *search_ts, ts_type* search_paa, TopKHeap &heap_, unordered_set<uint32_t> &approximate_found_nodes, FILE *file, FILE *sax_file, int ii,int search_max_num) const;

        void insert(LeafKey &leaf_key);

        void BuildTree();

    public:
        iSAX2Tree(const string &data_name, const string &output_directory) : ts_filename(
                output_directory + data_name + "_ts.bin"), sax_filename(output_directory + data_name + "_sax.bin"), index_filename(
                output_directory + data_name + "_index.bin") {}
        void build(const string &input_filename);
        void buildDisk(const string &input_filename);
        void buildLow(const string &input_filename);
        void buildFromDis();
        vector<pair<float, uint64_t>> search(TS *search_ts, int k, int ii,int search_max_num) const;
        vector<pair<float, uint64_t>> approximateSearch(TS *search_ts, int k, int ii,int search_max_num) const;
        vector<u_int64_t> ORI_count;

    private:
        RootNode *root;
        vector<LeafNode*> leaf_nodes;
        const string ts_filename;
        const string sax_filename;
        const string index_filename;

    };
}


#endif //BSAX_ISAX2TREE_H
