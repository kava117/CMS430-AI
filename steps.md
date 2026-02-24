# Implementation Steps: Blackjack Strategy Optimizer via Genetic Algorithm

## Step 1: Set Up Project Structure

Create the project directory and files:

```
blackjack_ga/
├── simulator.py
├── chromosome.py
├── ga.py
├── main.py
├── requirements.txt
```

In `requirements.txt`, add:
```
numpy
matplotlib
```

### Tests — Step 1

```python
import os

def test_step1_files_exist():
    files = ['simulator.py', 'chromosome.py', 'ga.py', 'main.py', 'requirements.txt']
    for f in files:
        assert os.path.exists(f), f"Missing file: {f}"

def test_step1_requirements():
    with open('requirements.txt') as f:
        contents = f.read()
    assert 'numpy' in contents
    assert 'matplotlib' in contents
```

**Pass criteria:** All five files exist and `requirements.txt` lists both `numpy` and `matplotlib`. Do not proceed until this passes.

---

## Step 2: Implement `chromosome.py`

1. Import `numpy as np`.
2. Implement `random_chromosome()`:
   - Return `np.random.randint(0, 2, size=260, dtype=np.uint8)`.
3. Implement `get_decision(chrom, player_total, is_soft, dealer_upcard)`:
   - Compute `dealer_upcard_index`: Ace=0, 2→1, 3→2, ..., 9→8, 10→9.
   - If `is_soft`: `index = 170 + (player_total - 12) * 10 + dealer_upcard_index`
   - Else: `index = (player_total - 4) * 10 + dealer_upcard_index`
   - Return `int(chrom[index])`.
4. Verify index arithmetic manually:
   - Hard 4 vs Ace → index 0
   - Hard 20 vs 10 → index 169
   - Soft 12 vs Ace → index 170
   - Soft 20 vs 10 → index 259

### Tests — Step 2

```python
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
```

**Pass criteria:** All 8 tests pass. Index arithmetic must be exact — any off-by-one here silently corrupts all downstream fitness results. Do not proceed until this passes.

---

## Step 3: Implement `simulator.py`

1. Import `numpy as np`, `random`, and `chromosome` functions.
2. Define a helper `make_deck()` that returns a list of 52 card values: four each of 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10.
3. Define a helper `hand_value(cards)` that returns `(total, is_soft)`:
   - Count aces. Start with non-ace sum. Add aces one at a time, counting as 11 if total stays ≤ 21, else count as 1.
   - `is_soft` is True if at least one ace is counted as 11 and total ≤ 21.
4. Implement `simulate_hand(chrom, deck)`:
   - Draw cards sequentially from the front of `deck` using `pop(0)` or an index pointer.
   - Deal: player card 1, dealer card 1, player card 2, dealer face-up card 2. The dealer's hole card (first card) is not used for decisions.
   - Check for naturals (two-card 21): if player has blackjack and dealer does not → `'win'`; dealer has blackjack and player does not → `'loss'`; both → `'tie'`.
   - Player loop: while player total < 21, call `get_decision(chrom, total, is_soft, dealer_upcard)`. If 1 (hit), draw next card and update hand. If 0 (stand), break.
   - If player total > 21 → `'loss'`.
   - Dealer loop: dealer reveals hole card, plays by fixed rule — hit if total < 17 (including soft 17, dealer stands on soft 17, meaning stand if total ≥ 17).
   - If dealer busts → `'win'`. Compare totals: player > dealer → `'win'`; player < dealer → `'loss'`; equal → `'tie'`.
5. Implement `evaluate_fitness(chrom, n_hands=1000)`:
   - For each of `n_hands`: create a fresh deck, shuffle with `random.shuffle(deck)`, call `simulate_hand`.
   - Count wins, losses, ties.
   - Return `(wins + 0.5 * ties) / n_hands`.

### Tests — Step 3

