# Development Steps for 3-CNF-SAT Phase Transition Project

## Stage 1: Random Instance Generator

### Implementation Tasks
1. Create `generate(n: int, alpha: float) -> list[list[int]]` function
2. Calculate number of clauses as `m = int(n * alpha)`
3. For each clause, randomly select 3 literals:
   - Choose variable from 1 to n
   - Randomly assign polarity (positive/negative with 50% probability)

### Tests to Pass

```python
# Test 1.1: Correct clause count
def test_clause_count():
    for alpha in [1.0, 2.0, 3.5, 5.0]:
        instance = generate(100, alpha)
        expected = int(100 * alpha)
        assert len(instance) == expected, f"Expected {expected} clauses, got {len(instance)}"

# Test 1.2: Each clause has exactly 3 literals
def test_clause_size():
    instance = generate(50, 3.0)
    for clause in instance:
        assert len(clause) == 3, f"Clause should have 3 literals, got {len(clause)}"

# Test 1.3: All literals are valid (1 to n or -1 to -n, never 0)
def test_valid_literals():
    n = 100
    instance = generate(n, 4.0)
    for clause in instance:
        for lit in clause:
            assert lit != 0, "Literal cannot be 0"
            assert 1 <= abs(lit) <= n, f"Variable {abs(lit)} out of range [1, {n}]"

# Test 1.4: Polarity distribution roughly 50/50
def test_polarity_distribution():
    instance = generate(100, 10.0)  # 1000 clauses = 3000 literals
    positive = sum(1 for clause in instance for lit in clause if lit > 0)
    total = sum(len(clause) for clause in instance)
    ratio = positive / total
    assert 0.45 < ratio < 0.55, f"Polarity ratio {ratio} not near 50%"

# Test 1.5: Variable distribution roughly uniform
def test_variable_distribution():
    from collections import Counter
    n = 20
    instance = generate(n, 50.0)  # 1000 clauses
    var_counts = Counter(abs(lit) for clause in instance for lit in clause)
    expected_per_var = 3000 / n  # 150 per variable
    for var in range(1, n + 1):
        count = var_counts.get(var, 0)
        assert expected_per_var * 0.5 < count < expected_per_var * 1.5
```

---

## Stage 2: Solution Verifier (Helper for Testing Solver)

### Implementation Tasks
1. Create `verify_solution(instance: list[list[int]], assignment: dict[int, bool]) -> bool`
2. Check that each clause has at least one true literal under the assignment

### Tests to Pass

```python
# Test 2.1: Simple satisfying assignment
def test_verify_simple_sat():
    instance = [[1, 2, 3]]
    assignment = {1: True, 2: False, 3: False}
    assert verify_solution(instance, assignment) == True

# Test 2.2: Simple unsatisfying assignment
def test_verify_simple_unsat():
    instance = [[1, 2, 3]]
    assignment = {1: False, 2: False, 3: False}
    assert verify_solution(instance, assignment) == False

# Test 2.3: Negative literals
def test_verify_negative_literals():
    instance = [[-1, -2, 3]]
    assignment = {1: False, 2: True, 3: False}  # -1 is True
    assert verify_solution(instance, assignment) == True

# Test 2.4: Multiple clauses - all must be satisfied
def test_verify_multiple_clauses():
    instance = [[1, 2, 3], [-1, 2, 3]]
    assignment = {1: True, 2: True, 3: False}
    assert verify_solution(instance, assignment) == True

    assignment_bad = {1: True, 2: False, 3: False}  # Fails clause 2
    assert verify_solution(instance, assignment_bad) == False
```

---

## Stage 3: SAT Solver (Core Algorithm)

### Implementation Tasks
1. Create `solve(instance: list[list[int]]) -> bool`
2. Implement backtracking search
3. Implement unit propagation
4. Implement conflict detection

### Tests to Pass

