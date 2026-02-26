# Implementation Steps: Blackjack Card Counting Extension

This document covers the implementation of `blackjack_ga_counting/`, a self-contained extension that evolves a card counting system and betting strategy alongside the base hit/stand strategy. Do **not** import from `blackjack_ga/`. All tests live in `blackjack_ga_counting/tests/` and are run from inside that directory (`cd blackjack_ga_counting && pytest tests/ -v`).

---

## Step 1: Set Up Project Structure

Create the following directory and files:

```
blackjack_ga_counting/
├── simulator.py
├── chromosome.py
├── ga.py
├── main.py
├── requirements.txt
└── tests/
    ├── conftest.py
    ├── test_step1.py
    ├── test_step2.py
    ├── test_step3.py
    ├── test_step4.py
    ├── test_step5.py
    └── test_step6.py
```

In `requirements.txt`, add:
```
numpy
matplotlib
```

In `tests/conftest.py`, add a `sys.path` fix so tests can import from the parent directory:
```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
```

Leave all four Python modules empty (or with a single `pass`) for now.

### Tests — Step 1

```python
# tests/test_step1.py
import os

BASE = os.path.join(os.path.dirname(__file__), '..')

def test_step1_files_exist():
    files = ['simulator.py', 'chromosome.py', 'ga.py', 'main.py', 'requirements.txt']
    for f in files:
        assert os.path.exists(os.path.join(BASE, f)), f"Missing file: {f}"

def test_step1_requirements():
    with open(os.path.join(BASE, 'requirements.txt')) as f:
        contents = f.read()
    assert 'numpy' in contents
    assert 'matplotlib' in contents

def test_step1_tests_directory_exists():
    assert os.path.isdir(os.path.join(BASE, 'tests')), "Missing tests/ directory"

def test_step1_conftest_has_sys_path_fix():
    conftest_path = os.path.join(BASE, 'tests', 'conftest.py')
    assert os.path.exists(conftest_path), "Missing tests/conftest.py"
    with open(conftest_path) as f:
        contents = f.read()
    assert 'sys.path' in contents, "conftest.py must add parent dir to sys.path"
```

**Pass criteria:** All 4 tests pass. All files and directories exist and `requirements.txt` lists both `numpy` and `matplotlib`. Do not proceed until this passes.

---

## Step 2: Implement `chromosome.py`

The 294-bit chromosome has three contiguous regions:

- **Bits 0–259 (260 bits):** Play strategy — identical layout to Part 1.
- **Bits 260–281 (22 bits):** Card count values — 11 ranks × 2 bits each. Bit pair decoding: `00`→−1, `01`→0, `10`→+1, `11`→0 (treated as 0).
- **Bits 282–293 (12 bits):** Bet multipliers — 4 true-count ranges × 3 bits each. Decoding: big-endian 3-bit integer + 1 gives multiplier 1–8.

1. Import `numpy as np`.
2. Implement `random_chromosome()`:
   - Return `np.random.randint(0, 2, size=294, dtype=np.uint8)`.
3. Implement `get_decision(chrom, player_total, is_soft, dealer_upcard)`:
   - Compute `dealer_upcard_index`: Ace=0, 2→1, 3→2, ..., 9→8, 10→9.
   - If `is_soft`: `index = 170 + (player_total - 12) * 10 + dealer_upcard_index`
   - Else: `index = (player_total - 4) * 10 + dealer_upcard_index`
   - Return `int(chrom[index])`. Reads only bits 0–259.
4. Implement `get_count_values(chrom)`:
   - For each rank `r` in 0–9 (Ace=0, 2=1, ..., 10=9):
     - `start_bit = 260 + r * 2`
     - `pair = (chrom[start_bit], chrom[start_bit + 1])`
     - Decode: `(0,0)`→−1, `(0,1)`→0, `(1,0)`→+1, `(1,1)`→0.
   - Return a dict `{1: cv_ace, 2: cv_2, ..., 9: cv_9, 10: cv_10}` where card value 1 = Ace and card value 10 represents all ten-valued cards.
5. Implement `get_bet_multipliers(chrom)`:
   - For each range index `i` in 0–3:
     - `start_bit = 282 + i * 3`
     - `encoded = chrom[start_bit] * 4 + chrom[start_bit + 1] * 2 + chrom[start_bit + 2]`
     - `multiplier = int(encoded) + 1`
   - Return a list of 4 integers in the range 1–8.
     Order: `[mult_for_<=−2, mult_for_−1_to_+1, mult_for_+2_to_+4, mult_for_>=+5]`.

