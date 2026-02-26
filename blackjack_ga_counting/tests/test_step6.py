import numpy as np
import random
from chromosome import random_chromosome, get_decision, get_count_values, get_bet_multipliers
from simulator import evaluate_fitness, simulate_session
import ga as ga_module

def _run_short_ga(generations=5, pop_size=10, n_hands=50, seed=42):
    orig_gen   = ga_module.N_GENERATIONS
    orig_size  = ga_module.POPULATION_SIZE
    orig_hands = ga_module.N_HANDS
    ga_module.N_GENERATIONS   = generations
    ga_module.POPULATION_SIZE = pop_size
    ga_module.N_HANDS         = n_hands
    np.random.seed(seed)
    random.seed(seed)
    final_pop, history = ga_module.run_ga()
    ga_module.N_GENERATIONS   = orig_gen
    ga_module.POPULATION_SIZE = orig_size
    ga_module.N_HANDS         = orig_hands
    return final_pop, history

def test_history_structure():
    _, history = _run_short_ga()
    for entry in history:
        assert entry['min'] <= entry['mean'] <= entry['max']
        assert entry['min'] <= entry['median'] <= entry['max']
        assert entry['min'] >= 0.0

def test_fitness_values_are_bankrolls():
    # Bankroll fitness should be in a plausible dollar range, not [0,1]
    _, history = _run_short_ga(generations=3, pop_size=5, n_hands=30)
    for entry in history:
        assert entry['max'] <= 5000.0, \
            f"Max bankroll {entry['max']} is implausibly large — may be using win-rate fitness"

def test_evaluate_fitness_returns_bankroll_not_winrate():
    chrom = random_chromosome()
    random.seed(0); np.random.seed(0)
    f = evaluate_fitness(chrom, n_hands=200)
    # Win rate would be in [0,1]; bankroll should be substantially larger
    assert f > 1.0 or f == 0.0, \
        f"evaluate_fitness returned {f} — looks like a win rate, not a bankroll"

def test_simulate_session_bankroll_history():
    chrom = random_chromosome()
    random.seed(7); np.random.seed(7)
    history = simulate_session(chrom, n_hands=100)
    assert len(history) > 0
    assert all(b >= 0.0 for b in history)

def test_count_values_all_in_domain():
    for _ in range(10):
        chrom = random_chromosome()
        for v in get_count_values(chrom).values():
            assert v in (-1, 0, 1)

def test_bet_multipliers_all_in_range():
    for _ in range(10):
        chrom = random_chromosome()
        for m in get_bet_multipliers(chrom):
            assert 1 <= m <= 8

def test_heatmap_hard_low_totals_lean_hit():
    # n_hands=500 needed: bankroll fitness has ~4x higher variance than win-rate fitness,
    # requiring more hands to get a sufficient signal-to-noise ratio for convergence.
    final_pop, _ = _run_short_ga(generations=15, pop_size=20, n_hands=500)
    hit_pcts = []
    for total in range(4, 9):   # hard 4–8
        for upcard in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
            hit_pcts.append(
                np.mean([get_decision(c, total, False, upcard) for c in final_pop]) * 100
            )
    avg = np.mean(hit_pcts)
    assert avg >= 55, f"Hard 4–8 avg hit% is {avg:.1f}%, expected ≥55%"

def test_heatmap_hard_high_totals_lean_stand():
    # n_hands=500 needed: bankroll fitness has ~4x higher variance than win-rate fitness,
    # requiring more hands to get a sufficient signal-to-noise ratio for convergence.
    final_pop, _ = _run_short_ga(generations=15, pop_size=20, n_hands=500)
    hit_pcts = []
    for total in range(17, 21):  # hard 17–20
        for upcard in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
            hit_pcts.append(
                np.mean([get_decision(c, total, False, upcard) for c in final_pop]) * 100
            )
    avg = np.mean(hit_pcts)
    assert avg <= 45, f"Hard 17–20 avg hit% is {avg:.1f}%, expected ≤45%"

def test_blackjack_ga_not_imported():
    # The extension must be self-contained — no imports from blackjack_ga/
    import simulator, chromosome, ga
    for mod in (simulator, chromosome, ga):
        src = open(mod.__file__).read()
        assert 'from blackjack_ga' not in src and 'import blackjack_ga' not in src, \
            f"{mod.__file__} imports from blackjack_ga/ — extension must be standalone"

def test_chromosome_length_is_294():
    chrom = random_chromosome()
    assert len(chrom) == 294, "Chromosome must be 294 bits, not 260"
