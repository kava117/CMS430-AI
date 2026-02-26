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

---

---

# Part 2 Extension: Card Counting and Betting Strategy

## Overview

Extend the basic version to evolve a card counting system and betting strategy. The player now tracks cards as they are dealt from a multi-deck shoe and adjusts bet sizes based on the running count. The GA must now simultaneously evolve three things: a hit/stand strategy, a card counting system (which values to assign each card rank), and a bet sizing schedule (how aggressively to bet at each count level).

---

## Project Structure

The extension lives in a separate subdirectory alongside the original:

```
blackjack_ga/                          # Original (unchanged)
├── simulator.py
├── chromosome.py
├── ga.py
├── main.py
└── requirements.txt

blackjack_ga_counting/                 # Extension (new)
├── simulator.py       # Extended game engine: shoe, penetration, bankroll, betting
├── chromosome.py      # Extended chromosome: 260 + 22 + 12 = 294 bits
├── ga.py              # GA logic adapted for new chromosome length and fitness function
├── main.py            # Entry point; orchestrates GA and produces all output figures
└── requirements.txt   # numpy, matplotlib (same dependencies)
```

All modules in `blackjack_ga_counting/` are independent of the originals — do not import from `blackjack_ga/`. The extension is a self-contained project.

---

## Dependencies

Same as Part 1: `numpy` and `matplotlib` only. No other third-party packages.

---

## Game Rules (replaces and extends Part 1 rules)

- Hands are dealt from a **6-deck shoe** (312 cards: six standard 52-card decks combined).
- Card values are identical to Part 1: Ace = 1 or 11, 2–9 = face value, 10/J/Q/K = 10.
- Each fitness evaluation begins with a freshly shuffled 6-deck shoe.
- Cards are dealt sequentially from the shoe. When **75% penetration** is reached (234 or more cards dealt from the shoe), the dealer completes the current hand in progress, then reshuffles the shoe before starting the next hand.
- The player starts each fitness evaluation with a **bankroll of $1,000**.
- **Minimum bet: $1. Maximum bet: $8.**
- **Blackjack pays 3:2** — a natural 21 on the initial two cards wins 1.5× the bet (e.g., a $2 bet wins $3, returning $5 total).
- If both player and dealer have blackjack, it is a tie (push): bet is returned.
- If the player's **bankroll reaches $0** at any point, the session ends immediately regardless of how many hands have been played. Fitness is 0.
- Player may only hit or stand. No doubling, splitting, or insurance.
- Dealer stands on soft 17.
- Player busts (>21) = loss. Dealer busts = player wins.
- Tie (push) = bet returned, bankroll unchanged.

---

## Module Specifications

---

### `chromosome.py` — Extended Strategy Encoding

#### Purpose
Encodes a 294-bit chromosome representing three components: play strategy, card count values, and bet multipliers. Provides all encoding, decoding, and lookup functions.

#### Chromosome Structure

The chromosome is a 1D `numpy` array of dtype `uint8` with exactly **294 elements**, divided into three contiguous regions:

---

**Component 1: Play Strategy (bits 0–259, 260 bits)**

Identical to Part 1. Hard hand matrix (170 bits) followed by soft hand matrix (90 bits). Indexing and lookup are unchanged.

---

**Component 2: Card Count Values (bits 260–281, 22 bits)**

Encodes a count value assignment for each of 11 card ranks: Ace, 2, 3, 4, 5, 6, 7, 8, 9, and 10 (all ten-valued cards use the same value). Each rank uses **2 bits** to encode one of three values:

```
Bit pair | Decoded value
-----------------------
  00     |    -1
  01     |     0
  10     |    +1
  11     |     0  (treat as 0; unused encoding)
```

Layout: rank values stored in order Ace, 2, 3, 4, 5, 6, 7, 8, 9, 10, each occupying 2 bits.

```
Bit offset for rank r (0-indexed, Ace=0, 2=1, ..., 10=9):
start_bit = 260 + r * 2
count_value = decode(bits[start_bit : start_bit + 2])
```

---

**Component 3: Bet Multipliers (bits 282–293, 12 bits)**

Encodes a bet multiplier (1–8) for each of four true count ranges. Each range uses **3 bits** encoding an integer 0–7, which maps to multipliers 1–8 (i.e., `multiplier = encoded_value + 1`).

True count ranges and their bit offsets within Component 3:

```
Range         | Offset within Component 3 | Bit offset in chromosome
---------------------------------------------------------------------------
<= -2         | 0                         | 282
-1 to +1      | 3                         | 285
+2 to +4      | 6                         | 288
>= +5         | 9                         | 291
```

Decoding:
```
bits = chrom[282 + range_index * 3 : 282 + range_index * 3 + 3]
encoded = bits[0] * 4 + bits[1] * 2 + bits[2]   # big-endian 3-bit integer
multiplier = encoded + 1   # maps 0–7 → 1–8
```

