import numpy as np
from chromosome import random_chromosome, get_decision


def test_chromosome_shape():
    chrom = random_chromosome()
    assert chrom.shape == (260,)
    assert chrom.dtype == np.uint8


def test_chromosome_values():
    chrom = random_chromosome()
    assert set(chrom).issubset({0, 1})


def test_get_decision_returns_binary():
    chrom = random_chromosome()
    result = get_decision(chrom, 16, False, 10)
    assert result in (0, 1)


def test_index_hard_4_ace():
    chrom = np.zeros(260, dtype=np.uint8)
    chrom[0] = 1
    assert get_decision(chrom, 4, False, 1) == 1   # index 0


def test_index_hard_20_ten():
    chrom = np.zeros(260, dtype=np.uint8)
    chrom[169] = 1
    assert get_decision(chrom, 20, False, 10) == 1  # index 169


def test_index_soft_12_ace():
    chrom = np.zeros(260, dtype=np.uint8)
    chrom[170] = 1
    assert get_decision(chrom, 12, True, 1) == 1   # index 170


def test_index_soft_20_ten():
    chrom = np.zeros(260, dtype=np.uint8)
    chrom[259] = 1
    assert get_decision(chrom, 20, True, 10) == 1  # index 259


def test_hard_and_soft_are_independent():
    chrom = np.zeros(260, dtype=np.uint8)
    chrom[0] = 1      # hard 4 vs Ace = hit
    chrom[170] = 0    # soft 12 vs Ace = stand
    assert get_decision(chrom, 4, False, 1) == 1
    assert get_decision(chrom, 12, True, 1) == 0
