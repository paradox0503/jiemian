//
// Created by seth on 5/22/23.
//

#ifndef BSAX_ROOTNODE_H
#define BSAX_ROOTNODE_H

#include "InternalNode.h"

namespace isax {
    class RootNode {
    public:
        void *node;
        bool root_is_leaf = true;

    };
}

#endif //BSAX_ROOTNODE_H
