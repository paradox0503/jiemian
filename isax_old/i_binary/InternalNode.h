//
// Created by seth on 5/22/23.
//

#ifndef BSAX_INTERNALNODE_H
#define BSAX_INTERNALNODE_H

#include "LeafNode.h"
#include "sax.h"
namespace isax {
    class InternalNode {
    public:
        InternalNode(SAX _sax, CARD _card, LeafNode *_left, LeafNode *_right, u_int8_t _sp) : sax_(_sax), card_(_card),
                                                                                              left(_left),
                                                                                              right(_right),
                                                                                              split_segment(_sp),
                                                                                              is_left_leaf(true),
                                                                                              is_right_leaf(true) {}

        void *left;
        void *right;
        SAX sax_;
        CARD card_;
        u_int8_t split_segment; // 选择的是哪个段进行分裂

        bool is_left_leaf;   // 指向的节点是否是叶子
        bool is_right_leaf;   // 指向的节点是否是叶子
    };
}

#endif //BSAX_INTERNALNODE_H