```python
# Test 3.1: Empty instance is satisfiable
def test_empty_instance():
    assert solve([]) == True

# Test 3.2: Single clause - trivially satisfiable
def test_single_clause_sat():
    assert solve([[1, 2, 3]]) == True

# Test 3.3: Known SAT - unit clauses
def test_unit_clauses_sat():
    instance = [[1, 1, 1], [2, 2, 2], [3, 3, 3]]
    assert solve(instance) == True

# Test 3.4: Known UNSAT - direct contradiction
def test_simple_contradiction():
    instance = [[1, 1, 1], [-1, -1, -1]]
    assert solve(instance) == False

# Test 3.5: Known UNSAT - all 8 combinations of 3 vars
def test_all_combinations_unsat():
    # (x1 v x2 v x3) ^ (x1 v x2 v -x3) ^ (x1 v -x2 v x3) ^ (x1 v -x2 v -x3) ^
    # (-x1 v x2 v x3) ^ (-x1 v x2 v -x3) ^ (-x1 v -x2 v x3) ^ (-x1 v -x2 v -x3)
    instance = [
        [1, 2, 3], [1, 2, -3], [1, -2, 3], [1, -2, -3],
        [-1, 2, 3], [-1, 2, -3], [-1, -2, 3], [-1, -2, -3]
    ]
    assert solve(instance) == False

# Test 3.6: Complex satisfiable instance
def test_complex_sat():
    instance = [[1, -2, 3], [-1, 2, 3], [1, 2, -3], [-1, -2, 3]]
    assert solve(instance) == True

# Test 3.7: Solver returns correct results for verifiable instances
def test_solver_with_verification():
    # Generate easy instances, verify solver results
    for _ in range(10):
        instance = generate(10, 1.0)  # Low alpha = likely SAT
        result = solve(instance)
        if result:  # If SAT, we could verify assignment (if solver returns it)
            pass  # At minimum, solver should not crash

# Test 3.8: Extreme alpha values
def test_extreme_alpha_low():
    # Very low alpha: almost always SAT
    sat_count = sum(1 for _ in range(20) if solve(generate(20, 1.0)))
    assert sat_count >= 18, f"Expected mostly SAT at alpha=1.0, got {sat_count}/20"

def test_extreme_alpha_high():
    # Very high alpha: almost always UNSAT
    sat_count = sum(1 for _ in range(20) if solve(generate(20, 8.0)))
    assert sat_count <= 2, f"Expected mostly UNSAT at alpha=8.0, got {sat_count}/20"
```

---

## Stage 4: Experiment Harness

### Implementation Tasks
1. Create `run_experiment(n: int, alpha_values: list[float], trials: int) -> dict`
2. Loop over alpha values, generate instances, solve, track results
3. Add progress reporting
4. Create `save_results_csv(results: dict, filename: str)`

### Tests to Pass

```python
# Test 4.1: Returns correct structure
def test_experiment_structure():
    alphas = [2.0, 4.0, 6.0]
    results = run_experiment(20, alphas, trials=5)
    assert isinstance(results, dict)
    assert set(results.keys()) == set(alphas)
    for v in results.values():
        assert 0.0 <= v <= 1.0

# Test 4.2: Results are reproducible with seed
def test_experiment_reproducibility():
    import random
    alphas = [3.0, 5.0]
    random.seed(42)
    results1 = run_experiment(20, alphas, trials=10)
    random.seed(42)
    results2 = run_experiment(20, alphas, trials=10)
    assert results1 == results2

# Test 4.3: Trend check - sat fraction decreases with alpha
def test_experiment_trend():
    alphas = [1.0, 3.0, 5.0, 7.0]
    results = run_experiment(30, alphas, trials=20)
    fractions = [results[a] for a in alphas]
    # Should generally decrease (allow some noise)
    assert fractions[0] > fractions[-1], "SAT fraction should decrease with alpha"

# Test 4.4: CSV save/load roundtrip
def test_csv_save_load():
    import os
    results = {1.0: 0.95, 2.0: 0.80, 3.0: 0.60}
    save_results_csv(results, "test_results.csv")
    assert os.path.exists("test_results.csv")
    # Verify file contents
    with open("test_results.csv") as f:
        lines = f.readlines()
        assert len(lines) >= 4  # header + 3 data rows
    os.remove("test_results.csv")
```

