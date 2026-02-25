import numpy as np


def random_chromosome() -> np.ndarray:
    """Return a random 260-bit chromosome."""
    return np.random.randint(0, 2, size=260, dtype=np.uint8)


def get_decision(chrom: np.ndarray, player_total: int, is_soft: bool, dealer_upcard: int) -> int:
    """
    Return 0 (stand) or 1 (hit) for the given game state.

    Parameters:
        player_total: integer sum of player's hand (4–20 for hard, 12–20 for soft)
        is_soft: True if the hand contains an ace counted as 11
        dealer_upcard: integer card value (Ace=1, 2–9, 10 for all ten-value cards)
    """
    # Ace=0, 2=1, 3=2, ..., 9=8, 10=9
    dealer_upcard_index = 0 if dealer_upcard == 1 else dealer_upcard - 1

    if is_soft:
        index = 170 + (player_total - 12) * 10 + dealer_upcard_index
    else:
        index = (player_total - 4) * 10 + dealer_upcard_index

    return int(chrom[index])