### Tests — Step 2

```python
# tests/test_step2.py
import numpy as np
from chromosome import random_chromosome, get_decision, get_count_values, get_bet_multipliers

def test_chromosome_shape():
    chrom = random_chromosome()
    assert chrom.shape == (294,)
    assert chrom.dtype == np.uint8

def test_chromosome_values_binary():
    chrom = random_chromosome()
    assert set(chrom).issubset({0, 1})

# --- get_decision: identical index arithmetic to Part 1 ---

def test_get_decision_returns_binary():
    chrom = random_chromosome()
    assert get_decision(chrom, 16, False, 10) in (0, 1)

def test_index_hard_4_ace():
    chrom = np.zeros(294, dtype=np.uint8)
    chrom[0] = 1
    assert get_decision(chrom, 4, False, 1) == 1   # hard index 0

def test_index_hard_20_ten():
    chrom = np.zeros(294, dtype=np.uint8)
    chrom[169] = 1
    assert get_decision(chrom, 20, False, 10) == 1  # hard index 169

def test_index_soft_12_ace():
    chrom = np.zeros(294, dtype=np.uint8)
    chrom[170] = 1
    assert get_decision(chrom, 12, True, 1) == 1   # soft index 170

def test_index_soft_20_ten():
    chrom = np.zeros(294, dtype=np.uint8)
    chrom[259] = 1
    assert get_decision(chrom, 20, True, 10) == 1  # soft index 259

def test_get_decision_ignores_count_bits():
    # Count and bet bits (260–293) must not affect play strategy lookup
    chrom = np.zeros(294, dtype=np.uint8)
    chrom[260:] = 1   # set all count/bet bits
    chrom[0] = 0      # hard 4 vs Ace = stand
    assert get_decision(chrom, 4, False, 1) == 0

# --- get_count_values ---

def test_count_values_keys():
    chrom = random_chromosome()
    cv = get_count_values(chrom)
    assert set(cv.keys()) == {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}

def test_count_values_domain():
    for _ in range(20):
        chrom = random_chromosome()
        for v in get_count_values(chrom).values():
            assert v in (-1, 0, 1), f"Unexpected count value: {v}"

def test_count_value_decoding_minus_one():
    # Bit pair 00 → -1
    chrom = np.zeros(294, dtype=np.uint8)
    # Ace is rank 0: bits 260–261 = 00
    cv = get_count_values(chrom)
    assert cv[1] == -1

def test_count_value_decoding_zero_01():
    # Bit pair 01 → 0
    chrom = np.zeros(294, dtype=np.uint8)
    chrom[261] = 1  # Ace bits 260-261 = 01
    cv = get_count_values(chrom)
    assert cv[1] == 0

def test_count_value_decoding_plus_one():
    # Bit pair 10 → +1
    chrom = np.zeros(294, dtype=np.uint8)
    chrom[260] = 1  # Ace bits 260-261 = 10
    cv = get_count_values(chrom)
    assert cv[1] == 1

def test_count_value_decoding_11_is_zero():
    # Bit pair 11 → 0 (unused encoding)
    chrom = np.zeros(294, dtype=np.uint8)
    chrom[260] = 1
    chrom[261] = 1  # Ace bits = 11
    cv = get_count_values(chrom)
    assert cv[1] == 0

def test_count_value_rank_10_uses_bits_278_279():
    # Rank 10 (index 9): start_bit = 260 + 9*2 = 278
    chrom = np.zeros(294, dtype=np.uint8)
    chrom[278] = 1  # bit pair 10 → +1 for rank 10
    cv = get_count_values(chrom)
    assert cv[10] == 1

# --- get_bet_multipliers ---

def test_bet_multipliers_length():
    chrom = random_chromosome()
    mults = get_bet_multipliers(chrom)
    assert len(mults) == 4

def test_bet_multipliers_range():
    for _ in range(20):
        chrom = random_chromosome()
        for m in get_bet_multipliers(chrom):
            assert 1 <= m <= 8, f"Multiplier {m} out of range 1–8"

def test_bet_multiplier_decoding_all_zeros():
    # Bits 282–293 all 0 → encoded=0 → multiplier=1 for all ranges
    chrom = np.zeros(294, dtype=np.uint8)
    mults = get_bet_multipliers(chrom)
    assert mults == [1, 1, 1, 1]

def test_bet_multiplier_decoding_all_ones():
    # Bits 282–293 all 1 → encoded=7 → multiplier=8 for all ranges
    chrom = np.zeros(294, dtype=np.uint8)
    chrom[282:294] = 1
    mults = get_bet_multipliers(chrom)
    assert mults == [8, 8, 8, 8]

def test_bet_multiplier_decoding_specific():
    # Range 1 (bits 285-287): set to 011 → encoded=3 → multiplier=4
    chrom = np.zeros(294, dtype=np.uint8)
    chrom[286] = 1  # 285=0, 286=1, 287=1 → 011 = 3 → mult=4
    chrom[287] = 1
    mults = get_bet_multipliers(chrom)
    assert mults[1] == 4

def test_bet_multiplier_independence():
    # Setting only the third range's bits should only affect index 2
    chrom = np.zeros(294, dtype=np.uint8)
    chrom[288] = 1  # range 2 (bits 288-290): 100 = 4 → mult=5
    mults = get_bet_multipliers(chrom)
    assert mults[0] == 1
    assert mults[1] == 1
    assert mults[2] == 5
    assert mults[3] == 1
```

