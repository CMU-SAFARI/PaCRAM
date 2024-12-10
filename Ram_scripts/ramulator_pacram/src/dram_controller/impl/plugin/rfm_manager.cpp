#include "base/base.h"
#include "dram_controller/controller.h"
#include "dram_controller/plugin.h"
#include "pacram.h"

namespace Ramulator {

class RFMManager : public IControllerPlugin, public Implementation {
    RAMULATOR_REGISTER_IMPLEMENTATION(IControllerPlugin, RFMManager, "RFMManager", "RFM Manager.")

private:
    IDRAM* m_dram = nullptr;
    std::vector<int> m_bank_ctrs;

    Clk_t m_clk = 0;

    int m_rfm_req_id = -1;
    int m_rrfm_req_id = -1;
    int m_no_send = -1;

    int m_rank_level = -1;
    int m_bank_level = -1;
    int m_bankgroup_level = -1;
    int m_row_level = -1;
    int m_col_level = -1;

    int m_num_ranks = -1;
    int m_num_bankgroups = -1;
    int m_num_banks_per_bankgroup = -1;
    int m_num_banks_per_rank = -1;
    int m_num_rows_per_bank = -1;
    int m_num_cls = -1;

    int m_rfm_thresh = -1;
    bool m_debug = false;


    bool m_is_pacram = false;
    PaCRAM* pacram = nullptr;
    int m_pacram_set_period_ns = -1;
    int m_pacram_set_period_clk = -1;
    bool m_pacram_always_pcr = false;

    int s_rfm_counter = 0;
    int s_rrfm_counter = 0;

public:
    void init() override { 
        m_rfm_thresh = param<int>("rfm_threshold").default_val(256);
        m_is_pacram = param<bool>("pacram").default_val(false);        
        m_debug = param<bool>("debug").default_val(false);
    }

    void setup(IFrontEnd* frontend, IMemorySystem* memory_system) override {
        m_ctrl = cast_parent<IDRAMController>();
        m_dram = m_ctrl->m_dram;
        if (!m_dram->m_requests.contains("same-bank-rfm")) {
            std::cout << "[Ramulator::RFMManager] [CRITICAL ERROR] DRAM Device does not support request: same-bank-rfm" << std::endl; 
            exit(0);
        }
        m_rfm_req_id = m_dram->m_requests("same-bank-rfm");
        if(m_is_pacram)
            m_rrfm_req_id = m_dram->m_requests("reduced-same-bank-rfm");

        m_rank_level = m_dram->m_levels("rank");
        m_bank_level = m_dram->m_levels("bank");
        m_bankgroup_level = m_dram->m_levels("bankgroup");
        m_row_level = m_dram->m_levels("row");
        m_col_level = m_dram->m_levels("column");

        m_num_ranks = m_dram->get_level_size("rank");
        m_num_bankgroups = m_dram->get_level_size("bankgroup");
        m_num_banks_per_bankgroup = m_dram->get_level_size("bankgroup") < 0 ? 0 : m_dram->get_level_size("bank");
        m_num_banks_per_rank = m_dram->get_level_size("bankgroup") < 0 ? 
                                m_dram->get_level_size("bank") : 
                                m_dram->get_level_size("bankgroup") * m_dram->get_level_size("bank");
        m_num_rows_per_bank = m_dram->get_level_size("row");
        m_num_cls = m_dram->get_level_size("column") / 8;
        
        m_bank_ctrs.resize(m_num_ranks * m_num_banks_per_rank);
        for (int i = 0; i < m_bank_ctrs.size(); i++) {
            m_bank_ctrs[i] = 0;
        }
        m_no_send = 0;

        register_stat(s_rfm_counter).name("rfm_counter");
        register_stat(s_rrfm_counter).name("rrfm_counter");
        
        std::cout << "RFMManager: " << m_rfm_thresh << std::endl;

        if(m_is_pacram) {
            m_pacram_set_period_ns = param<int>("pacram_set_period_ns").desc("PR set ns").required();
            if (m_pacram_set_period_ns == 0){
                m_pacram_always_pcr = true;
                m_pacram_set_period_clk = std::numeric_limits<int>::max();
            }else{
                m_pacram_always_pcr = false;
                m_pacram_set_period_clk = m_pacram_set_period_ns / ((float) m_dram->m_timing_vals("tCK_ps") / 1000.0f);
            }
            pacram = new PaCRAM(m_num_banks_per_rank * m_num_ranks, m_num_rows_per_bank, m_pacram_always_pcr);
        }
    }

