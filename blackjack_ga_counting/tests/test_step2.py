import numpy as np
from chromosome import random_chromosome, get_decision, get_count_values, get_bet_multipliers

def test_chromosome_shape():
    chrom = random_chromosome()
    assert chrom.shape == (294,)
    assert chrom.dtype == np.uint8

def test_chromosome_values_binary():
    chrom = random_chromosome()
    assert set(chrom).issubset({0, 1})

# --- get_decision: identical index arithmetic to Part 1 ---

def test_get_decision_returns_binary():
    chrom = random_chromosome()
    assert get_decision(chrom, 16, False, 10) in (0, 1)

def test_index_hard_4_ace():
    chrom = np.zeros(294, dtype=np.uint8)
    chrom[0] = 1
    assert get_decision(chrom, 4, False, 1) == 1   # hard index 0

def test_index_hard_20_ten():
    chrom = np.zeros(294, dtype=np.uint8)
    chrom[169] = 1
    assert get_decision(chrom, 20, False, 10) == 1  # hard index 169

def test_index_soft_12_ace():
    chrom = np.zeros(294, dtype=np.uint8)
    chrom[170] = 1
    assert get_decision(chrom, 12, True, 1) == 1   # soft index 170

def test_index_soft_20_ten():
    chrom = np.zeros(294, dtype=np.uint8)
    chrom[259] = 1
    assert get_decision(chrom, 20, True, 10) == 1  # soft index 259

def test_get_decision_ignores_count_bits():
    chrom = np.zeros(294, dtype=np.uint8)
    chrom[260:] = 1   # set all count/bet bits
    chrom[0] = 0      # hard 4 vs Ace = stand
    assert get_decision(chrom, 4, False, 1) == 0

# --- get_count_values ---

def test_count_values_keys():
    chrom = random_chromosome()
    cv = get_count_values(chrom)
    assert set(cv.keys()) == {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}

def test_count_values_domain():
    for _ in range(20):
        chrom = random_chromosome()
        for v in get_count_values(chrom).values():
            assert v in (-1, 0, 1), f"Unexpected count value: {v}"

def test_count_value_decoding_minus_one():
    chrom = np.zeros(294, dtype=np.uint8)
    # Ace is rank 0: bits 260-261 = 00 → -1
    cv = get_count_values(chrom)
    assert cv[1] == -1

def test_count_value_decoding_zero_01():
    chrom = np.zeros(294, dtype=np.uint8)
    chrom[261] = 1  # Ace bits 260-261 = 01 → 0
    cv = get_count_values(chrom)
    assert cv[1] == 0

def test_count_value_decoding_plus_one():
    chrom = np.zeros(294, dtype=np.uint8)
    chrom[260] = 1  # Ace bits 260-261 = 10 → +1
    cv = get_count_values(chrom)
    assert cv[1] == 1

def test_count_value_decoding_11_is_zero():
    chrom = np.zeros(294, dtype=np.uint8)
    chrom[260] = 1
    chrom[261] = 1  # Ace bits = 11 → 0
    cv = get_count_values(chrom)
    assert cv[1] == 0

def test_count_value_rank_10_uses_bits_278_279():
    # Rank 10 (index 9): start_bit = 260 + 9*2 = 278
    chrom = np.zeros(294, dtype=np.uint8)
    chrom[278] = 1  # bit pair 10 → +1 for rank 10
    cv = get_count_values(chrom)
    assert cv[10] == 1

# --- get_bet_multipliers ---

def test_bet_multipliers_length():
    chrom = random_chromosome()
    mults = get_bet_multipliers(chrom)
    assert len(mults) == 4

def test_bet_multipliers_range():
    for _ in range(20):
        chrom = random_chromosome()
        for m in get_bet_multipliers(chrom):
            assert 1 <= m <= 8, f"Multiplier {m} out of range 1-8"

def test_bet_multiplier_decoding_all_zeros():
    chrom = np.zeros(294, dtype=np.uint8)
    mults = get_bet_multipliers(chrom)
    assert mults == [1, 1, 1, 1]

def test_bet_multiplier_decoding_all_ones():
    chrom = np.zeros(294, dtype=np.uint8)
    chrom[282:294] = 1
    mults = get_bet_multipliers(chrom)
    assert mults == [8, 8, 8, 8]

def test_bet_multiplier_decoding_specific():
    # Range 1 (bits 285-287): set to 011 → encoded=3 → multiplier=4
    chrom = np.zeros(294, dtype=np.uint8)
    chrom[286] = 1  # 285=0, 286=1, 287=1 → 011 = 3 → mult=4
    chrom[287] = 1
    mults = get_bet_multipliers(chrom)
    assert mults[1] == 4

def test_bet_multiplier_independence():
    chrom = np.zeros(294, dtype=np.uint8)
    chrom[288] = 1  # range 2 (bits 288-290): 100 = 4 → mult=5
    mults = get_bet_multipliers(chrom)
    assert mults[0] == 1
    assert mults[1] == 1
    assert mults[2] == 5
    assert mults[3] == 1
