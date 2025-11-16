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

    auto start = std::chrono::high_resolution_clock::now();
    std::string subfolder = "exact_search_results";
    std::string filename_e = data_name+"-exact"+".txt";
    std::string fullPath = subfolder + "/" + filename_e;
    std::system(("mkdir -p " + subfolder).c_str());
    std::ofstream outFile(fullPath);

    // 对每条查询执行搜索
    for (int i=0;i<num;i++) {
        EXACT_GET_ANS_START

        cout<<"query:"<<i<<endl;
        COUNT_CLEAR
        auto res = isax_index.search(&query_ts_vec[i], K,i,-1);
        for(auto ele:res) {
            outFile<<i<<","<<ele.second<<","<<ele.first<<endl;
        }
        EXACT_GET_ANS_END
        PRINT_COUNT
    }
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    outFile<<"平均总 time:"<<duration.count() / NUM_SEARCH<<endl;
    outFile<<"multiply_ratio:"<<MULTIPLY_RATIO<<endl;
    outFile.close();
    std::cout << "数据已成功写入文件。" << std::endl;

    return 0;
}