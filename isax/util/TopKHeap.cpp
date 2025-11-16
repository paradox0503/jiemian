//
// Created by seth on 5/21/23.
//

#include "TopKHeap.h"




void TopKHeap::push_ans_approximate(float dis, u_int64_t p) {
    if (pq.size() < k) {
        pq.push({dis, p});
    }
    else {
        if (pq.top().first >= dis) {
//            TS * old_ts = pq.top().second;
            pq.pop();
            pq.push({dis, p});
        }
    }
}



void TopKHeap::push_ans_exact(float dis, u_int64_t p) {

    if (pq.top().first >= dis) {
//            TS * old_ts = pq.top().second;
        pq.pop();
        pq.push({dis, p});
    }
}

/**
 * 是否需要查找ts
 * 对于近似查询，小于k个直接放进堆内；大于k个时跟堆顶比较，比堆顶小才直接放入堆内
 * @param dis
 * @return
 */
bool TopKHeap::check_approximate(float dis) const {
    if (pq.size() < k) {
        return true;
    }
    else {
        return pq.top().first >= dis;
    }
}

// false 要检查ts
bool TopKHeap::check_exact(float dis) const {
    if (dis <= pq.top().first) return true;
    return false;
}
