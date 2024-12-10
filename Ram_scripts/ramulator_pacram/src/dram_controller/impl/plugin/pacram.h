#include "base/base.h"
#include "dram_controller/controller.h"
#include "dram_controller/plugin.h"

#include <vector>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <functional>
#include <bitset>
#include <queue>
#include <iostream>
#include <fstream>
#include <sstream>
#include <random>

namespace Ramulator {

class PaCRAM {
  public:
    std::vector<std::unordered_set<int>> fcr_sets;
    std::vector<std::unordered_map<int, int>> pcr_counters;
    int bank_num = 0;
    int row_num = 0;
    bool always_pcr = false;
    PaCRAM(int _bank_num, int _row_num, bool _always_pcr) 
      : bank_num(_bank_num), row_num(_row_num) {
      
      always_pcr = _always_pcr;
      for (int i = 0; i < bank_num; i++) {
        std::unordered_set<int> tmp;
        fcr_sets.push_back(tmp);
      }

      set_all();

      std::cout << std::endl;
      std::cout << "PaCRAM initialized" << std::endl;
      std::cout << "bank_num: " << bank_num << std::endl;
      std::cout << "row_num: " << row_num << std::endl;
      std::cout << "always_pcr: " << always_pcr << std::endl;
      std::cout << std::endl;
    }

    void set_all() {
      if (always_pcr) // no need to set
        return;

      for (int i = 0; i < bank_num; i++) {
        for (int j = 0; j < row_num; j++) {
          if (fcr_sets[i].find(j) == fcr_sets[i].end())
            fcr_sets[i].insert(j);
        }
      }
    }

    bool use_pcr(int bank_id, int row_id) {
      if (always_pcr)
        return true;

      if (fcr_sets[bank_id].find(row_id) != fcr_sets[bank_id].end()) { // in set
        // std::cout << "PR: bank " << bank_id << " row " << row_id << " cannot use PR. Use Full Restoration" << std::endl;
        fcr_sets[bank_id].erase(row_id);
        return false;
      } else { // not in set
        // std::cout << "PR: bank " << bank_id << " row " << row_id << " can use PR. Use Partial Restoration" << std::endl;
        return true;
      }
    }
    
};


}