import numpy as np

# Chromosome layout (294 bits total):
#   Bits   0-259: play strategy (260 bits) — identical to Part 1
#   Bits 260-281: card count values (22 bits) — 11 ranks × 2 bits
#   Bits 282-293: bet multipliers (12 bits) — 4 ranges × 3 bits

# Bit-pair → count value decoding table
_COUNT_DECODE = {(0, 0): -1, (0, 1): 0, (1, 0): 1, (1, 1): 0}

# Dealer upcard → column index
_UPCARD_INDEX = {1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6, 8: 7, 9: 8, 10: 9}


def random_chromosome() -> np.ndarray:
    """Return a random 294-bit chromosome."""
    return np.random.randint(0, 2, size=294, dtype=np.uint8)


def get_decision(chrom: np.ndarray, player_total: int, is_soft: bool,
                 dealer_upcard: int) -> int:
    """
    Return 0 (stand) or 1 (hit) for the given game state.
    Reads only bits 0-259 (play strategy region).
    """
    upcard_idx = _UPCARD_INDEX[dealer_upcard]
    if is_soft:
        index = 170 + (player_total - 12) * 10 + upcard_idx
    else:
        index = (player_total - 4) * 10 + upcard_idx
    return int(chrom[index])


def get_count_values(chrom: np.ndarray) -> dict:
    """
    Decode the card count value for each rank from bits 260-281.
    Returns {1: cv_ace, 2: cv_2, ..., 9: cv_9, 10: cv_10}.
    Bit pairs: 00 → -1, 01 → 0, 10 → +1, 11 → 0 (unused).
    """
    result = {}
    for r in range(10):  # r=0 → Ace, r=1 → 2, ..., r=9 → 10
        start = 260 + r * 2
        pair = (int(chrom[start]), int(chrom[start + 1]))
        card_value = r + 1  # Ace=1, 2=2, ..., 10=10
        result[card_value] = _COUNT_DECODE[pair]
    return result


def get_bet_multipliers(chrom: np.ndarray) -> list:
    """
    Decode the four bet multipliers (1-8) from bits 282-293.
    Order: [mult_for_<=−2, mult_for_−1_to_+1, mult_for_+2_to_+4, mult_for_>=+5]
    Each 3-bit group: big-endian integer + 1 → multiplier 1-8.
    """
    multipliers = []
    for i in range(4):
        start = 282 + i * 3
        encoded = int(chrom[start]) * 4 + int(chrom[start + 1]) * 2 + int(chrom[start + 2])
        multipliers.append(encoded + 1)
    return multipliers