**Pass criteria:** All 24 tests pass. Index arithmetic for all three regions must be exact — any off-by-one corrupts the entire fitness landscape. Do not proceed until this passes.

---

## Step 3: Implement `simulator.py`

1. Import `numpy as np`, `random`, and `chromosome` functions (`get_decision`, `get_count_values`, `get_bet_multipliers`).
2. Define `make_shoe()`: return a list of 312 card values — six copies of `[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10] * 4`.
3. Define `hand_value(cards)` returning `(total, is_soft)`:
   - Count all aces as 1 first (non-ace sum + number of aces). If any aces are present and `total + 10 <= 21`, add 10 and set `is_soft = True`. Otherwise `is_soft = False`.
4. Define `calculate_true_count(running_count, cards_dealt, shoe_size=312)`:
   - `decks_remaining = (shoe_size - cards_dealt) / 52`
   - Guard: if `decks_remaining <= 0`, return 0.
   - Return `round(running_count / decks_remaining)`.
5. Define `get_bet(chrom, running_count, cards_dealt, bankroll)`:
   - Compute `true_count`.
   - Select multiplier from `get_bet_multipliers(chrom)` using the four true-count ranges (`<= -2`, `-1 to +1`, `+2 to +4`, `>= +5`).
   - Return `min(multiplier * 1, bankroll)`. (Base unit = $1.)
6. Implement `simulate_hand(chrom, shoe, cards_dealt, running_count, bankroll, bet)`:
   - Draw cards from `shoe` using `cards_dealt` as an index pointer (do not pop).
   - Deal order: player card 1 (`shoe[cards_dealt]`), dealer hole card (`shoe[cards_dealt+1]`), player card 2 (`shoe[cards_dealt+2]`), dealer upcard (`shoe[cards_dealt+3]`). Advance `cards_dealt` by 4.
   - Add count values for player card 1, player card 2, and dealer upcard to `running_count`. **Do not add the hole card yet** (it is hidden).
   - Check naturals using `hand_value`: if player has 21 and dealer does not → `'win'`, dealer has 21 and player does not → `'loss'`, both → `'tie'`. Add hole card count value to `running_count` whenever dealer cards are revealed.
   - Player loop: while `player_total < 21`, call `get_decision(chrom, total, is_soft, dealer_upcard)`. If hit (1), draw next card, add its count value to `running_count`, update hand. If stand (0), break. If player total > 21 → `'loss'`.
   - Dealer loop: reveal hole card (add its count value to `running_count` now). Dealer hits if `total < 17`. For each dealer hit, add its count value to `running_count`.
   - Resolve: dealer bust → `'win'`; compare totals; equal → `'tie'`.
   - Return `(outcome, cards_dealt, running_count, bankroll_after_outcome)`.
   - Apply bankroll changes inside this function based on outcome and bet:
     - Win (non-blackjack): `bankroll += bet`
     - Player blackjack: `bankroll += 1.5 * bet`
     - Loss: `bankroll -= bet`
     - Tie: unchanged
7. Implement `simulate_session(chrom, n_hands=1000)`:
   - Shuffle a fresh shoe. Set `cards_dealt = 0`, `running_count = 0`, `bankroll = 1000.0`.
   - For up to `n_hands`: if `cards_dealt >= 234` (75% penetration), reshuffle shoe and reset `cards_dealt = 0`, `running_count = 0`.
   - Compute bet, call `simulate_hand`. Append bankroll to history list. Stop early if `bankroll <= 0`.
   - Return list of bankrolls after each hand.
