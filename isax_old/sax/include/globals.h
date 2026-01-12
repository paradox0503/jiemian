//
//  defines.h
//  isaxlib
//
//  Created by Kostas Zoumpatianos on 3/19/12.
//  Copyright 2012 University of Trento. All rights reserved.
//



#include "bitset"
#include "config.h"
#include "iostream"
#include <cassert>
#include "cstring"
#include "sax_bsearch.h"
#include "immintrin.h"
#ifndef isax_globals_h
#define isax_globals_h

#define TEST_BUILD_BATCH 100000

#define CARDINALITY 256

#define BIT_CARDINALITY 8

#if BIT_CARDINALITY == 8
typedef unsigned char sax_type;
#elif BIT_CARDINALITY == 32
typedef float sax_type;
#elif BIT_CARDINALITY == 64
typedef double sax_type;
#else
#error "Unsupported BIT_CARDINALITY value"
#endif

#define LEAF_MAX_NUM 50000
#define dataset_type 29
#define recall_if_true 0
// 29 : astro
// 30 : deep1b
// 31 : F5
// 32 : F10
// 33 : origin
// 34 : sald
// 35 ：seismic




static const std::string embed_input_directory = "/data/user_jialinhan/SEAnet-main-yuanban/seanet-2w/";
static const std::string embed_query_directory = "/data/user_jialinhan/SEAnet-main-yuanban/seanet-2w/";
#define MULTIPLY_RATIO 1



#define K 10  // 查询的k

#define INDEX_FROM 1  // 1:在原始数据集中的索引位置; 0:在构建新的数据集索引时的索引位置;
#define MEMORY_ENOUGH 1  // 1:表明内存充盈; 0:表明内存不足;

// #define LEAF_MAX_NUM 4000

// #define LEAF_MAX_NUM 4000

#define NUM_PER_SEGMENT ((TS_LENGTH - 1) / SEGMENTS + 1)    // ts_length / segments
#if dataset_type == 3 || dataset_type == 4 || dataset_type == 5 || dataset_type == 7 || dataset_type == 8
#define num_approximate_search_nodes 3
// b+树近似查询返回节点个数
#else
//#define num_approximate_search_nodes 3
#define num_approximate_search_nodes 200 // b+树近似查询返回节点个数
#endif
#if recall_if_true==1
  #define NUM_SEARCH 100
#else
  #if dataset_type==29
    #define NUM_SEARCH 100 // 查询的个数
  #else
    #define NUM_SEARCH 1000 // 查询的个数
  #endif
#endif
#if dataset_type >= 25
#define SEGMENTS 16
#elif dataset_type > 20
#define SEGMENTS 16
#elif dataset_type == 20
#define SEGMENTS 5
//段数为16，为8变为char
#elif dataset_type == 17
#define SEGMENTS 30
#elif dataset_type == 16
#define SEGMENTS 128
#elif dataset_type == 15
#define SEGMENTS 140
#elif dataset_type == 14
#define SEGMENTS 100
#elif dataset_type == 13
#define SEGMENTS 320
#elif dataset_type == 11
#define SEGMENTS 34
#elif dataset_type == 6
#define SEGMENTS 50
#elif dataset_type == 10
#define SEGMENTS 16
#else
#define SEGMENTS 32
#endif

#if SEGMENTS <= 16
typedef unsigned short saxt_type;
#elif SEGMENTS <= 32
typedef unsigned int saxt_type;
#else
typedef unsigned long saxt_type;
#endif


typedef float ts_type;
typedef time_t ts_time;

typedef unsigned char cod;

static const std::string input_directory = "/data/user_jialinhan/data_big/";
static const std::string query_directory = "/data/user_jialinhan/data_big/";
static const std::string ans_directory = "../../dataset_ans/";
static const std::string sax_directory = "../../dataset_sax/";
static const std::string origin_input_directory = "/data/user_jialinhan/data_big/";
static const std::string origin_query_directory = "/data/user_jialinhan/data_big/";

