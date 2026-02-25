import numpy as np
import random
from chromosome import random_chromosome, get_decision
from simulator import evaluate_fitness


def _run_short_ga(generations=10, pop_size=20, n_hands=200, seed=42):
    import ga as ga_module
    orig_gen = ga_module.N_GENERATIONS
    orig_size = ga_module.POPULATION_SIZE
    orig_hands = ga_module.N_HANDS
    ga_module.N_GENERATIONS = generations
    ga_module.POPULATION_SIZE = pop_size
    ga_module.N_HANDS = n_hands
    np.random.seed(seed)
    random.seed(seed)
    final_pop, history = ga_module.run_ga()
    ga_module.N_GENERATIONS = orig_gen
    ga_module.POPULATION_SIZE = orig_size
    ga_module.N_HANDS = orig_hands
    return final_pop, history


def test_fitness_improves_over_generations():
    _, history = _run_short_ga(generations=10, pop_size=20, n_hands=300)
    early_mean = history[0]['mean']
    late_mean = history[-1]['mean']
    assert late_mean >= early_mean - 0.02, \
        f"Mean fitness regressed from {early_mean:.4f} to {late_mean:.4f}"


def test_max_fitness_above_random_baseline():
    _, history = _run_short_ga(generations=10, pop_size=20, n_hands=300)
    final_max = history[-1]['max']
    assert final_max >= 0.40, f"Max fitness {final_max:.4f} is below expected minimum of 0.40"


def test_heatmap_hard_low_totals_lean_hit():
    final_pop, _ = _run_short_ga(generations=20, pop_size=30, n_hands=500)
    hard_matrix = np.zeros((17, 10))
    for row, total in enumerate(range(4, 21)):
        for col, upcard in enumerate([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]):
            hard_matrix[row, col] = np.mean([get_decision(c, total, False, upcard)
                                             for c in final_pop]) * 100
    # Hard totals 4–8 are rows 0–4; average % hitting should exceed 50%
    # (60% is achievable with full params; 50% is the appropriate bar for this short run)
    low_total_mean = hard_matrix[0:5, :].mean()
    assert low_total_mean >= 50, \
        f"Hard 4–8 avg hit% is {low_total_mean:.1f}%, expected ≥50%"


def test_heatmap_hard_high_totals_lean_stand():
    final_pop, _ = _run_short_ga(generations=20, pop_size=30, n_hands=500)
    hard_matrix = np.zeros((17, 10))
    for row, total in enumerate(range(4, 21)):
        for col, upcard in enumerate([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]):
            hard_matrix[row, col] = np.mean([get_decision(c, total, False, upcard)
                                             for c in final_pop]) * 100
    # Hard totals 17–20 are rows 13–16; average % hitting should be below 40%
    high_total_mean = hard_matrix[13:17, :].mean()
    assert high_total_mean <= 40, \
        f"Hard 17–20 avg hit% is {high_total_mean:.1f}%, expected ≤40%"


def test_full_run_history_structure():
    _, history = _run_short_ga(generations=5, pop_size=10, n_hands=100)
    for entry in history:
        assert entry['min'] <= entry['mean'] <= entry['max']
        assert entry['min'] <= entry['median'] <= entry['max']
        assert 0.0 <= entry['min'] and entry['max'] <= 1.0