8. Implement `evaluate_fitness(chrom, n_hands=1000)`:
   - Call `simulate_session(chrom, n_hands)`.
   - Return the final bankroll (last element of the list), or `0.0` if the list is empty.

### Tests — Step 3

```python
# tests/test_step3.py
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
    # Ace + 9 + 5 = 15 hard (ace falls back to 1)
    total, is_soft = hand_value([1, 9, 5])
    assert total == 15
    assert is_soft is False

def test_hand_value_blackjack():
    total, is_soft = hand_value([1, 10])
    assert total == 21
    assert is_soft is True

def test_hand_value_double_ace():
    # Ace + Ace: one counts as 11, one as 1 → soft 12
    total, is_soft = hand_value([1, 1])
    assert total == 12
    assert is_soft is True

# --- calculate_true_count ---

def test_true_count_basic():
    # 6 decks = 312 cards; 156 dealt → 3 decks remain → true count = round(6/3) = 2
    tc = calculate_true_count(6, 156)
    assert tc == 2

def test_true_count_zero_running():
    assert calculate_true_count(0, 0) == 0

def test_true_count_guards_zero_remaining():
    # Should not raise; returns 0 when decks_remaining <= 0
    tc = calculate_true_count(5, 312)
    assert tc == 0

def test_true_count_rounding():
    # running=5, 260 dealt → 52 remaining = 1 deck → TC = 5
    tc = calculate_true_count(5, 260)
    assert tc == 5

# --- get_bet ---

def test_get_bet_within_bounds():
    chrom = random_chromosome()
    bet = get_bet(chrom, 0, 0, 1000.0)
    assert 1 <= bet <= 8

def test_get_bet_capped_by_bankroll():
    # With a tiny bankroll, bet must not exceed it
    chrom = np.zeros(294, dtype=np.uint8)
    chrom[282:294] = 1   # all multipliers = 8
    bet = get_bet(chrom, 10, 0, 2.0)   # high count → max multiplier, but capped at 2
    assert bet == 2.0

def test_get_bet_range_selection():
    # Force multiplier for each range by setting bits explicitly
    chrom = np.zeros(294, dtype=np.uint8)
    # Range 0 (<=−2): bits 282-284 = 001 → mult=2
    chrom[284] = 1
    # Range 3 (>=+5): bits 291-293 = 111 → mult=8
    chrom[291] = chrom[292] = chrom[293] = 1

    # true_count <= -2 should use range 0 (mult=2)
    # running_count=-12, cards_dealt=0 → decks_remaining=6 → TC=round(-12/6)=-2
    bet_low = get_bet(chrom, -12, 0, 1000.0)
    assert bet_low == 2

    # true_count >= +5 should use range 3 (mult=8)
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
    assert new_cd >= 4   # at minimum 4 cards dealt (2 player + 2 dealer)

def test_simulate_hand_bankroll_changes_on_win():
    # Force a win: player gets natural blackjack, dealer does not
    chrom = np.zeros(294, dtype=np.uint8)   # all stand
    shoe = make_shoe()
    # Prepend: player=Ace, dealer=2, player=10, dealer=3 (player BJ, dealer no BJ)
    shoe = [1, 2, 10, 3] + shoe
    _, _, _, bankroll = simulate_hand(chrom, shoe, 0, 0, 1000.0, 2.0)
    assert bankroll == 1003.0   # 3:2 payout on $2 bet = +$3

def test_simulate_hand_bankroll_changes_on_loss():
    # Force a loss: dealer gets natural blackjack, player does not
    chrom = np.zeros(294, dtype=np.uint8)   # all stand
    shoe = make_shoe()
    # player=5, dealer=1(hole), player=6, dealer=10(upcard) → dealer BJ
    shoe = [5, 1, 6, 10] + shoe
    _, _, _, bankroll = simulate_hand(chrom, shoe, 0, 0, 1000.0, 3.0)
    assert bankroll == 997.0   # −$3

def test_hole_card_count_not_added_early():
    # Track running_count: hole card count value must be added only when dealer reveals
    # Use a chromosome with known count values: all ranks count as +1
    chrom = np.zeros(294, dtype=np.uint8)
    # Set all count bits to 10 (+1): bits 260,262,264,...,278 = 1
    for r in range(10):
        chrom[260 + r * 2] = 1
    shoe = make_shoe()
    random.shuffle(shoe)
    # After 4 cards dealt: player c1, player c2, dealer upcard counted → +3
    # hole card counted only when dealer reveals it (during dealer loop)
    # We can't easily isolate the timing, but we can check the final rc is consistent
    _, cd, rc, _ = simulate_hand(chrom, shoe, 0, 0, 1000.0, 1.0)
    # At minimum 4 cards, all +1 each, so rc >= 4
    assert rc >= 4

# --- simulate_session ---

def test_simulate_session_returns_list():
    chrom = random_chromosome()
    history = simulate_session(chrom, n_hands=10)
    assert isinstance(history, list)
    assert len(history) <= 10
    assert all(isinstance(b, float) for b in history)

def test_simulate_session_stops_on_bust():
    # A chromosome that always bets maximum and stands on low totals
    # may bust. If it does, history must stop there.
    chrom = np.zeros(294, dtype=np.uint8)
    chrom[282:294] = 1   # max bets always
    # Use a fixed seed to get a deterministic bust scenario (if any)
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
    # Verify that after 234 cards dealt the shoe is reshuffled.
    # We can indirectly test by running many hands and ensuring no IndexError.
    chrom = random_chromosome()
    random.seed(0)
    history = simulate_session(chrom, n_hands=500)
    assert len(history) > 0   # should complete without crashing

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
    # Starting bankroll is $1000. After 1000 hands with random strategy, should
    # remain roughly in range $0–$2000 for a random chromosome.
    chrom = random_chromosome()
    random.seed(42)
    f = evaluate_fitness(chrom, n_hands=200)
    assert 0.0 <= f <= 3000.0, f"Fitness {f} looks unreasonable"
```

