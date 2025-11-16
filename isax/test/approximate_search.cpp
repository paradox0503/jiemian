#include <vector>
#include <algorithm>
#include <thread>
#include "../sax/include/sax.h"
#include "../i_binary/iSAX2Tree.h"
#include "CntRecord.h"
#include "TimeRecord.h"
#include "google/malloc_extension.h"
#include <iostream>
#include <fstream>
#include <chrono>
#include <vector>
#include <utility>
#include <string>
#include <filesystem>
using namespace std;
int main() {
    cout<< "test isax" << endl;
    std::string output_directory = "../../dataset_index_isax/";
    std::system(("mkdir -p " + output_directory).c_str());
    const int num = NUM_SEARCH;
    FILE * query_data_file = fopen(query_filename.c_str(), "r");
    vector<TS> query_ts_vec(num);
    for(int i=0;i<num;i++) {
        fread(&query_ts_vec[i], sizeof(TS), 1, query_data_file);
    }
    isax::iSAX2Tree isax_index(data_name, output_directory);
    isax_index.build(input_filename);
    MallocExtension::instance()->ReleaseFreeMemory();

    std::string subfolder = "approximate_search_results";
    std::string filename_e = data_name+"-approximate"+".txt";
    std::string fullPath = subfolder + "/" + filename_e;
    std::system(("mkdir -p " + subfolder).c_str());
    std::ofstream outFile(fullPath);
    // 对每条查询执行搜索
    auto start = std::chrono::high_resolution_clock::now();
    for (int i=0;i<num;i++) {
        EXACT_GET_ANS_START
        cout<<i<<endl;
        COUNT_CLEAR
        auto res2 = isax_index.approximateSearch(&query_ts_vec[i], K,i,-1);//,&query_embed_vec[i]
        for(auto ele:res2) {
            outFile<<i<<","<<ele.second<<","<<ele.first<<endl;
        }
        PRINT_COUNT
        EXACT_GET_ANS_END
        // PRINT_TIME
    }
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    outFile<<"平均总 time:"<<duration.count() / NUM_SEARCH<<endl;
    outFile.close();
    std::cout << "数据已成功写入文件。" << std::endl;

    return 0;
}