```python
import numpy as np
import random
from simulator import make_deck, simulate_hand, evaluate_fitness
from chromosome import random_chromosome

def test_deck_length():
    assert len(make_deck()) == 52

def test_deck_composition():
    deck = make_deck()
    assert deck.count(1) == 4
    for v in range(2, 10):
        assert deck.count(v) == 4
    assert deck.count(10) == 16  # tens + J + Q + K

def test_simulate_hand_returns_valid_outcome():
    chrom = random_chromosome()
    deck = make_deck()
    random.shuffle(deck)
    result = simulate_hand(chrom, deck)
    assert result in ('win', 'loss', 'tie')

def test_always_stand_strategy_fitness_range():
    # A strategy that always stands should have fitness between 0.35 and 0.50
    chrom = np.zeros(260, dtype=np.uint8)  # all stand
    fitness = evaluate_fitness(chrom, n_hands=2000)
    assert 0.35 <= fitness <= 0.50, f"Unexpected fitness: {fitness}"

def test_always_hit_strategy_busts_often():
    # Always hitting produces many busts; fitness should be below 0.45
    chrom = np.ones(260, dtype=np.uint8)   # all hit
    fitness = evaluate_fitness(chrom, n_hands=2000)
    assert fitness < 0.45, f"Always-hit fitness too high: {fitness}"

def test_evaluate_fitness_bounds():
    chrom = random_chromosome()
    fitness = evaluate_fitness(chrom, n_hands=500)
    assert 0.0 <= fitness <= 1.0

def test_evaluate_fitness_uses_fresh_deck_each_hand():
    # Run evaluate_fitness twice with same seed; results should match (deterministic)
    chrom = np.zeros(260, dtype=np.uint8)
    random.seed(0)
    f1 = evaluate_fitness(chrom, n_hands=100)
    random.seed(0)
    f2 = evaluate_fitness(chrom, n_hands=100)
    assert f1 == f2, "evaluate_fitness is not deterministic given same seed"

def test_natural_blackjack_player_wins():
    # Force a natural: player gets Ace + 10, dealer gets 2 + 3
    chrom = np.zeros(260, dtype=np.uint8)
    deck = [1, 2, 10, 3] + make_deck()  # player: 1,10; dealer: 2,3
    result = simulate_hand(chrom, deck)
    assert result == 'win'

def test_natural_blackjack_dealer_wins():
    # Dealer gets Ace + 10, player gets 5 + 6
    chrom = np.zeros(260, dtype=np.uint8)
    deck = [5, 1, 6, 10] + make_deck()  # player: 5,6; dealer: 1,10
    result = simulate_hand(chrom, deck)
    assert result == 'loss'
```

**Pass criteria:** All 9 tests pass. The always-stand fitness bound (0.35–0.50) and always-hit bust check are statistical — run with `n_hands=2000` to reduce flakiness. Do not proceed until this passes.

---

## Step 4: Implement `ga.py`

1. Import `numpy as np`, `copy`, and `evaluate_fitness`, `random_chromosome` from other modules.
2. Define module-level constants:
   ```python
   POPULATION_SIZE = 100
   N_GENERATIONS = 75
   N_HANDS = 1000
   MUTATION_RATE = 0.01
   N_ELITES = 2
   CROSSOVER_TYPE = 'single_point'
   ```
3. Implement `initialize_population(size=POPULATION_SIZE)`:
   - Return `[random_chromosome() for _ in range(size)]`.
4. Implement `roulette_select(population, fitnesses)`:
   - Compute `total = fitnesses.sum()`. If `total == 0`, select uniformly.
   - Otherwise, compute probabilities and use `np.random.choice(len(population), p=probs)`.
   - Return `population[index].copy()`.
5. Implement `crossover(parent_a, parent_b)`:
   - Pick a random crossover point in range `[1, 258]` inclusive.
   - `child_a = np.concatenate([parent_a[:point], parent_b[point:]])`
   - `child_b = np.concatenate([parent_b[:point], parent_a[point:]])`
   - Return `(child_a, child_b)`.
