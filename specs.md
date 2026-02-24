# Project Specification: Blackjack Strategy Optimizer via Genetic Algorithm

## Overview

Build a Python application that uses a genetic algorithm (GA) to evolve an optimal blackjack playing strategy. The system simulates thousands of blackjack hands, evaluates strategy fitness, and iteratively evolves better strategies over multiple generations. The target outcome is a strategy that approaches the theoretical optimal win rate of approximately 49.5%.

---

## Project Structure

The project must be organized as four Python modules plus a `requirements.txt`:

```
blackjack_ga/
├── simulator.py       # Blackjack game engine
├── chromosome.py      # Strategy encoding and lookup
├── ga.py              # Genetic algorithm logic
├── main.py            # Entry point; orchestrates GA loop and produces output figures
├── requirements.txt   # numpy, matplotlib
```

---

## Dependencies

- `numpy` — array operations, random number generation, chromosome representation
- `matplotlib` — output figures

No other third-party packages. Standard library modules (`random`, `copy`, etc.) may be used freely.

---

## Module Specifications

---

### `chromosome.py` — Strategy Encoding

#### Purpose
Encodes a complete blackjack playing strategy as a 260-bit binary numpy array. Provides indexing and lookup logic to retrieve the hit/stand decision for any game state.

#### Chromosome Structure

The chromosome is a 1D `numpy` array of dtype `uint8` with exactly 260 elements. Each element is either `0` (stand) or `1` (hit).

The chromosome is divided into two contiguous regions:

**Hard hand region (bits 0–169, 170 total)**

Covers all hard hand totals from 4 through 20 (17 values) × all dealer upcards from Ace through 10 (10 values).

Layout: row-major order where rows are player totals (4, 5, ..., 20) and columns are dealer upcards (Ace, 2, 3, ..., 10).

```
Index = (player_total - 4) * 10 + dealer_upcard_index
dealer_upcard_index: Ace=0, 2=1, 3=2, ..., 9=8, 10=9
```

**Soft hand region (bits 170–259, 90 total)**

Covers soft hand totals from soft 12 through soft 20 (9 values) × all dealer upcards (10 values). "Soft 12" means Ace + Ace (one ace counted as 11, total = 12). "Soft 20" means Ace + 9.

```
Index = 170 + (soft_total - 12) * 10 + dealer_upcard_index
```

#### Functions to implement

```python
def random_chromosome() -> np.ndarray:
    """Return a random 260-bit chromosome."""

def get_decision(chrom: np.ndarray, player_total: int, is_soft: bool, dealer_upcard: int) -> int:
    """
    Return 0 (stand) or 1 (hit) for the given game state.
    
    Parameters:
        player_total: integer sum of player's hand (4–20 for hard, 12–20 for soft)
        is_soft: True if the hand contains an ace counted as 11
        dealer_upcard: integer card value (Ace=1, 2–9, 10 for all ten-value cards)
    """
```

---

### `simulator.py` — Blackjack Game Engine

#### Purpose
Simulates complete blackjack hands according to the rules below. Evaluates a strategy chromosome over N hands and returns fitness.

#### Game Rules

- Each hand is dealt from a freshly shuffled standard 52-card deck (suits irrelevant; values are 1 (Ace), 2–9, 10 for all face cards and tens).
- Card values: number cards = face value, Jack/Queen/King = 10, Ace = 1 or 11.
- The dealer's hole card is not visible to the player strategy; only the dealer's face-up card is used for decision-making.
- Dealer stands on soft 17 (i.e., dealer stands if hand total is 17 or more, including a soft 17).
- Player may only **hit** or **stand**. No doubling, splitting, or insurance.
- A natural blackjack (two-card 21) for the player counts as a win. A natural for the dealer counts as a loss for the player. If both have naturals, it is a tie.
- Tie (push) counts as 0.5 wins in fitness calculation.
- Player busts (>21) = loss, dealer busts = win for player.

#### Ace handling

Track aces explicitly. A hand is "soft" if it contains at least one ace currently counted as 11 and the total is ≤ 21. When hitting would cause a bust and a soft ace exists, convert it to count as 1 (subtract 10) — the hand becomes hard.

#### Deck

Represent a deck as a list of 52 card values: four each of 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10. Shuffle with `numpy.random.shuffle` or `random.shuffle` before each hand.

#### Functions to implement

```python
def evaluate_fitness(chrom: np.ndarray, n_hands: int = 1000) -> float:
    """
    Simulate n_hands of blackjack using the given strategy chromosome.
    Returns fitness = (wins + 0.5 * ties) / (wins + losses + ties).
    """

def simulate_hand(chrom: np.ndarray, deck: list) -> str:
    """
    Simulate one hand using the given chromosome and a pre-shuffled deck.
    Returns 'win', 'loss', or 'tie'.
    Draws cards sequentially from the front of the deck list.
    """
```