**Pass criteria:** All 26 tests pass. Pay special attention to:
- `test_simulate_hand_bankroll_changes_on_win`: confirms 3:2 blackjack payout.
- `test_simulate_session_bankroll_is_nonnegative`: bankroll may hit 0 but never go negative.
- `test_simulate_session_reshuffles_at_penetration`: no crashes from shoe running dry.
Do not proceed until this passes.

---

## Step 4: Implement `ga.py`

This is identical in structure to Part 1 `ga.py`, adapted for the 294-bit chromosome and bankroll-valued fitness.

1. Import `numpy as np`, `copy`, `evaluate_fitness` from `simulator`, and `random_chromosome` from `chromosome`.
2. Define module-level constants:
   ```python
   POPULATION_SIZE = 100
   N_GENERATIONS   = 75
   N_HANDS         = 1000
   MUTATION_RATE   = 0.01
   N_ELITES        = 2
   ```
3. Implement `initialize_population(size=POPULATION_SIZE)`:
   - Return `[random_chromosome() for _ in range(size)]`.
4. Implement `roulette_select(population, fitnesses)`:
   - Clip fitnesses to `np.clip(fitnesses, 0, None)` (handles any stray negatives).
   - `total = fitnesses.sum()`. If `total == 0`, select uniformly via `np.random.randint`.
   - Otherwise, `probs = fitnesses / total`. Use `np.random.choice(len(population), p=probs)`.
   - Return `population[index].copy()`.
5. Implement `crossover(parent_a, parent_b)`:
   - Pick a random crossover point in `[1, 292]` inclusive (use `len(parent_a) - 2`).
   - Return two children by swapping tails.
6. Implement `mutate(chrom, rate=MUTATION_RATE)`:
   - `mask = np.random.random(len(chrom)) < rate`
   - Return `chrom.copy() ^ mask.astype(np.uint8)`.
7. Implement `evolve(population, fitnesses)`:
   - Sort descending by fitness; copy top `N_ELITES` unchanged.
   - Fill remaining `POPULATION_SIZE - N_ELITES` slots with offspring: select two parents via `roulette_select`, apply `crossover`, then `mutate` each child.
   - Trim to exactly `POPULATION_SIZE`. Return new population.
8. Implement `run_ga()`:
   - Initialize population.
   - For each generation 0 to `N_GENERATIONS - 1`:
     - Evaluate fitness for every individual; store as `np.ndarray` of floats.
     - Record `{'generation': g, 'min': float, 'max': float, 'mean': float, 'median': float}` into `history`.
     - Print `Gen {g+1}/{N_GENERATIONS} | Max: ${max:.2f} | Mean: ${mean:.2f}`.
     - Evolve population.
   - Return `(population, history)`.

### Tests — Step 4