6. Implement `mutate(chrom, rate=MUTATION_RATE)`:
   - Create a copy of `chrom`.
   - For each bit, flip it with probability `rate`: `mask = np.random.random(260) < rate; chrom_copy ^= mask.astype(np.uint8)`.
   - Return the mutated copy.
7. Implement `evolve(population, fitnesses)`:
   - Sort population by fitness descending; copy top `N_ELITES` unchanged.
   - Fill remaining slots: repeatedly select two parents via `roulette_select`, apply `crossover`, then `mutate` each offspring.
   - Trim or pad to exactly `POPULATION_SIZE`. Return new population.
8. Implement `run_ga()`:
   - Initialize population.
   - For each generation 0 to `N_GENERATIONS - 1`:
     - Evaluate fitness for every individual; store as `np.ndarray`.
     - Record `{'generation': g, 'min': ..., 'max': ..., 'mean': ..., 'median': ...}` into `history`.
     - Evolve population.
   - Return `(population, history)`.

### Tests — Step 4

```python
import numpy as np
from ga import (initialize_population, roulette_select, crossover, mutate,
                evolve, POPULATION_SIZE, N_ELITES, MUTATION_RATE)

def test_initialize_population_size():
    pop = initialize_population(50)
    assert len(pop) == 50

def test_initialize_population_default_size():
    pop = initialize_population()
    assert len(pop) == POPULATION_SIZE

def test_initialize_population_chromosome_shape():
    pop = initialize_population(10)
    for chrom in pop:
        assert chrom.shape == (260,)

def test_roulette_select_returns_copy():
    pop = initialize_population(10)
    fitnesses = np.random.uniform(0.4, 0.5, size=10)
    selected = roulette_select(pop, fitnesses)
    assert selected.shape == (260,)
    assert selected is not pop[0]  # must be a copy

def test_roulette_select_uniform_when_all_zero():
    pop = initialize_population(10)
    fitnesses = np.zeros(10)
    selected = roulette_select(pop, fitnesses)  # should not raise ZeroDivisionError
    assert selected.shape == (260,)

def test_crossover_output_shapes():
    pop = initialize_population(2)
    c1, c2 = crossover(pop[0], pop[1])
    assert c1.shape == (260,)
    assert c2.shape == (260,)

def test_crossover_combines_parents():
    a = np.zeros(260, dtype=np.uint8)
    b = np.ones(260, dtype=np.uint8)
    c1, c2 = crossover(a, b)
    # Each child must be composed entirely of 0s and 1s from parents
    assert set(c1).issubset({0, 1})
    assert set(c2).issubset({0, 1})
    # Together they contain all bits from both parents
    assert not np.array_equal(c1, a) or not np.array_equal(c2, b)

def test_mutate_returns_copy():
    chrom = np.zeros(260, dtype=np.uint8)
    mutated = mutate(chrom, rate=0.0)
    assert mutated is not chrom
    assert np.array_equal(mutated, chrom)

def test_mutate_zero_rate_unchanged():
    chrom = np.zeros(260, dtype=np.uint8)
    mutated = mutate(chrom, rate=0.0)
    assert np.array_equal(mutated, chrom)

def test_mutate_full_rate_all_flipped():
    chrom = np.zeros(260, dtype=np.uint8)
    mutated = mutate(chrom, rate=1.0)
    assert np.all(mutated == 1)

def test_evolve_population_size_preserved():
    pop = initialize_population(POPULATION_SIZE)
    fitnesses = np.random.uniform(0.4, 0.5, size=POPULATION_SIZE)
    new_pop = evolve(pop, fitnesses)
    assert len(new_pop) == POPULATION_SIZE

def test_evolve_elites_preserved():
    pop = initialize_population(POPULATION_SIZE)
    fitnesses = np.random.uniform(0.4, 0.5, size=POPULATION_SIZE)
    # Identify the top N_ELITES
    top_indices = np.argsort(fitnesses)[-N_ELITES:][::-1]
    top_chroms = [pop[i].copy() for i in top_indices]
    new_pop = evolve(pop, fitnesses)
    # At least one elite must appear unchanged in the new population
    found = sum(any(np.array_equal(e, c) for c in new_pop) for e in top_chroms)
    assert found == N_ELITES

def test_run_ga_history_length():
    # Run a tiny GA to verify structure (reduced params)
    import ga as ga_module
    orig_gen = ga_module.N_GENERATIONS
    orig_size = ga_module.POPULATION_SIZE
    orig_hands = ga_module.N_HANDS
    ga_module.N_GENERATIONS = 3
    ga_module.POPULATION_SIZE = 10
    ga_module.N_HANDS = 50
    final_pop, history = ga_module.run_ga()
    ga_module.N_GENERATIONS = orig_gen
    ga_module.POPULATION_SIZE = orig_size
    ga_module.N_HANDS = orig_hands
    assert len(history) == 3
    assert all(k in history[0] for k in ('generation', 'min', 'max', 'mean', 'median'))
    assert len(final_pop) == 10
```