---

### `ga.py` — Genetic Algorithm

#### Purpose
Implements the full genetic algorithm: population initialization, fitness evaluation, selection, crossover, mutation, and elitism.

#### Parameters (expose as constants or function arguments with these defaults)

| Parameter | Default | Description |
|---|---|---|
| `POPULATION_SIZE` | 100 | Number of individuals |
| `N_GENERATIONS` | 75 | Number of generations to evolve |
| `N_HANDS` | 1000 | Hands simulated per fitness evaluation |
| `MUTATION_RATE` | 0.01 | Probability of flipping each bit |
| `N_ELITES` | 2 | Top individuals that pass unchanged to next generation |
| `CROSSOVER_TYPE` | `'single_point'` | Crossover strategy (only single-point is required) |

#### Algorithm Steps (per generation)

1. **Evaluate fitness** — call `evaluate_fitness` for every individual in the population. Store results.
2. **Elitism** — copy the top `N_ELITES` individuals (by fitness) unchanged into the next generation.
3. **Roulette wheel selection** — assign selection probability proportional to fitness. Sample pairs of parents using this distribution (with replacement).
4. **Single-point crossover** — for each pair of parents, select a random crossover point uniformly from 1 to 258 (inclusive). Produce two offspring by swapping the tail segments. Both offspring enter the next generation.
5. **Mutation** — for each offspring, independently flip each bit with probability `MUTATION_RATE`.
6. **Replace population** — the new population consists of elites + offspring (trim or pad to exactly `POPULATION_SIZE` if needed).

#### Functions to implement

```python
def initialize_population(size: int = POPULATION_SIZE) -> list[np.ndarray]:
    """Return a list of `size` random chromosomes."""

def roulette_select(population: list, fitnesses: np.ndarray) -> np.ndarray:
    """Select one individual using fitness-proportional roulette wheel selection."""

def crossover(parent_a: np.ndarray, parent_b: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Single-point crossover. Returns two offspring."""

def mutate(chrom: np.ndarray, rate: float = MUTATION_RATE) -> np.ndarray:
    """Flip each bit independently with probability `rate`. Returns mutated copy."""

def evolve(population: list, fitnesses: np.ndarray) -> list[np.ndarray]:
    """Produce the next generation from the current population and its fitnesses."""

def run_ga() -> tuple[list[np.ndarray], list[dict]]:
    """
    Run the full genetic algorithm.
    Returns:
        final_population: list of chromosomes from the last generation
        history: list of dicts, one per generation, each containing:
            {'generation': int, 'min': float, 'max': float, 'mean': float, 'median': float}
    """
```

---

### `main.py` — Entry Point and Visualization

#### Purpose
Orchestrates the GA run and produces the two required output figures saved as PNG files.

#### Behavior

1. Call `run_ga()` from `ga.py` to get the final population and per-generation history.
2. Print a brief summary to stdout after each generation (generation number, max fitness, mean fitness). Example: `Gen 12/75 | Max: 0.4821 | Mean: 0.4634`
3. After all generations complete, produce Figure 1 and Figure 2 as described below.
4. Save both figures to the working directory as `fitness_over_generations.png` and `strategy_heatmap.png`.
5. Call `plt.show()` after saving so figures display interactively if run in a terminal.

---

## Output Specifications

### Figure 1: Fitness Over Generations

**File:** `fitness_over_generations.png`

**Type:** Line plot

**Axes:**
- X-axis: Generation number (0 to N_GENERATIONS - 1), labeled "Generation"
- Y-axis: Fitness (fraction of hands won), labeled "Fitness (win rate)", range approximately 0.35–0.55 with some padding

**Lines to plot (all on the same axes):**
- Maximum fitness across population — solid line, color red, label "Max"
- Mean fitness — solid line, color blue, label "Mean"
- Median fitness — dashed line, color green, label "Median"
- Minimum fitness — solid line, color orange, label "Min"

**Additional elements:**
- A horizontal dashed grey line at y = 0.495 labeled "Theoretical optimum (~49.5%)"
- Legend in the upper right
- Title: "Blackjack GA: Fitness Over Generations"
- Grid lines on (alpha 0.3)

**Expected behavior:** Min, mean, and median lines should start scattered around 0.42–0.46 and gradually converge upward. The max line will be noisy but trend toward 0.47–0.50. By generation 75, the mean and median should be clearly higher than at generation 0, likely in the 0.45–0.49 range. Perfect convergence to 0.495 is not expected but should be approached.