#if dataset_type == 29
#define TS_LENGTH 256
#define TOTAL_TS 10000  // 数据序列个数
// #define TOTAL_TS 100000000 // 数据序列个数
static const std::string input_filename = origin_input_directory + "astro-dataset.bin";
static const std::string query_filename = origin_query_directory + "astro-query.bin";
// static const std::string input_filename = embed_input_directory + "astro-database.bin";
// static const std::string query_filename = embed_query_directory + "astro-query.bin";
static const std::string embed_input_filename = embed_input_directory + "astro-database.bin";
static const std::string embed_query_filename = embed_query_directory + "astro-query.bin";
static const std::string data_name = "astro";
#elif dataset_type == 30
#define TS_LENGTH 96
// #define TOTAL_TS 10000
#define TOTAL_TS 100000000//数据序列个数
static const std::string input_filename = origin_input_directory + "deep1b-dataset.bin";
static const std::string query_filename = origin_query_directory + "deep1b-query.bin";
static const std::string embed_input_filename = embed_input_directory + "deep1b-database.bin";
static const std::string embed_query_filename = embed_query_directory + "deep1b-query.bin";
static const std::string data_name = "deep1b";
#elif dataset_type == 31
#define TS_LENGTH 256
// #define TOTAL_TS 10000
#define TOTAL_TS 100000000  // 数据序列个数
static  std::string input_filename = origin_input_directory + "F5-dataset.bin";
static  std::string query_filename = origin_query_directory + "F5-query.bin";
static  std::string embed_input_filename = embed_input_directory + "F5-database.bin";
static  std::string embed_query_filename = embed_query_directory + "F5-query.bin";
static  std::string data_name = "F5";
#elif dataset_type == 32
#define TS_LENGTH 256
// #define TOTAL_TS 10000
#define TOTAL_TS 100000000  // 数据序列个数
static const std::string input_filename = origin_input_directory + "F10-dataset.bin";
static const std::string query_filename = origin_query_directory + "F10-query.bin";
static const std::string embed_input_filename = embed_input_directory + "F10-database.bin";
static const std::string embed_query_filename = embed_query_directory + "F10-query.bin";
static const std::string data_name = "F10";
#elif dataset_type == 33
#define TS_LENGTH 256
// #define TOTAL_TS 10000
#define TOTAL_TS 100000000  // 数据序列个数
static const std::string input_filename = origin_input_directory + "origin-dataset.bin";
static const std::string query_filename = origin_query_directory + "origin-query.bin";
static const std::string embed_input_filename = embed_input_directory + "origin-database.bin";
static const std::string embed_query_filename = embed_query_directory + "origin-query.bin";
static const std::string data_name = "origin";
#elif dataset_type == 34
#define TS_LENGTH 128
// #define TOTAL_TS 10000
#define TOTAL_TS 100000000  // 数据序列个数
static const std::string input_filename = origin_input_directory + "sald-dataset.bin";
static const std::string query_filename = origin_query_directory + "sald-query.bin";
static const std::string embed_input_filename = embed_input_directory + "sald-database.bin";
static const std::string embed_query_filename = embed_query_directory + "sald-query.bin";
static const std::string data_name = "sald";
#elif dataset_type == 35
#define TS_LENGTH 256
// #define TOTAL_TS 10000
#define TOTAL_TS 100000000  // 数据序列个数
static const std::string input_filename = origin_input_directory + "seismic-dataset.bin";
static const std::string query_filename = origin_query_directory + "seismic-query.bin";
static const std::string embed_input_filename = embed_input_directory + "seismic-database.bin";
static const std::string embed_query_filename = embed_query_directory + "seismic-query.bin";
static const std::string data_name = "seismic";
#endif



#define binary_tree_root_full 0 // 二叉树第一层是否创建2^segment个节点
#define num_approximate_search_key (num_approximate_search_nodes * LEAF_MAX_NUM) // 二叉树树近似查询返回key个数
#define b_binary_use_breakpoint_to_split 0 // bsax在二叉树上分裂策略,1用breakpoint差值挑选段分裂，0用sax差值挑选段分裂

