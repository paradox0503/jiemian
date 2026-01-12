//
// Created by seth on 5/28/23.
//

#ifndef BSAX_CNTRECORD_H
#define BSAX_CNTRECORD_H


unsigned long long int count_approximate_ans;
unsigned long long int total_count_approximate_ans = 0;
unsigned long long int count_exact_ans;
unsigned long long int total_count_exact_ans = 0;


unsigned long long int count_node_compute_min_dis;
unsigned long long int total_count_node_compute_min_dis = 0;

unsigned long long int count_approximate_read_ts;
unsigned long long int total_count_approximate_read_ts = 0;
unsigned long long int count_exact_read_ts;
unsigned long long int total_exact_count_read_ts = 0;


unsigned long long int nodes_number;

#define COUNT_NODES(cnt)  nodes_number += cnt;
#define PRINT_NODES printf("node数量: %lld\n", nodes_number);

// sum
#define COUNT_APPROXIMATE_ANS(cnt)  count_approximate_ans += cnt, total_count_approximate_ans += cnt;
#define COUNT_EXACT_ANS(cnt)  count_exact_ans += cnt, total_count_exact_ans += cnt;

// sketch
#define COUNT_NODE_COMPUTE_MIN_DIS(cnt)  count_node_compute_min_dis += cnt, total_count_node_compute_min_dis += cnt;

#define COUNT_APPROXIMATE_READ_TS(cnt)  count_approximate_read_ts += cnt, total_count_approximate_read_ts += cnt;
#define COUNT_EXACT_READ_TS(cnt)  count_exact_read_ts += cnt, total_exact_count_read_ts += cnt;


#define COUNT_CLEAR count_approximate_ans = 0, count_exact_ans = 0, count_node_compute_min_dis = 0, count_approximate_read_ts = 0, count_exact_read_ts = 0;

#define PRINT_COUNT printf("近似索引结果个数(摘要计算下界距离个数):%llu \t 精确索引结果个数(摘要计算下界距离个数):%llu\n\
精确presentation计算下界距离次数:%llu\n\
近似读取原始时间序列个数:%llu \t 精确读取原始时间序列个数:%llu\n\n",             \
count_approximate_ans, count_exact_ans,  \
count_node_compute_min_dis, \
count_approximate_read_ts, count_exact_read_ts);


#define PRINT_AVG_COUNT printf("近似索引结果个数(摘要计算下界距离次数)与总数量比值:%lf \t 精确索引结果个数(摘要计算下界距离次数)个数与总数量比值:%lf\n\
精确presentation计算下界距离平均次数:%lf\n\
近似读取原始时间序列平均个数:%lf \t 精确读取原始时间序列平均个数:%lf\n\n",             \
(double)total_count_approximate_ans/ ((u_int64_t)NUM_SEARCH * TOTAL_TS), (double)total_count_exact_ans/ ((u_int64_t)NUM_SEARCH * TOTAL_TS), \
(double)total_count_node_compute_min_dis / ((u_int64_t)NUM_SEARCH * TOTAL_TS), \
(double)total_count_approximate_read_ts / ((u_int64_t)NUM_SEARCH * TOTAL_TS), (double)total_exact_count_read_ts / ((u_int64_t)NUM_SEARCH * TOTAL_TS));

#endif //BSAX_CNTRECORD_H
