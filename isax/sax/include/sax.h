//
//  sax.h
//  isaxlib
//
//  Created by Kostas Zoumpatianos on 3/10/12.
//  Copyright 2012 University of Trento. All rights reserved.
//

#ifndef isaxlib_sax_h
#define isaxlib_sax_h

#include "config.h"
#include "globals.h"
#include "ts.h"
#include <cstring>
#include "vector"


void sax_print(sax_type *sax, int segments, int bit_cardinality, CARD *card);

void sax_print(sax_type *sax);

void sax_print(SAX sax);

void sax_print_bit(SAX sax);

void saxt_print(saxt_type *saxt);

void saxt_print(SAXT saxt);

void saxt_print_bit(SAXT saxt);

void leafkey_print(void *saxt);

void saxt_print(saxt_type *saxt, saxt_type *prefix, cod co_d);

void printbin(unsigned long long n, int size);

void serial_printbin(unsigned long long n, int size);

int compare(const void *a, const void *b);
//saxt 只有co_d个


float minidist_paa_to_saxt_simd(const float *paa, saxt_type *saxt_, cod co_d);

float dist_breakpoint_to_sax(float breakpoint, saxt_type sax_s);

float min_dist_paa_to_sax(const ts_type *paa, SAX sax_);

float min_dist_paa_to_bsax(const ts_type *paa, SAX sax_lb, SAX sax_ub);

float min_dist_paa_to_saxt(const ts_type *paa, SAXT saxt, u_int8_t card);

float min_dist_paa_to_saxt(const ts_type *paa, SAXT saxt_lb, SAXT saxt_ub);

float min_dist_paa_to_isax(const ts_type *paa, SAX isax, CARD sax_card);


void paa_from_ts(const ts_type *ts_in, ts_type *paa);

void paa_from_ts_simd(ts_type *ts_in, ts_type *paa_out);

void paa_saxt_from_ts_simd(ts_type *ts_in, saxt_type *saxt_out, ts_type *paa);

void sax_from_ts(const ts_type *ts_in, sax_type *sax_out);

void sax_from_ts_paris(ts_type *ts_in, sax_type *sax_out);

void sax_from_ts_simd(ts_type *ts_in, sax_type *sax_out);

void sax_from_paa_simd(ts_type *paa, sax_type *sax);

void sax_from_saxt(const saxt_type *saxt_in, sax_type *sax_out);

void sax_from_saxt_simd(saxt_type *saxt_in, sax_type *sax_out);

void saxt_from_ts(const ts_type *ts_in, saxt_type *saxt_out);

void saxt_from_ts_simd(ts_type *ts_in, saxt_type *saxt_out);

void saxt_from_sax(const sax_type *sax_in, saxt_type *saxt_out);

void saxt_from_sax_simd(sax_type *sax_in, saxt_type *saxt_out);



static int getRecallNum(const float real_ans, const std::vector<std::pair<float, uint64_t>> &find_ans) {
    int recall_num = 0;
    for (const auto & find_an : find_ans) {
        if (find_an.first < real_ans + 1e-4) {
            recall_num ++;
        }
    }
    return recall_num;
}


#endif