//#define sort_strategy 2 // 0按p排序,1按下界距离排序,2先按下界距离排序(SBB),一个batch内按p排序(SBS)
//#define sort_batch_num 10 // 排序策略选择2时,几个batch



static const int sax_offset = ((CARDINALITY - 1) * (CARDINALITY - 2)) / 2;
static int sax_offset_i[BIT_CARDINALITY + 1] = {0, 0, 3, 21, 105, 465, 1953, 8001, 32385};
static int cardinality_1_i[BIT_CARDINALITY + 1] = {0, 1, 3, 7, 15, 31, 63, 127, 255};

struct TS_emb{
  ts_type ts[SEGMENTS];
  bool operator== (const TS_emb& a) const {
    for (int i = SEGMENTS - 1; i >= 0; i--) {
        if (ts[i] == a.ts[i]) continue;
        return false;
    }
    return true;
}
};
struct TS{
  ts_type ts[TS_LENGTH];

    bool operator== (const TS& a) const {
        for (int i = TS_LENGTH - 1; i >= 0; i--) {
            if (ts[i] == a.ts[i]) continue;
            return false;
        }
        return true;
    }
};

struct EMBED{
  ts_type ts[SEGMENTS];

    bool operator== (const TS& a) const {
        for (int i = TS_LENGTH - 1; i >= 0; i--) {
            if (ts[i] == a.ts[i]) continue;
            return false;
        }
        return true;
    }
};

/**
 * sax结构，每段小端存储，如果基数>256，一段多个字节，前缀放后面(高地址)
 */

struct SAX {
    void set_min_value() {
        memset(sax, 0, sizeof(sax));
    }
    void set_max_value() {
        memset(sax, 0xff, sizeof(sax));
    }

    bool operator== (const SAX& a) const {
        for (int i = SEGMENTS - 1; i >= 0; i--) {
            if (sax[i] == a.sax[i]) continue;
            return false;
        }
        return true;
    }


    bool operator< (const SAX& a) const {
        for (int i = SEGMENTS - 1; i >= 0; i--) {
            if (sax[i] == a.sax[i]) continue;
            return sax[i] < a.sax[i];
        }
        return false;
    }

    sax_type sax[SEGMENTS];
};

struct PAA {
    float paa[SEGMENTS];
};

struct CARD {
    u_int8_t card[SEGMENTS];
    void set_min_card() {
        memset(card, 0, sizeof(card));
    }
    void set_max_card() {
        for (int i = 0; i < SEGMENTS; i ++ ) {
            card[i] = BIT_CARDINALITY;
        }
    }
};

/**
 * saxt结构，重要的位存在后面(高地址)，方便转成8字节小端比较
**/
struct SAXT {
  saxt_type saxt[BIT_CARDINALITY];

//    SAXT() {}
//    SAXT(const void* saxt_) {
//    memcpy(saxt, saxt_, sizeof(SAXT));
//  }

  bool operator< (const SAXT& a) const {
    for(int i=BIT_CARDINALITY-1;i>=0;i--) {
        if(saxt[i] == a.saxt[i]) continue;
        return saxt[i] < a.saxt[i];
    }
    return false;
  }
  bool operator> (const SAXT& a) const {
      for(int i=BIT_CARDINALITY-1;i>=0;i--) {
          if(saxt[i] == a.saxt[i]) continue;
          return saxt[i] > a.saxt[i];
      }
      return false;
  }

  bool operator<= (const SAXT& a) const {
      for(int i=BIT_CARDINALITY-1;i>=0;i--) {
          if(saxt[i] == a.saxt[i]) continue;
          return saxt[i] < a.saxt[i];
      }
      return true;
  }
  bool operator>= (const SAXT& a) const {
      for(int i=BIT_CARDINALITY-1;i>=0;i--) {
          if(saxt[i] == a.saxt[i]) continue;
          return saxt[i] > a.saxt[i];
      }
      return true;
  }

