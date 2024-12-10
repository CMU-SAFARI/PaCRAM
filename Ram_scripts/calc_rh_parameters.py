from math import ceil, floor

def get_para_parameters(tRH):
    threshold = 1 - (10**-15)**(1/tRH)
    return threshold

def get_graphene_parameters(tRH, tREFWms):
    tREFW = tREFWms * 1000000
    tRC = 46
    k = 1
    num_table_entries = int(ceil(2*(tREFW/tRC)/tRH * ((k+1)/(k)) - 1))
    activation_threshold = int(floor(tRH / (2*(k+1))))
    reset_period_ns = int(tREFW / k)
    return num_table_entries, activation_threshold, reset_period_ns

def get_hydra_parameters(tRH, tREFWms):
    hydra_tracking_threshold = int(floor(tRH / 2))
    hydra_group_threshold = int(floor(hydra_tracking_threshold * 4 / 5))
    hydra_row_group_size = 128
    hydra_reset_period_ns = tREFWms * 1000000
    hydra_rcc_num_per_rank = 4096
    hydra_rcc_policy = "RANDOM"
    return hydra_tracking_threshold, hydra_group_threshold, hydra_row_group_size, hydra_reset_period_ns, hydra_rcc_num_per_rank, hydra_rcc_policy

def get_rfm_parameters(tRH):
    nrh_rfm_pairs = [
        (16, 1),
        (20, 2),
        (32, 3),
        (64, 6),
        (128, 13),
        (256, 27),
        (512, 60)
    ]
    for nrh, rfmth in nrh_rfm_pairs:
        if tRH <= nrh:
            return rfmth
    return 80

def get_prac_parameters(tRH, ABO_refs=4):
    nrh_aboth_pairmap = {
        1: [
            (32, 1),
            (64, 28),
            (128, 95)
        ],
        2: [
            (25, 1),
            (32, 8),
            (64, 42),
            (128, 108)
        ],
        4: [
            (20, 1),
            (32, 14),
            (64, 47),
            (128, 112)
        ]
    }
    nrh_aboth_pairs = nrh_aboth_pairmap[ABO_refs]
    for nrh, rfmth in nrh_aboth_pairs:
        if tRH <= nrh:
            return rfmth
    if tRH <= 256:
        return int(tRH * 0.8)
    return int(tRH * 0.9)

def get_pracrfm_parameters(tRH):
    aboth = get_prac_parameters(tRH)
    rfmth = int(min(75, aboth // 2))
    return aboth, rfmth

if __name__ == "__main__":
    print(get_graphene_parameters(1024))
    print(get_graphene_parameters(512))
    print(get_graphene_parameters(256))
    print(get_graphene_parameters(128))
    print(get_graphene_parameters(64))
    print(get_graphene_parameters(32))
    print(get_graphene_parameters(16))