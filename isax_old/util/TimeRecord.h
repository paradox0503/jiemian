//
// Created by seth on 5/27/23.
//

#ifndef BSAX_TIME_RECORD_H
#define BSAX_TIME_RECORD_H

#include <ctime>
#include <sys/time.h>

double tS;
double tE;
struct timeval current_time;

struct timeval build_time_start;
double total_build_time;
struct timeval build_read_ts_time_start;
double total_build_read_ts_time;
struct timeval build_convert_sax_time_start;
double total_build_convert_sax_time;
struct timeval build_index_time_start;
double total_index_time;
struct timeval m_time_start;
double total_m_time;

struct timeval approximate_index_time_start;
double total_approximate_index_time;
struct timeval approximate_get_ans_time_start;
double total_approximate_get_ans_time;
struct timeval approximate_time_start;
double total_approximate_time;


struct timeval exact_index_time_start;
double total_exact_index_time;
struct timeval exact_get_ans_time_start;
double total_exact_get_ans_time;
struct timeval exact_time_start;
double total_exact_time;


struct timeval compute_min_dis_start;
double total_compute_min_dis;

#define BUILD_TIME_START gettimeofday(&build_time_start, NULL);
#define BUILD_TIME_END  gettimeofday(&current_time, NULL); \
                                      tS = build_time_start.tv_sec*1000000 + (build_time_start.tv_usec); \
                                      tE = current_time.tv_sec*1000000 + (current_time.tv_usec); \
                                      total_build_time += (tE - tS) / 1000;
#define BUILD_READ_TS_START gettimeofday(&build_read_ts_time_start, NULL);
#define BUILD_READ_TS_END  gettimeofday(&current_time, NULL); \
                                      tS = build_read_ts_time_start.tv_sec*1000000 + (build_read_ts_time_start.tv_usec); \
                                      tE = current_time.tv_sec*1000000 + (current_time.tv_usec); \
                                      total_build_read_ts_time += (tE - tS) / 1000;
#define BUILD_CONVERT_SAX_START gettimeofday(&build_convert_sax_time_start, NULL);
#define BUILD_CONVERT_SAX_END  gettimeofday(&current_time, NULL); \
                                      tS = build_convert_sax_time_start.tv_sec*1000000 + (build_convert_sax_time_start.tv_usec); \
                                      tE = current_time.tv_sec*1000000 + (current_time.tv_usec); \
                                      total_build_convert_sax_time += (tE - tS) / 1000;

#define BUILD_INDEX_START gettimeofday(&build_index_time_start, NULL);
#define BUILD_INDEX_END  gettimeofday(&current_time, NULL); \
                                      tS = build_index_time_start.tv_sec*1000000 + (build_index_time_start.tv_usec); \
                                      tE = current_time.tv_sec*1000000 + (current_time.tv_usec); \
                                      total_index_time += (tE - tS) / 1000;

#define BUILD_M_START gettimeofday(&m_time_start, NULL);
#define BUILD_M_END  gettimeofday(&current_time, NULL); \
                                      tS = m_time_start.tv_sec*1000000 + (m_time_start.tv_usec); \
                                      tE = current_time.tv_sec*1000000 + (current_time.tv_usec); \
                                      total_m_time += (tE - tS) / 1000;

#define APPROXIMATE_INDEX_START gettimeofday(&approximate_index_time_start, NULL);
#define APPROXIMATE_INDEX_END  gettimeofday(&current_time, NULL); \
                                      tS = approximate_index_time_start.tv_sec*1000000 + (approximate_index_time_start.tv_usec); \
                                      tE = current_time.tv_sec*1000000 + (current_time.tv_usec); \
                                      total_approximate_index_time += (tE - tS) / 1000;

#define APPROXIMATE_GET_ANS_START gettimeofday(&approximate_get_ans_time_start, NULL);
#define APPROXIMATE_GET_ANS_END  gettimeofday(&current_time, NULL); \
                                      tS = approximate_get_ans_time_start.tv_sec*1000000 + (approximate_get_ans_time_start.tv_usec); \
                                      tE = current_time.tv_sec*1000000 + (current_time.tv_usec); \
                                      total_approximate_get_ans_time += (tE - tS) / 1000;

#define APPROXIMATE_TIME_START gettimeofday(&approximate_time_start, NULL);
#define APPROXIMATE_TIME_END  gettimeofday(&current_time, NULL); \
                                      tS = approximate_time_start.tv_sec*1000000 + (approximate_time_start.tv_usec); \
                                      tE = current_time.tv_sec*1000000 + (current_time.tv_usec); \
                                      total_approximate_time += (tE - tS) / 1000;


#define EXACT_INDEX_START gettimeofday(&exact_index_time_start, NULL);
#define EXACT_INDEX_END  gettimeofday(&current_time, NULL); \
                                      tS = exact_index_time_start.tv_sec*1000000 + (exact_index_time_start.tv_usec); \
                                      tE = current_time.tv_sec*1000000 + (current_time.tv_usec); \
                                      total_exact_index_time += (tE - tS) / 1000;

#define EXACT_GET_ANS_START gettimeofday(&exact_get_ans_time_start, NULL);
#define EXACT_GET_ANS_END  gettimeofday(&current_time, NULL); \
                                      tS = exact_get_ans_time_start.tv_sec*1000000 + (exact_get_ans_time_start.tv_usec); \
                                      tE = current_time.tv_sec*1000000 + (current_time.tv_usec); \
                                      total_exact_get_ans_time += (tE - tS) / 1000;

#define EXACT_TIME_START gettimeofday(&exact_time_start, NULL);
#define EXACT_TIME_END  gettimeofday(&current_time, NULL); \
                                      tS = exact_time_start.tv_sec*1000000 + (exact_time_start.tv_usec); \
                                      tE = current_time.tv_sec*1000000 + (current_time.tv_usec); \
                                      total_exact_time += (tE - tS) / 1000;

#define COMPUTE_MIN_DIS_START gettimeofday(&compute_min_dis_start, NULL);
#define COMPUTE_MIN_DIS_END  gettimeofday(&current_time, NULL); \
                                      tS = compute_min_dis_start.tv_sec*1000000 + (compute_min_dis_start.tv_usec); \
                                      tE = current_time.tv_sec*1000000 + (current_time.tv_usec); \
                                      total_compute_min_dis += (tE - tS) / 1000;







#define PRINT_TIME printf("构建读取ts时间: %lf ms \t 构建TS转换SAX时间: %lf ms \t 构建索引时间: %lf ms \t 构建物化时间: %lf ms \t 构建总时间: %lf ms\n" \
"近似遍历索引时间: %lf ms \t 近似获取答案时间: %lf ms \t 近似总时间: %lf ms\n" \
"精确遍历索引时间: %lf ms \t 精确获取答案时间: %lf ms \t 精确总时间: %lf ms\n" \
"精确获取答案: 计算下界距离时间: %lf ms \t 访问原始时间序列时间: %lf ms\n", \
total_build_read_ts_time, total_build_convert_sax_time, total_index_time, total_m_time, total_build_time, \
total_approximate_index_time, total_approximate_get_ans_time, total_approximate_time, \
total_exact_index_time, total_exact_get_ans_time, total_exact_time, total_compute_min_dis, total_exact_get_ans_time - total_compute_min_dis);

#endif //BSAX_TIME_RECORD_H