  bool operator== (const SAXT& a) const {
      for(int i=BIT_CARDINALITY-1;i>=0;i--) {
          if(saxt[i] == a.saxt[i]) continue;
          return false;
      }
      return true;
  }

};

typedef struct {
  ts_type apaa[SEGMENTS];
} paa_only;

typedef struct {
  ts_type ts[TS_LENGTH];
#if istime
  ts_time tsTime;
#endif
} tsKey;



typedef struct {
  ts_type ts[TS_LENGTH];
#if istime
  ts_time startTime;
  ts_time endTime;
#endif
} aquery_rep;

typedef struct {
  aquery_rep rep;
  int k;
  ts_type paa[SEGMENTS];
  SAXT asaxt;
} aquery;

typedef struct ares_exact_rep{
  tsKey atskey;
  float dist;

  bool operator< (const ares_exact_rep& a) const {
    return dist < a.dist;
  }
  bool operator> (const ares_exact_rep& a) const {
    return dist > a.dist;
  }
} ares_exact;

typedef struct ares{
  ares_exact rep;
  void* p;

  bool operator< (const ares& a) const {
    return rep < a.rep;
  }
  bool operator> (const ares& a) const {
    return rep > a.rep;
  }
} ares;



typedef std::pair<float, void*> dist_p;

static const size_t send_size1 = 1 +sizeof(int)*2 + sizeof(uint64_t) + sizeof(SAXT) * 2 + sizeof(ts_time) * 2;
static const size_t send_size2 = 1+sizeof(int)*3;
static const size_t send_size2_add = sizeof(uint64_t) + sizeof(SAXT) * 2 + sizeof(ts_time) * 2;

static const size_t sizeinfo_pos = sizeof(aquery_rep) + sizeof(int)*2 + sizeof(float);

static const size_t to_find_size_leafkey = sizeof(aquery_rep) + sizeof(int)*3 + sizeof(float);

static inline int compare_saxt(const void* a, const void* b) {
  if (*(SAXT*)a < *(SAXT*)b) return -1;
  if (*(SAXT*)a > *(SAXT*)b) return 1;
  return 0;
}

typedef struct to_bsear_rep {

  to_bsear_rep() {
    a1 = _mm256_loadu_ps(sax_a1);
    for(int i=0;i<8;i++) a2[i] = _mm256_loadu_ps(sax_a2[i]);
    for(int i=0;i<8;i++)
      for(int j=0;j<8;j++)
        a3[i][j] = _mm_loadu_ps(sax_a3[i][j]);
  }
  __m256 a1;
  __m256 a2[8];
  __m128 a3[8][8];
} to_bsear;

static to_bsear BM;

struct DisP {

    DisP(float dis, u_int64_t p): dis(dis), p(p) {}
    DisP() {}

    float dis;
    u_int64_t p;
};

struct DisNode {
    DisNode(float dis, u_int64_t begin, u_int64_t size): dis(dis), begin(begin), size(size) {}
    DisNode() {}

    float dis;
    u_int64_t begin;
    u_int64_t size;
};


static bool DisCmp(DisP& a, DisP& b) {
    return a.dis < b.dis;
}

static bool PCmp(DisP& a, DisP& b) {
    return a.p < b.p;
}

static bool DisNodeCmp(DisNode& a, DisNode& b) {
    return a.dis < b.dis;
}




typedef unsigned long long file_position_type;
typedef unsigned long long root_mask_type;

enum response {OUT_OF_MEMORY_FAILURE, FAILURE, SUCCESS};
enum insertion_mode {PARTIAL = 1,
                     TMP = 2,
                     FULL = 4,
                     NO_TMP = 8};

enum buffer_cleaning_mode {FULL_CLEAN, TMP_ONLY_CLEAN, TMP_AND_TS_CLEAN};
enum node_cleaning_mode {DO_NOT_INCLUDE_CHILDREN = 0,
                         INCLUDE_CHILDREN = 1};

#endif
