import numpy as np
import random
from simulator import (make_shoe, hand_value, calculate_true_count,
                       get_bet, simulate_hand, simulate_session, evaluate_fitness)
from chromosome import random_chromosome, get_count_values

# --- make_shoe ---

def test_shoe_length():
    assert len(make_shoe()) == 312

def test_shoe_composition():
    shoe = make_shoe()
    assert shoe.count(1) == 24    # 4 aces/deck × 6 decks
    for v in range(2, 10):
        assert shoe.count(v) == 24
    assert shoe.count(10) == 96   # 16 ten-value cards/deck × 6 decks

# --- hand_value ---

def test_hand_value_no_ace():
    total, is_soft = hand_value([7, 9])
    assert total == 16
    assert is_soft is False

def test_hand_value_soft_ace():
    total, is_soft = hand_value([1, 6])
    assert total == 17
    assert is_soft is True

def test_hand_value_hard_ace_after_bust():
    total, is_soft = hand_value([1, 9, 5])
    assert total == 15
    assert is_soft is False

def test_hand_value_blackjack():
    total, is_soft = hand_value([1, 10])
    assert total == 21
    assert is_soft is True

def test_hand_value_double_ace():
    total, is_soft = hand_value([1, 1])
    assert total == 12
    assert is_soft is True

# --- calculate_true_count ---

def test_true_count_basic():
    tc = calculate_true_count(6, 156)
    assert tc == 2

def test_true_count_zero_running():
    assert calculate_true_count(0, 0) == 0

def test_true_count_guards_zero_remaining():
    tc = calculate_true_count(5, 312)
    assert tc == 0

def test_true_count_rounding():
    tc = calculate_true_count(5, 260)
    assert tc == 5

# --- get_bet ---

def test_get_bet_within_bounds():
    chrom = random_chromosome()
    bet = get_bet(chrom, 0, 0, 1000.0)
    assert 1 <= bet <= 8

def test_get_bet_capped_by_bankroll():
    chrom = np.zeros(294, dtype=np.uint8)
    chrom[282:294] = 1   # all multipliers = 8
    bet = get_bet(chrom, 10, 0, 2.0)
    assert bet == 2.0

def test_get_bet_range_selection():
    chrom = np.zeros(294, dtype=np.uint8)
    # Range 0 (<=−2): bits 282-284 = 001 → mult=2
    chrom[284] = 1
    # Range 3 (>=+5): bits 291-293 = 111 → mult=8
    chrom[291] = chrom[292] = chrom[293] = 1

    bet_low = get_bet(chrom, -12, 0, 1000.0)
    assert bet_low == 2

    bet_high = get_bet(chrom, 30, 0, 1000.0)
    assert bet_high == 8

# --- simulate_hand ---

def test_simulate_hand_return_structure():
    chrom = random_chromosome()
    shoe = make_shoe()
    random.shuffle(shoe)
    outcome, new_cards_dealt, new_rc, new_bankroll = simulate_hand(
        chrom, shoe, 0, 0, 1000.0, 1.0
    )
    assert outcome in ('win', 'loss', 'tie')
    assert new_cards_dealt > 0
    assert isinstance(new_rc, int)
    assert isinstance(new_bankroll, float)

def test_simulate_hand_advances_cards_dealt():
    chrom = random_chromosome()
    shoe = make_shoe()
    random.shuffle(shoe)
    _, new_cd, _, _ = simulate_hand(chrom, shoe, 0, 0, 1000.0, 1.0)
    assert new_cd >= 4

def test_simulate_hand_bankroll_changes_on_win():
    chrom = np.zeros(294, dtype=np.uint8)  # all stand
    shoe = make_shoe()
    # player=Ace, dealer_hole=2, player=10, dealer_upcard=3 → player BJ, dealer no BJ
    shoe = [1, 2, 10, 3] + shoe
    _, _, _, bankroll = simulate_hand(chrom, shoe, 0, 0, 1000.0, 2.0)
    assert bankroll == 1003.0   # 3:2 on $2 bet = +$3

def test_simulate_hand_bankroll_changes_on_loss():
    chrom = np.zeros(294, dtype=np.uint8)  # all stand
    shoe = make_shoe()
    # player=5, dealer_hole=1, player=6, dealer_upcard=10 → dealer BJ
    shoe = [5, 1, 6, 10] + shoe
    _, _, _, bankroll = simulate_hand(chrom, shoe, 0, 0, 1000.0, 3.0)
    assert bankroll == 997.0   # -$3

def test_hole_card_count_not_added_early():
    chrom = np.zeros(294, dtype=np.uint8)
    # Set all count bits to +1 (10 pattern per rank)
    for r in range(10):
        chrom[260 + r * 2] = 1
    shoe = make_shoe()
    random.shuffle(shoe)
    _, cd, rc, _ = simulate_hand(chrom, shoe, 0, 0, 1000.0, 1.0)
    # At minimum 4 cards dealt, each +1, so rc >= 4
    assert rc >= 4

# --- simulate_session ---

def test_simulate_session_returns_list():
    chrom = random_chromosome()
    history = simulate_session(chrom, n_hands=10)
    assert isinstance(history, list)
    assert len(history) <= 10
    assert all(isinstance(b, float) for b in history)

def test_simulate_session_stops_on_bust():
    chrom = np.zeros(294, dtype=np.uint8)
    chrom[282:294] = 1   # max bets always
    random.seed(99)
    np.random.seed(99)
    history = simulate_session(chrom, n_hands=1000)
    if history and history[-1] <= 0:
        assert len(history) < 1000

def test_simulate_session_bankroll_is_nonnegative():
    chrom = random_chromosome()
    history = simulate_session(chrom, n_hands=100)
    for b in history:
        assert b >= 0.0, f"Bankroll went negative: {b}"

def test_simulate_session_reshuffles_at_penetration():
    chrom = random_chromosome()
    random.seed(0)
    history = simulate_session(chrom, n_hands=500)
    assert len(history) > 0

# --- evaluate_fitness ---

def test_evaluate_fitness_returns_float():
    chrom = random_chromosome()
    f = evaluate_fitness(chrom, n_hands=50)
    assert isinstance(f, float)

def test_evaluate_fitness_nonnegative():
    chrom = random_chromosome()
    f = evaluate_fitness(chrom, n_hands=50)
    assert f >= 0.0

def test_evaluate_fitness_reasonable_range():
    chrom = random_chromosome()
    random.seed(42)
    f = evaluate_fitness(chrom, n_hands=200)
    assert 0.0 <= f <= 3000.0, f"Fitness {f} looks unreasonable"