```python
# tests/test_step4.py
import numpy as np
import random
from ga import (initialize_population, roulette_select, crossover, mutate,
                evolve, POPULATION_SIZE, N_ELITES, MUTATION_RATE)

def test_initialize_population_size():
    pop = initialize_population(30)
    assert len(pop) == 30

def test_initialize_population_default():
    pop = initialize_population()
    assert len(pop) == POPULATION_SIZE

def test_initialize_population_chromosome_shape():
    pop = initialize_population(5)
    for chrom in pop:
        assert chrom.shape == (294,)
        assert chrom.dtype == np.uint8

def test_roulette_select_returns_copy():
    pop = initialize_population(10)
    fitnesses = np.random.uniform(800, 1200, size=10)
    selected = roulette_select(pop, fitnesses)
    assert selected.shape == (294,)
    # Must be a copy, not a reference to an existing element
    assert not any(selected is p for p in pop)

def test_roulette_select_uniform_when_all_zero():
    pop = initialize_population(10)
    fitnesses = np.zeros(10)
    selected = roulette_select(pop, fitnesses)  # must not raise ZeroDivisionError
    assert selected.shape == (294,)

def test_roulette_select_clips_negative():
    pop = initialize_population(10)
    fitnesses = np.array([-100.0] * 5 + [500.0] * 5)
    selected = roulette_select(pop, fitnesses)  # must not raise
    assert selected.shape == (294,)

def test_crossover_output_shapes():
    pop = initialize_population(2)
    c1, c2 = crossover(pop[0], pop[1])
    assert c1.shape == (294,)
    assert c2.shape == (294,)

def test_crossover_values_binary():
    pop = initialize_population(2)
    c1, c2 = crossover(pop[0], pop[1])
    assert set(c1).issubset({0, 1})
    assert set(c2).issubset({0, 1})

def test_crossover_point_is_interior():
    # With all-0 and all-1 parents, each child must be mixed
    a = np.zeros(294, dtype=np.uint8)
    b = np.ones(294, dtype=np.uint8)
    for _ in range(20):
        c1, c2 = crossover(a, b)
        # Neither child should equal a parent (crossover point must be interior)
        assert not np.array_equal(c1, a)
        assert not np.array_equal(c1, b)

def test_mutate_returns_copy():
    chrom = np.zeros(294, dtype=np.uint8)
    mutated = mutate(chrom, rate=0.0)
    assert mutated is not chrom
    assert np.array_equal(mutated, chrom)

def test_mutate_zero_rate_unchanged():
    chrom = np.zeros(294, dtype=np.uint8)
    assert np.array_equal(mutate(chrom, rate=0.0), chrom)

def test_mutate_full_rate_all_flipped():
    chrom = np.zeros(294, dtype=np.uint8)
    assert np.all(mutate(chrom, rate=1.0) == 1)

def test_evolve_population_size_preserved():
    pop = initialize_population(POPULATION_SIZE)
    fitnesses = np.random.uniform(800, 1200, size=POPULATION_SIZE)
    new_pop = evolve(pop, fitnesses)
    assert len(new_pop) == POPULATION_SIZE

def test_evolve_all_chromosomes_correct_shape():
    pop = initialize_population(POPULATION_SIZE)
    fitnesses = np.random.uniform(800, 1200, size=POPULATION_SIZE)
    new_pop = evolve(pop, fitnesses)
    for chrom in new_pop:
        assert chrom.shape == (294,)

def test_evolve_elites_preserved():
    pop = initialize_population(POPULATION_SIZE)
    fitnesses = np.random.uniform(800, 1200, size=POPULATION_SIZE)
    top_indices = np.argsort(fitnesses)[-N_ELITES:]
    top_chroms = [pop[i].copy() for i in top_indices]
    new_pop = evolve(pop, fitnesses)
    found = sum(any(np.array_equal(e, c) for c in new_pop) for e in top_chroms)
    assert found == N_ELITES, f"Expected {N_ELITES} elites preserved, found {found}"

def test_run_ga_history_length():
    import ga as ga_module
    orig_gen   = ga_module.N_GENERATIONS
    orig_size  = ga_module.POPULATION_SIZE
    orig_hands = ga_module.N_HANDS
    ga_module.N_GENERATIONS   = 3
    ga_module.POPULATION_SIZE = 10
    ga_module.N_HANDS         = 20
    final_pop, history = ga_module.run_ga()
    ga_module.N_GENERATIONS   = orig_gen
    ga_module.POPULATION_SIZE = orig_size
    ga_module.N_HANDS         = orig_hands
    assert len(history) == 3
    assert all(k in history[0] for k in ('generation', 'min', 'max', 'mean', 'median'))
    assert len(final_pop) == 10

def test_run_ga_history_values_are_bankrolls():
    import ga as ga_module
    orig_gen   = ga_module.N_GENERATIONS
    orig_size  = ga_module.POPULATION_SIZE
    orig_hands = ga_module.N_HANDS
    ga_module.N_GENERATIONS   = 2
    ga_module.POPULATION_SIZE = 5
    ga_module.N_HANDS         = 20
    _, history = ga_module.run_ga()
    ga_module.N_GENERATIONS   = orig_gen
    ga_module.POPULATION_SIZE = orig_size
    ga_module.N_HANDS         = orig_hands
    for entry in history:
        assert entry['min'] <= entry['mean']
        assert entry['mean'] <= entry['max']
        assert entry['min'] >= 0.0   # bankroll never negative
```