**Pass criteria:** All 13 tests pass. Pay special attention to `test_roulette_select_uniform_when_all_zero` (no division by zero) and `test_evolve_elites_preserved` (elitism is correctly implemented). Do not proceed until this passes.

---

## Step 5: Implement `main.py`

1. Import `numpy as np`, `matplotlib.pyplot as plt`, `run_ga` from `ga`, and `get_decision` from `chromosome`.
2. Set seeds at the top:
   ```python
   SEED = 42
   import random; random.seed(SEED)
   np.random.seed(SEED)
   ```
3. Call `run_ga()`, storing `final_population, history`.
4. After each generation (inside `run_ga` or via a callback), print:
   `Gen {g}/{N_GENERATIONS} | Max: {max:.4f} | Mean: {mean:.4f}`
   - Simplest approach: print from inside `run_ga()` before returning, or restructure so `main.py` controls the loop.
5. **Figure 1 — Fitness Over Generations:**
   - Extract `generations`, `maxes`, `means`, `medians`, `mins` lists from `history`.
   - Plot all four lines on one axes with the specified colors and line styles.
   - Add horizontal dashed grey line at y=0.495 labeled `"Theoretical optimum (~49.5%)"`.
   - Set title, axis labels, legend (upper right), grid (alpha=0.3).
   - Save as `fitness_over_generations.png`.
6. **Figure 2 — Strategy Heatmap:**
   - Compute a `(17, 10)` hard-hand matrix and `(9, 10)` soft-hand matrix:
     - For each cell, compute mean bit value across all 100 final chromosomes × 100.
   - Create a figure with two subplots (side by side or stacked).
   - For each panel, call `ax.imshow(data, cmap='RdBu_r', vmin=0, vmax=100, aspect='auto')`.
   - Flip the Y-axis so lowest total is at the bottom (`ax.invert_yaxis()` or set `origin='lower'` in imshow).
   - Set X tick labels to `['A','2','3','4','5','6','7','8','9','10']`.
   - Set Y tick labels to `['4','5',...,'20']` for hard and `['S12','S13',...,'S20']` for soft.
   - Annotate each cell with its integer percentage value, font size 7, black text, centered.
   - Add a colorbar labeled `"% Hitting"`.
   - Set overall figure title and per-panel titles as specified.
   - Save as `strategy_heatmap.png`.
7. Call `plt.show()` after saving both figures.

### Tests — Step 5