    void update(bool request_found, ReqBuffer::iterator& req_it) override {
        m_clk++;

        if (m_is_pacram){
            if (m_clk % m_pacram_set_period_clk == 0) {
                // Reset        
                pacram->set_all();
            }
        }

        if (!request_found) {
            return;
        }

        auto& req = *req_it;
        auto& req_meta = m_dram->m_command_meta(req.command);
        auto& req_scope = m_dram->m_command_scopes(req.command);
        if (!(req_meta.is_opening && req_scope == m_row_level)) {
            return; 
        }

        int flat_bank_id = req_it->addr_vec[m_bank_level];
        int accumulated_dimension = 1;
        for (int i = m_bank_level - 1; i >= m_rank_level; i--) {
            accumulated_dimension *= m_dram->m_organization.count[i + 1];
            flat_bank_id += req_it->addr_vec[i] * accumulated_dimension;
        }

        m_bank_ctrs[flat_bank_id]++;
        if (m_debug) {
            std::cout << "Rank     : " << req_it->addr_vec[m_rank_level] << std::endl;
            std::cout << "Bank     : " << req_it->addr_vec[m_bank_level] << std::endl;
            std::cout << "BankGroup: " << req_it->addr_vec[m_bankgroup_level] << std::endl;
            std::cout << "Flat Bank: " << flat_bank_id << std::endl;
        }
        if (m_bank_ctrs[flat_bank_id] < m_rfm_thresh) {
            return;
        }
        
        for (int bg = 0; bg < m_num_bankgroups; bg++) {
            int bank_id = req_it->addr_vec[m_rank_level] * m_num_banks_per_rank + bg * m_num_banks_per_bankgroup + req_it->addr_vec[m_bank_level];
            m_bank_ctrs[bank_id] = 0;
        }
        if (m_is_pacram) {
            bool use_pcr = pacram->use_pcr(flat_bank_id, req_it->addr_vec[m_row_level]);
            if (use_pcr) {
                Request rrfm(req.addr_vec, m_rrfm_req_id);
                rrfm.addr_vec[m_bankgroup_level] = -1;
                if (!m_ctrl->priority_send(rrfm)) {
                    std::cout << "[Ramulator::RFMManager] [CRITICAL ERROR] Could not send request: reduced-same-bank-rfm" << std::endl; 
                    exit(0);
                }
                s_rrfm_counter++;
            } else {
                Request rfm(req.addr_vec, m_rfm_req_id);
                rfm.addr_vec[m_bankgroup_level] = -1;
                if (!m_ctrl->priority_send(rfm)) {
                    std::cout << "[Ramulator::RFMManager] [CRITICAL ERROR] Could not send request: same-bank-rfm" << std::endl; 
                    exit(0);
                }
                s_rfm_counter++;
            }
        } else {
            Request rfm(req.addr_vec, m_rfm_req_id);
            rfm.addr_vec[m_bankgroup_level] = -1;
            // TODO: Add a buffer to retry later
            if (!m_ctrl->priority_send(rfm)) {
                std::cout << "[Ramulator::RFMManager] [CRITICAL ERROR] Could not send request: same-bank-rfm" << std::endl; 
                exit(0);
            }
            s_rfm_counter++;
        }
    }
};

}       // namespace Ramulator