**Pass criteria:** All 17 tests pass. `test_evolve_elites_preserved` and `test_roulette_select_uniform_when_all_zero` are the most important — early generations can produce many bankrupt individuals (fitness=0) so the fallback to uniform selection is essential. Do not proceed until this passes.

---

## Step 5: Implement `main.py`

1. At the top, set seeds and define the seed constant:
   ```python
   import numpy as np, random, matplotlib
   matplotlib.use('Agg')   # non-interactive backend for saving PNGs
   import matplotlib.pyplot as plt
   from ga import run_ga, N_GENERATIONS
   from chromosome import get_decision, get_count_values
   from simulator import simulate_session
   SEED = 42
   random.seed(SEED)
   np.random.seed(SEED)
   ```
2. Call `run_ga()`, storing `final_population, history`. (Generation summary lines are printed inside `run_ga()`.)
3. Identify `best_chrom` = chromosome with the highest fitness in `final_population`.
4. **Figure 1 — Bankroll Over Generations** (`fitness_over_generations.png`):
   - Extract `generations`, `maxes`, `means`, `medians`, `mins` from `history`.
   - Plot four lines (colors: red=Max, blue=Mean, green dashed=Median, orange=Min).
   - Add horizontal dashed grey line at y=1000 labeled `"Starting bankroll ($1,000)"`.
   - Title: `"Blackjack Counting GA: Bankroll Over Generations"`. X-label: `"Generation"`. Y-label: `"Final Bankroll ($)"`. Legend upper right. Grid alpha=0.3.
   - Save as `fitness_over_generations.png`.
5. **Figure 2 — Strategy Heatmap** (`strategy_heatmap.png`):
   - Identical to Part 1 Figure 2. Compute hard `(17, 10)` and soft `(9, 10)` consensus matrices from bits 0–259 of each final chromosome. Two-panel figure with `RdBu_r` colormap, cell annotations, colorbar.
   - Save as `strategy_heatmap.png`.
6. **Figure 3 — Evolved Count Values vs. Hi-Lo** (`count_values.png`):
   - For each rank in `[1,2,3,4,5,6,7,8,9,10]` (Ace to 10), compute the mean decoded count value across all final population chromosomes.
   - Hi-Lo reference: `{1:-1, 2:+1, 3:+1, 4:+1, 5:+1, 6:+1, 7:0, 8:0, 9:0, 10:-1}`.
   - Grouped bar chart: evolved bars in steel blue, hi-lo bars in coral/salmon. Two groups per rank.
   - Annotate evolved bars with `"+X.XX"` or `"-X.XX"` above each bar.
   - X-axis: `['A','2','3','4','5','6','7','8','9','10']`. Y-axis: `"Count Value"`, range −1.2 to +1.2.
   - Horizontal dashed line at y=0. Legend. Title: `"Evolved Count Values vs. Hi-Lo System"`. Grid alpha=0.3.
   - Save as `count_values.png`.
7. **Figure 4 — Best Individual Bankroll Over Time** (`bankroll_over_time.png`):
   - Call `simulate_session(best_chrom, n_hands=1000)` to get `bankroll_history`.
   - Line plot of bankroll over time (steelblue, linewidth=1.5).
   - Horizontal dashed grey line at y=1000 labeled `"Starting bankroll"`.
   - `ax.fill_between`: green (alpha=0.15) where `bankroll > 1000`, red (alpha=0.15) where `bankroll < 1000`.
   - Annotate final bankroll value in the lower right of the plot (e.g., `"Final: $1,142"`).
   - X-label: `"Hand"`. Y-label: `"Bankroll ($)"`. Title: `"Best Individual: Bankroll Over 1,000 Hands"`. Grid alpha=0.3.
   - Save as `bankroll_over_time.png`.
