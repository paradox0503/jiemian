//
// Created by seth on 5/21/23.
//

#ifndef BSAX_TOPKHEAP_H
#define BSAX_TOPKHEAP_H

#include <vector>
#include <queue>
#include "globals.h"
using namespace std;

class TopKHeap {
public:
    TopKHeap(int _k): k(_k) {}

    bool check_approximate(float dis) const;
    bool check_exact(float dis) const;
    void push_ans_approximate(float dis, u_int64_t p);
    void push_ans_exact(float dis, u_int64_t p);

    int k;
    priority_queue<pair<float, uint64_t>, vector<pair<float, uint64_t>>> pq;

};


#endif //BSAX_TOPKHEAP_H
