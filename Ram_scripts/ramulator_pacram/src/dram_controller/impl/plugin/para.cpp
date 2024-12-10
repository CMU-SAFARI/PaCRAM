#include <vector>
#include <unordered_map>
#include <limits>
#include <random>

#include "base/base.h"
#include "dram_controller/controller.h"
#include "dram_controller/plugin.h"
#include "dram_controller/impl/plugin/device_config/device_config.h"
#include "pacram.h"

namespace Ramulator {

class PARA : public IControllerPlugin, public Implementation {
  RAMULATOR_REGISTER_IMPLEMENTATION(IControllerPlugin, PARA, "PARA", "PARA.")

  private:
    IDRAM* m_dram = nullptr;
    DeviceConfig m_cfg;

    float m_pr_threshold;

    int   m_seed;
    std::mt19937 m_generator;
    std::uniform_real_distribution<float> m_distribution;
    bool m_is_debug = false;

    int m_VRR_req_id = -1;
    int m_RVRR_req_id = -1;

    int m_bank_level = -1;
    int m_row_level = -1;

    Clk_t m_clk;

    bool m_is_pacram = false;
    PaCRAM* pacram = nullptr;
    int m_pacram_set_period_ns = -1;
    int m_pacram_set_period_clk = -1;
    bool m_pacram_always_pcr = false;

    int s_vrr_counter = 0;
    int s_rvrr_counter = 0;

  public:
    void init() override { 
      m_pr_threshold = param<float>("threshold").desc("Probability threshold for issuing neighbor row refresh").required();
      if (m_pr_threshold <= 0.0f || m_pr_threshold >= 1.0f)
        throw ConfigurationError("Invalid probability threshold ({}) for PARA!", m_pr_threshold);

      m_seed = param<int>("seed").desc("Seed for the RNG").default_val(123);
      m_generator = std::mt19937(m_seed);
      m_distribution = std::uniform_real_distribution<float>(0.0, 1.0);

      m_is_debug = param<bool>("debug").default_val(false);
      m_is_pacram = param<bool>("pacram").default_val(false);
    };

    void setup(IFrontEnd* frontend, IMemorySystem* memory_system) override {
      m_ctrl = cast_parent<IDRAMController>();
      m_dram = m_ctrl->m_dram;
  
      m_cfg.set_device(m_ctrl);

      if (!m_dram->m_commands.contains("VRR")) {
        throw ConfigurationError("PARA is not compatible with the DRAM implementation that does not have Victim-Row-Refresh (VRR) command!");
      }

      m_VRR_req_id = m_dram->m_requests("victim-row-refresh");
      if(m_is_pacram)
        m_RVRR_req_id = m_dram->m_requests("reduced-victim-row-refresh");

      m_bank_level = m_dram->m_levels("bank");
      m_row_level = m_dram->m_levels("row");

      register_stat(s_vrr_counter).name("vrr_counter");
      register_stat(s_rvrr_counter).name("rvrr_counter");
      
      if(m_is_pacram) {
        m_pacram_set_period_ns = param<int>("pacram_set_period_ns").desc("PR set ns").required();
        if (m_pacram_set_period_ns == 0){
          m_pacram_always_pcr = true;
          m_pacram_set_period_clk = std::numeric_limits<int>::max();
        }else{
          m_pacram_always_pcr = false;
          m_pacram_set_period_clk = m_pacram_set_period_ns / ((float) m_dram->m_timing_vals("tCK_ps") / 1000.0f);
        }
        pacram = new PaCRAM(m_cfg.m_num_banks, m_cfg.m_num_rows_per_bank, m_pacram_always_pcr);
      }
    };

    void update(bool request_found, ReqBuffer::iterator& req_it) override {
      m_clk++;
      
      if (m_is_pacram){
        if (m_clk % m_pacram_set_period_clk == 0) {
        // Reset        
          pacram->set_all();
        }
      }
      
      if (request_found) {
        if (
          m_dram->m_command_meta(req_it->command).is_opening && 
          m_dram->m_command_scopes(req_it->command) == m_row_level
        ) {
          int flat_bank_id = m_cfg.get_flat_bank_id(*req_it);

          if (m_distribution(m_generator) < m_pr_threshold) {
            if(m_is_pacram){
              bool use_pcr = pacram->use_pcr(flat_bank_id, req_it->addr_vec[m_row_level]);
              if (use_pcr){
                Request rvrr_req(req_it->addr_vec, m_RVRR_req_id);
                m_ctrl->priority_send(rvrr_req);
                s_rvrr_counter++;
              } else {
                Request vrr_req(req_it->addr_vec, m_VRR_req_id);
                m_ctrl->priority_send(vrr_req);
                s_vrr_counter++;
              }
            } else {
              Request vrr_req(req_it->addr_vec, m_VRR_req_id);
              m_ctrl->priority_send(vrr_req);
              s_vrr_counter++;
            }
          }
        }
      }
    };

};

}       // namespace Ramulator