8. Call `plt.show()` after saving all figures.

### Tests — Step 5

```python
# tests/test_step5.py
import os
import subprocess
import time

BASE = os.path.join(os.path.dirname(__file__), '..')

def _run_main(timeout=600):
    return subprocess.run(
        ['python', 'main.py'],
        capture_output=True, text=True, timeout=timeout,
        cwd=BASE
    )

def test_main_runs_without_error():
    result = _run_main()
    assert result.returncode == 0, f"main.py exited with error:\n{result.stderr}"

def test_main_completes_within_time_limit():
    start = time.time()
    _run_main(timeout=600)
    elapsed = time.time() - start
    assert elapsed < 600, f"main.py took {elapsed:.1f}s — exceeds 10-minute limit"

def test_fitness_png_exists():
    assert os.path.exists(os.path.join(BASE, 'fitness_over_generations.png'))

def test_strategy_heatmap_png_exists():
    assert os.path.exists(os.path.join(BASE, 'strategy_heatmap.png'))

def test_count_values_png_exists():
    assert os.path.exists(os.path.join(BASE, 'count_values.png'))

def test_bankroll_over_time_png_exists():
    assert os.path.exists(os.path.join(BASE, 'bankroll_over_time.png'))

def test_all_pngs_are_nonempty():
    for fname in ['fitness_over_generations.png', 'strategy_heatmap.png',
                  'count_values.png', 'bankroll_over_time.png']:
        path = os.path.join(BASE, fname)
        size = os.path.getsize(path)
        assert size > 1000, f"{fname} appears empty ({size} bytes)"

def test_stdout_contains_generation_lines():
    result = _run_main()
    lines = result.stdout.strip().split('\n')
    gen_lines = [l for l in lines if l.startswith('Gen ')]
    assert len(gen_lines) == 75, f"Expected 75 generation lines, got {len(gen_lines)}"
    assert 'Max:' in gen_lines[0] and 'Mean:' in gen_lines[0]

def test_stdout_generation_lines_use_dollar_amounts():
    result = _run_main()
    lines = result.stdout.strip().split('\n')
    gen_lines = [l for l in lines if l.startswith('Gen ')]
    # Bankroll amounts should contain '$' prefix
    assert '$' in gen_lines[0], f"Generation line missing '$': {gen_lines[0]}"
```

**Pass criteria:** All 9 tests pass. All four PNG files must exist and be non-trivially sized. The stdout must contain exactly 75 generation summary lines with dollar amounts. Do not proceed to Step 6 until this passes.

---

## Step 6: Verify Final Output Quality

Run `python main.py` from inside `blackjack_ga_counting/` and inspect all four figures for correctness.

1. **Figure 1 (Bankroll Over Generations):** Mean and median should trend upward relative to the start. The max line will be noisy. The $1,000 reference line should be visible.
2. **Figure 2 (Strategy Heatmap):** Same convergence as Part 1 — hard 4–8 mostly red, hard 17–20 mostly blue, 12–16 shows a gradient.
3. **Figure 3 (Count Values):** Evolved bars should broadly resemble hi-lo. Low cards (2–6) should lean positive, high cards (Ace, 10) should lean negative. Perfect agreement is not expected after 75 generations from random.
4. **Figure 4 (Bankroll Over Time):** A volatile line with green/red fill zones. Final bankroll annotated in the lower right.

### Tests — Step 6

```python
# tests/test_step6.py
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
    final_pop, _ = _run_short_ga(generations=15, pop_size=20, n_hands=100)
    hit_pcts = []
    for total in range(4, 9):   # hard 4–8
        for upcard in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
            hit_pcts.append(
                np.mean([get_decision(c, total, False, upcard) for c in final_pop]) * 100
            )
    avg = np.mean(hit_pcts)
    assert avg >= 55, f"Hard 4–8 avg hit% is {avg:.1f}%, expected ≥55%"

def test_heatmap_hard_high_totals_lean_stand():
    final_pop, _ = _run_short_ga(generations=15, pop_size=20, n_hands=100)
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
```

**Pass criteria:** All 10 tests pass. The project is complete when all tests across all steps pass.