```python
import os
import subprocess
import time

def test_main_runs_without_error():
    result = subprocess.run(['python', 'main.py'], capture_output=True, text=True, timeout=300)
    assert result.returncode == 0, f"main.py exited with error:\n{result.stderr}"

def test_main_completes_within_time_limit():
    start = time.time()
    subprocess.run(['python', 'main.py'], capture_output=True, timeout=300)
    elapsed = time.time() - start
    assert elapsed < 300, f"main.py took {elapsed:.1f}s — exceeds 5-minute limit"

def test_fitness_png_exists():
    assert os.path.exists('fitness_over_generations.png'), "Missing fitness_over_generations.png"

def test_heatmap_png_exists():
    assert os.path.exists('strategy_heatmap.png'), "Missing strategy_heatmap.png"

def test_fitness_png_is_nonempty():
    size = os.path.getsize('fitness_over_generations.png')
    assert size > 1000, f"fitness_over_generations.png appears empty ({size} bytes)"

def test_heatmap_png_is_nonempty():
    size = os.path.getsize('strategy_heatmap.png')
    assert size > 1000, f"strategy_heatmap.png appears empty ({size} bytes)"

def test_stdout_contains_generation_lines():
    result = subprocess.run(['python', 'main.py'], capture_output=True, text=True, timeout=300)
    lines = result.stdout.strip().split('\n')
    gen_lines = [l for l in lines if l.startswith('Gen ')]
    assert len(gen_lines) == 75, f"Expected 75 generation lines, got {len(gen_lines)}"
    assert 'Max:' in gen_lines[0] and 'Mean:' in gen_lines[0]
```

**Pass criteria:** All 7 tests pass. Both PNG files must exist and be non-trivially sized. The stdout must contain exactly 75 generation summary lines. Do not proceed to Step 6 until this passes.

---

## Step 6: Verify Final Output Quality

1. Run `python main.py` from inside the `blackjack_ga/` directory.
2. Confirm no import errors and the run completes within 5 minutes.
3. Confirm two PNG files are created: `fitness_over_generations.png` and `strategy_heatmap.png`.
4. Inspect Figure 1: mean/max fitness should show an upward trend over 75 generations.
5. Inspect Figure 2:
   - Hard totals 4–8: nearly all red (≥90% hitting).
   - Hard totals 17–20: nearly all blue (≤10% hitting).
   - Hard totals 12–16: visible gradient — more red when dealer shows 7–Ace, more blue when dealer shows 4–6.
   - Soft totals below S18: lean red; S19–S20: lean blue.
6. Spot-check `get_decision` index arithmetic with a few known values to rule out off-by-one bugs.

### Tests — Step 6

```python
import numpy as np
import random
from chromosome import random_chromosome, get_decision
from simulator import evaluate_fitness
from ga import run_ga, POPULATION_SIZE, N_GENERATIONS

# Run a short GA and verify convergence behavior
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
    # Mean fitness should not degrade over 10 generations
    assert late_mean >= early_mean - 0.02, \
        f"Mean fitness regressed from {early_mean:.4f} to {late_mean:.4f}"

def test_max_fitness_above_random_baseline():
    _, history = _run_short_ga(generations=10, pop_size=20, n_hands=300)
    final_max = history[-1]['max']
    assert final_max >= 0.40, f"Max fitness {final_max:.4f} is below expected minimum of 0.40"

def test_heatmap_hard_low_totals_lean_hit(tmp_path):
    # A converged population should mostly hit on hard 4–8
    final_pop, _ = _run_short_ga(generations=20, pop_size=30, n_hands=500)
    hard_matrix = np.zeros((17, 10))
    for row, total in enumerate(range(4, 21)):
        for col, upcard in enumerate([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]):
            hard_matrix[row, col] = np.mean([get_decision(c, total, False, upcard)
                                             for c in final_pop]) * 100
    # Hard totals 4–8 are rows 0–4; average % hitting should exceed 60%
    low_total_mean = hard_matrix[0:5, :].mean()
    assert low_total_mean >= 60, \
        f"Hard 4–8 avg hit% is {low_total_mean:.1f}%, expected ≥60%"

def test_heatmap_hard_high_totals_lean_stand(tmp_path):
    # A converged population should mostly stand on hard 17–20
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
```

**Pass criteria:** All 5 tests pass. The convergence tests use reduced parameters so they run quickly, but they validate that the GA is actually learning — not just running without crashing. The heatmap shape tests confirm the evolved strategy approaches known blackjack logic. The project is complete when all tests across all steps pass.