---

#### Functions to implement

```python
def random_chromosome() -> np.ndarray:
    """Return a random 294-bit chromosome."""

def get_decision(chrom: np.ndarray, player_total: int, is_soft: bool, dealer_upcard: int) -> int:
    """
    Return 0 (stand) or 1 (hit). Identical logic to Part 1.
    Reads from bits 0–259 only.
    """

def get_count_values(chrom: np.ndarray) -> dict:
    """
    Decode and return the count value for each card rank.
    Returns a dict mapping card value (int) to count value (-1, 0, or +1):
      {1: cv_ace, 2: cv_2, ..., 9: cv_9, 10: cv_10}
    All ten-valued cards (10, J, Q, K) share the count value for rank 10.
    """

def get_bet_multipliers(chrom: np.ndarray) -> list[int]:
    """
    Decode and return the four bet multipliers as a list of ints (1–8).
    Order: [mult_for_<=−2, mult_for_−1_to_+1, mult_for_+2_to_+4, mult_for_>=+5]
    """
```

---

### `simulator.py` — Extended Game Engine

#### Purpose
Simulates blackjack sessions using a 6-deck shoe with card counting, penetration logic, bankroll tracking, and bet sizing.

#### Shoe Management

Represent the shoe as a list of 312 card values (six copies of the standard 52-card deck). Shuffle once at the start of each fitness evaluation. Track how many cards have been dealt with a `cards_dealt` counter. When `cards_dealt >= 234`, set a `reshuffle_pending` flag. After the current hand completes, reshuffle the shoe and reset `cards_dealt = 0` and `running_count = 0` before the next hand.

#### Card Counting During Play