---

## Stage 5: Visualization

### Implementation Tasks
1. Create `plot_results(results: dict, output_file: str)`
2. Plot alpha (x-axis) vs sat_fraction (y-axis)
3. Add labels, title, grid, theoretical transition line

### Tests to Pass

```python
# Test 5.1: Plot file is created
def test_plot_creation():
    import os
    results = {1.0: 0.98, 2.0: 0.92, 3.0: 0.75, 4.0: 0.50, 5.0: 0.20, 6.0: 0.05}
    plot_results(results, "test_plot.png")
    assert os.path.exists("test_plot.png")
    assert os.path.getsize("test_plot.png") > 1000  # Non-trivial file size
    os.remove("test_plot.png")

# Test 5.2: Handles full alpha range
def test_plot_full_range():
    import os
    alphas = [round(1.0 + 0.25 * i, 2) for i in range(29)]
    results = {a: max(0, 1 - (a - 1) / 7) for a in alphas}  # Fake linear decrease
    plot_results(results, "test_full_plot.png")
    assert os.path.exists("test_full_plot.png")
    os.remove("test_full_plot.png")
```

---

## Stage 6: Integration & Full Experiment

### Implementation Tasks
1. Create `main()` function that orchestrates everything
2. Add command-line arguments for seed, output paths
3. Run full experiment with n=100, 29 alpha values, 100 trials each

### Tests to Pass

```python
# Test 6.1: Small-scale integration test
def test_small_integration():
    """Run a mini version of the full experiment"""
    alphas = [2.0, 4.0, 6.0]
    results = run_experiment(30, alphas, trials=10)
    save_results_csv(results, "integration_test.csv")
    plot_results(results, "integration_test.png")

    # Cleanup
    import os
    os.remove("integration_test.csv")
    os.remove("integration_test.png")

# Test 6.2: Phase transition is visible
def test_phase_transition_visible():
    """Verify transition occurs near expected alpha"""
    alphas = [round(1.0 + 0.5 * i, 2) for i in range(15)]  # 1.0 to 8.0
    results = run_experiment(50, alphas, trials=30)

    # Find where sat fraction drops below 50%
    transition_alpha = None
    for a in sorted(alphas):
        if results[a] < 0.5:
            transition_alpha = a
            break

    # Should be near 4.26 (allow range 3.5 to 5.5)
    assert transition_alpha is not None, "No transition found"
    assert 3.5 <= transition_alpha <= 5.5, f"Transition at {transition_alpha}, expected near 4.26"

# Test 6.3: End-to-end smoke test
def test_main_smoke():
    """Verify main() runs without error (with reduced params)"""
    # Would need to modify main() to accept params or use smaller defaults for testing
    pass
```

---

## Stage 7: Final Validation & Full Run

### Acceptance Criteria
1. Full experiment completes (n=100, 29 alphas, 100 trials = 2,900 trials)
2. Results CSV contains all 29 data points
3. Plot shows clear S-curve phase transition
4. Transition point is near α ≈ 4.26 (within ±0.5)
5. α < 3.0 yields >90% SAT
6. α > 6.0 yields <10% SAT

---

## Summary: Test Gate Checklist

| Stage | Must Pass Before Proceeding |
|-------|----------------------------|
| 1 | All 5 generator tests pass |
| 2 | All 4 verifier tests pass |
| 3 | All 8 solver tests pass |
| 4 | All 4 harness tests pass |
| 5 | Both plot tests pass |
| 6 | Integration tests pass, transition visible |
| 7 | Full experiment produces expected results |
