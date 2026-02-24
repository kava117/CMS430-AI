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

---

## Step 6: Verify and Test

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