Maintain a `running_count` integer throughout the session (reset to 0 only on reshuffle). Every time a card is revealed — including both player cards on the initial deal, the dealer's face-up card, and every subsequent hit card for both player and dealer — add that card's count value (from the chromosome's Component 2) to `running_count`. The dealer's hole card is **not** revealed until the dealer plays; add its count value only when it is turned face-up (i.e., when the dealer begins playing their hand).

#### True Count Calculation

```python
decks_remaining = (len(shoe) - cards_dealt) / 52
true_count = round(running_count / decks_remaining)
```

Guard against `decks_remaining <= 0` (should not occur if penetration logic is correct, but add a safety check).

#### Bet Sizing

At the start of each hand, before any cards are dealt:

```python
true_count = calculate_true_count(running_count, cards_dealt, shoe_size=312)

if true_count <= -2:
    multiplier = bet_multipliers[0]
elif true_count <= 1:
    multiplier = bet_multipliers[1]
elif true_count <= 4:
    multiplier = bet_multipliers[2]
else:
    multiplier = bet_multipliers[3]

bet = multiplier * 1   # $1 base unit
bet = min(bet, bankroll)   # cap at available bankroll
```

#### Bankroll Updates

- Win (non-blackjack): `bankroll += bet`
- Loss: `bankroll -= bet`
- Tie: `bankroll` unchanged
- Player blackjack: `bankroll += 1.5 * bet` (3:2 payout; use `floor` if bankroll must be integer, but float is acceptable)
- Dealer blackjack: `bankroll -= bet`
- Both blackjack (tie): `bankroll` unchanged

#### Functions to implement

```python
def evaluate_fitness(chrom: np.ndarray, n_hands: int = 1000) -> float:
    """
    Simulate up to n_hands of blackjack using the given chromosome.
    Manages shoe, penetration, running count, bankroll, and bet sizing.
    Returns final bankroll as fitness (float).
    Returns 0.0 if bankroll reaches $0 before n_hands are complete.
    """

def simulate_hand(
    chrom: np.ndarray,
    shoe: list,
    cards_dealt: int,
    running_count: int,
    bankroll: float,
    bet: float
) -> tuple[str, int, int, float]:
    """
    Simulate one hand. Draws cards from shoe starting at index cards_dealt.
    Updates running_count as each card is revealed.
    Returns:
        outcome:       'win', 'loss', or 'tie'
        cards_dealt:   updated count after this hand
        running_count: updated running count after this hand
        bankroll:      updated bankroll after this hand
    """

def simulate_session(chrom: np.ndarray, n_hands: int = 1000) -> list[float]:
    """
    Simulate a full session and return the bankroll after each hand as a list.
    Used by main.py to generate the bankroll-over-time plot for the best individual.
    Returns a list of length <= n_hands (may be shorter if bankroll hits 0).
    The first element is the bankroll after hand 1; element 0 of the returned
    list is not the starting bankroll.
    """
```

---

### `ga.py` — Genetic Algorithm (Extended)

#### Purpose
Identical GA logic to Part 1, adapted for the 294-bit chromosome and the new fitness function (bankroll instead of win rate).

#### Parameters

| Parameter | Default | Description |
|---|---|---|
| `POPULATION_SIZE` | 100 | Number of individuals |
| `N_GENERATIONS` | 75 | Number of generations |
| `N_HANDS` | 1000 | Hands per fitness evaluation |
| `MUTATION_RATE` | 0.01 | Per-bit flip probability |
| `N_ELITES` | 2 | Individuals passed unchanged each generation |

#### Key differences from Part 1

- Chromosome length is 294 bits (not 260). Crossover point is uniformly sampled from 1 to 292 inclusive.
- Fitness values are raw bankroll amounts (floats, e.g. 800.0, 1200.0, 0.0) rather than win rates. Roulette wheel selection must handle this: if all fitnesses are 0 (edge case), use uniform selection. If some fitnesses are negative (should not occur given bankroll floor of 0), clip to 0 before computing selection weights.
- All other logic (elitism, crossover, mutation, population replacement) is identical to Part 1.

#### Functions to implement

Same signatures as Part 1, adapted for 294-bit chromosomes and bankroll fitness:

```python
def initialize_population(size: int = POPULATION_SIZE) -> list[np.ndarray]
def roulette_select(population: list, fitnesses: np.ndarray) -> np.ndarray
def crossover(parent_a: np.ndarray, parent_b: np.ndarray) -> tuple[np.ndarray, np.ndarray]
def mutate(chrom: np.ndarray, rate: float = MUTATION_RATE) -> np.ndarray
def evolve(population: list, fitnesses: np.ndarray) -> list[np.ndarray]
def run_ga() -> tuple[list[np.ndarray], list[dict]]
```

`run_ga()` returns the same structure as Part 1: `(final_population, history)` where each history dict contains `{'generation', 'min', 'max', 'mean', 'median'}` — all in raw bankroll units ($).

---

### `main.py` — Entry Point and Visualization

#### Purpose
Orchestrates the GA run and produces all four output figures.

#### Behavior

1. Set `numpy` and `random` seeds at the top (`SEED = 42`).
2. Call `run_ga()` to get `final_population` and `history`.
3. Print a per-generation summary to stdout. Example: `Gen 15/75 | Max: $1243.50 | Mean: $987.20`
4. Identify the best individual in `final_population` (highest fitness).
5. Produce and save Figures 1–4 as described below.
6. Call `plt.show()` after all figures are saved.

---

## Output Specifications

---

### Figure 1: Fitness (Bankroll) Over Generations

**File:** `fitness_over_generations.png`

**Type:** Line plot

**Axes:**
- X-axis: Generation number (0 to N_GENERATIONS − 1), labeled `"Generation"`
- Y-axis: Bankroll in dollars, labeled `"Final Bankroll ($)"`. Use raw dollar values — do not normalize. Add a horizontal dashed line at y = 1000 labeled `"Starting bankroll ($1,000)"`.

**Lines to plot:**
- Max bankroll — solid red, label `"Max"`
- Mean bankroll — solid blue, label `"Mean"`
- Median bankroll — dashed green, label `"Median"`
- Min bankroll — solid orange, label `"Min"`

**Additional elements:** Legend upper right, title `"Blackjack Counting GA: Bankroll Over Generations"`, grid on (alpha 0.3).

**Expected behavior:** Early generations will be noisy with high variance — bankrolls ranging from $0 (bust) to perhaps $1,400+. The mean and median should trend upward and stabilize above $1,000 by later generations as bet sizing and count values co-evolve. The max line will be very noisy throughout due to the high variance of blackjack. Do not expect clean convergence; modest upward drift in the mean is a success.

---

### Figure 2: Strategy Heatmap

**File:** `strategy_heatmap.png`

Identical specification to Part 1 Figure 2. Extract the play strategy bits (0–259) from each chromosome in the final population, compute population consensus per cell, and render the two-panel (hard/soft) heatmap. Expected behavior is the same as Part 1.

---

### Figure 3: Evolved Count Values vs. Hi-Lo

**File:** `count_values.png`

**Type:** Grouped bar chart

**Data:** For each of the 10 card ranks (Ace, 2, 3, 4, 5, 6, 7, 8, 9, 10), compute two values:
1. **Evolved consensus count value**: the mean decoded count value across all individuals in the final population for that rank (a float between −1 and +1).
2. **Hi-Lo reference value**: the known optimal hi-lo count values: `{Ace: -1, 2: +1, 3: +1, 4: +1, 5: +1, 6: +1, 7: 0, 8: 0, 9: 0, 10: -1}`.

**Chart layout:**
- X-axis: Card ranks `['A', '2', '3', '4', '5', '6', '7', '8', '9', '10']`
- Y-axis: Count value, range −1.2 to +1.2, labeled `"Count Value"`
- Two bar groups per rank: evolved consensus (color steel blue) and hi-lo reference (color coral/salmon)
- A horizontal dashed line at y = 0
- Legend identifying the two bar series
- Title: `"Evolved Count Values vs. Hi-Lo System"`
- Annotate each evolved bar with its numeric value rounded to 2 decimal places (e.g., `"+0.72"`) above the bar

**Expected behavior:** A well-evolved population should show count values that broadly agree with hi-lo: low cards (2–6) should have positive consensus values, high cards (Ace, 10) should have negative values, and middle cards (7–9) should be near zero. The agreement will be imperfect — some ranks may deviate — but the overall pattern should be recognizable as a hi-lo-like system.

---

### Figure 4: Best Individual — Bankroll Over Time

**File:** `bankroll_over_time.png`

**Type:** Line plot

**Data:** Call `simulate_session(best_chromosome, n_hands=1000)` from `simulator.py` using the best individual from the final population. This returns a list of bankroll values after each hand.

**Axes:**
- X-axis: Hand number (1 to len(bankroll_history)), labeled `"Hand"`
- Y-axis: Bankroll in dollars, labeled `"Bankroll ($)"`

**Elements:**
- Single line showing bankroll over time — color `"steelblue"`, linewidth 1.5
- Horizontal dashed line at y = 1000 (starting bankroll) in grey, labeled `"Starting bankroll"`
- Fill between the bankroll line and y = 1000: use `ax.fill_between` with green (alpha 0.15) where bankroll > 1000 and red (alpha 0.15) where bankroll < 1000, to visually distinguish profit and loss zones
- Title: `"Best Individual: Bankroll Over 1,000 Hands"`
- Annotate the final bankroll value in the lower right of the plot area (e.g., `"Final: $1,142"`)
- Grid on (alpha 0.3)

**Expected behavior:** The line will be highly volatile — blackjack has high hand-to-hand variance even with a counting advantage. The player may dip below $1,000 frequently. The fill coloring makes it easy to see net profit/loss zones. The best individual should more often finish above $1,000 than below, but a single 1,000-hand sample may end below starting bankroll even for a strong strategy due to variance.

---

## Implementation Notes for the Coding Agent

**Chromosome length change:** All crossover point sampling, mutation loops, and any hardcoded length references must use 294, not 260. Use `len(chrom)` wherever possible rather than magic numbers.

**Count value decoding is lossy by design:** The `11` bit pattern maps to 0 — this is intentional. Random initialization will produce some `11` pairs; they are valid chromosomes that happen to assign 0 to that rank.

**Shoe indexing:** Represent the shoe as a flat list. Use a `cards_dealt` integer index rather than popping cards, to avoid the overhead of list mutation. Access cards as `shoe[cards_dealt]`, `shoe[cards_dealt + 1]`, etc., and increment `cards_dealt` accordingly.

**Reshuffle timing:** The reshuffle check must happen before each hand starts, not mid-hand. If `cards_dealt >= 234` at the start of a new hand, reshuffle first. Never reshuffle mid-hand.

**Dealer hole card counting:** The hole card is physically dealt at the start of the hand but its value is not added to `running_count` until the dealer reveals it (after the player stands or before dealer hits). This is the standard card-counting convention and must be followed exactly.

**Bankroll as float:** Use `float` for bankroll to handle the 3:2 blackjack payout correctly (e.g., $1.50 win on a $1 bet). Do not round to integer.

**Roulette wheel with bankroll fitness:** Early in training, many individuals may have fitness = 0 (bankrupt). Avoid division-by-zero: if all fitnesses are 0, fall back to uniform random selection. If some are 0 and some are positive, 0-fitness individuals simply receive 0 selection probability.

**Reproducibility:** Set `numpy.random.seed(SEED)` and `random.seed(SEED)` at the top of `main.py`. Expose `SEED = 42` as a module-level constant.

**No hard-coded count values or strategy:** The chromosome must determine all decisions. Do not initialize the population with hi-lo values or basic strategy — start from random.

---

## Acceptance Criteria

- [ ] `blackjack_ga_counting/` directory contains all four modules and `requirements.txt`.
- [ ] `python main.py` (from within `blackjack_ga_counting/`) runs end-to-end in under 10 minutes on a modern laptop.
- [ ] Four PNG files are produced: `fitness_over_generations.png`, `strategy_heatmap.png`, `count_values.png`, `bankroll_over_time.png`.
- [ ] The fitness plot y-axis shows raw dollar values and includes the $1,000 reference line.
- [ ] The strategy heatmap shows the same convergence behavior as Part 1.
- [ ] The count values chart shows two bar groups per rank with the hi-lo reference overlaid.
- [ ] The bankroll plot uses fill coloring to show profit/loss zones.
- [ ] No third-party packages beyond numpy and matplotlib are used.
- [ ] The `blackjack_ga/` directory (Part 1) is not modified.