---

### Figure 2: Strategy Heatmap

**File:** `strategy_heatmap.png`

**Type:** Two-panel heatmap figure (side by side or stacked)

**Data:** For each (player total, dealer upcard) cell, compute the **percentage of individuals in the final population that recommend hitting** (i.e., mean of that chromosome bit across all 100 individuals × 100).

**Panel 1 — Hard Hands:**
- Rows: Player totals 4 through 20 (bottom to top, so 20 is at the top)
- Columns: Dealer upcard Ace, 2, 3, 4, 5, 6, 7, 8, 9, 10 (left to right)
- Title: "Hard Hands — % of Population Hitting"

**Panel 2 — Soft Hands:**
- Rows: Soft totals soft 12 through soft 20 (bottom to top)
- Columns: Same dealer upcards
- Title: "Soft Hands — % of Population Hitting"

**Color mapping:**
- Use `matplotlib` colormap `RdBu_r` (or manually map: 0% → pure blue `#0000FF`, 100% → pure red `#FF0000`, 50% → white/neutral). The `RdBu_r` colormap with `vmin=0`, `vmax=100` achieves this.
- Add a colorbar labeled "% Hitting"

**Axis labels:**
- X-axis tick labels: `['A', '2', '3', '4', '5', '6', '7', '8', '9', '10']`
- Y-axis tick labels: player totals as strings (e.g., `'4'` through `'20'` for hard; `'S12'` through `'S20'` for soft)
- X-axis label: "Dealer Upcard"
- Y-axis label: "Player Total"

**Annotations:** Annotate each cell with its integer percentage value (e.g., "87" or "12") in black text, font size 7.

**Overall figure title:** "Final Population Strategy Consensus (% Hitting)"

**Expected behavior:** The heatmap should closely resemble published blackjack basic strategy:
- Hard totals 17–20: nearly all blue (0–10% hitting) regardless of dealer upcard — the population should strongly converge to always stand.
- Hard totals 4–8: nearly all red (90–100% hitting) — always hit low totals.
- Hard totals 12–16: a visible gradient — more hitting (red) when dealer shows 7–Ace, more standing (blue) when dealer shows 4–6. This is the most interesting region and will show partial consensus (cells in the 40–70% range are expected and normal).
- Soft hands: most soft totals below soft 18 should lean toward hitting; soft 19–20 should lean toward standing.

---

## Implementation Notes for the Coding Agent

**Chromosome indexing:** Double-check the index arithmetic in `get_decision`. Off-by-one errors here will silently corrupt all fitness evaluations. Write a unit test or assertion that verifies a few known indices.

**Deck representation:** Do not use a single shuffled deck across multiple hands. Each hand must start with its own freshly shuffled 52-card deck to avoid running out of cards.

**Soft hand tracking during play:** When a player draws a card, maintain two variables: `total` (current best total ≤ 21 if possible) and `is_soft` (bool). When adding a card: if it's an ace, try counting it as 11 first; if total would exceed 21 and hand is soft, subtract 10 and set `is_soft = False`.

**Roulette wheel edge case:** If all fitness values are equal (e.g., at initialization), use uniform random selection rather than dividing by zero. Normalize by the sum of fitnesses.

**Performance:** With 100 individuals, 75 generations, and 1000 hands each, this is 7.5 million simulated hands. Pure Python loops will be slow (~5–10 minutes). To keep runtime under 2 minutes, vectorize the inner card-draw loop where possible, or use numpy for deck shuffling and card sampling. The simulation loop itself (hit/stand decisions) is inherently sequential per hand, but the outer loop over 1000 hands can be parallelized with a simple list comprehension or numpy-batched approach if clever.

**Reproducibility:** Set a numpy and random seed at the top of `main.py` (default `seed=42`) so results are reproducible. Expose it as a constant that can be changed.

**No hard-coded strategy:** The chromosome must determine all decisions. Do not inject basic strategy knowledge anywhere in the code.

---

## Acceptance Criteria

- [ ] All four modules are present and importable without errors.
- [ ] `python main.py` runs end-to-end in under 5 minutes on a modern laptop.
- [ ] Two PNG files are produced: `fitness_over_generations.png` and `strategy_heatmap.png`.
- [ ] The fitness plot shows at least some upward trend in mean/max fitness over generations.
- [ ] The heatmap shows strong convergence (>90% consensus) on always-hit for totals ≤ 8 and always-stand for totals ≥ 17.
- [ ] The hard 12–16 region of the heatmap shows a visible dealer-upcard-dependent gradient.
- [ ] No third-party packages beyond numpy and matplotlib are used.