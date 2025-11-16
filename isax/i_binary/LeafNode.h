//
// Created by seth on 5/22/23.
//

#ifndef BSAX_LEAFNODE_H
#define BSAX_LEAFNODE_H

#include "LeafKey.h"
namespace isax {
    class LeafNode {
    public:
        LeafNode(SAX sax, CARD card) : sax_(sax), card_(card), len(0) {
            sum = new uint32_t[SEGMENTS];
            square_sum = new uint32_t[SEGMENTS];
            memset(sum, 0, sizeof(uint32_t) * SEGMENTS);
            memset(square_sum, 0, sizeof(uint32_t) * SEGMENTS);
            leaf_keys.reserve(LEAF_MAX_NUM);

        }

        void del() {
            leaf_keys = std::vector<LeafKey>();
            delete[] sum;
            delete[] square_sum;
        }

        SAX sax_;
        CARD card_;
        uint32_t id;
        u_int32_t len;
        uint64_t file_pos;

//        LeafKey leaf_keys[LEAF_MAX_NUM];
        std::vector<LeafKey> leaf_keys;

        uint32_t* sum;
        uint32_t* square_sum;


    };
}

#endif //BSAX_LEAFNODE_H
