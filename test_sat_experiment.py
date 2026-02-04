"""
Tests for the 3-CNF-SAT Phase Transition Experiment
"""

import pytest
import os
from collections import Counter

import random
from sat_experiment import generate, verify_solution, solve, run_experiment, save_results_csv, plot_results, main


# =============================================================================
# Stage 1: Generator Tests
# =============================================================================

class TestStage1Generator:
    """Tests for the random instance generator."""

    def test_clause_count(self):
        """Test 1.1: Correct clause count"""
        for alpha in [1.0, 2.0, 3.5, 5.0]:
            instance = generate(100, alpha)
            expected = int(100 * alpha)
            assert len(instance) == expected, f"Expected {expected} clauses, got {len(instance)}"

    def test_clause_size(self):
        """Test 1.2: Each clause has exactly 3 literals"""
        instance = generate(50, 3.0)
        for clause in instance:
            assert len(clause) == 3, f"Clause should have 3 literals, got {len(clause)}"

    def test_valid_literals(self):
        """Test 1.3: All literals are valid (1 to n or -1 to -n, never 0)"""
        n = 100
        instance = generate(n, 4.0)
        for clause in instance:
            for lit in clause:
                assert lit != 0, "Literal cannot be 0"
                assert 1 <= abs(lit) <= n, f"Variable {abs(lit)} out of range [1, {n}]"

    def test_polarity_distribution(self):
        """Test 1.4: Polarity distribution roughly 50/50"""
        instance = generate(100, 10.0)  # 1000 clauses = 3000 literals
        positive = sum(1 for clause in instance for lit in clause if lit > 0)
        total = sum(len(clause) for clause in instance)
        ratio = positive / total
        assert 0.45 < ratio < 0.55, f"Polarity ratio {ratio} not near 50%"

    def test_variable_distribution(self):
        """Test 1.5: Variable distribution roughly uniform"""
        n = 20
        instance = generate(n, 50.0)  # 1000 clauses
        var_counts = Counter(abs(lit) for clause in instance for lit in clause)
        expected_per_var = 3000 / n  # 150 per variable
        for var in range(1, n + 1):
            count = var_counts.get(var, 0)
            assert expected_per_var * 0.5 < count < expected_per_var * 1.5, \
                f"Variable {var} count {count} outside expected range"


# =============================================================================
# Stage 2: Solution Verifier Tests
# =============================================================================

class TestStage2Verifier:
    """Tests for the solution verifier."""

    def test_verify_simple_sat(self):
        """Test 2.1: Simple satisfying assignment"""
        instance = [[1, 2, 3]]
        assignment = {1: True, 2: False, 3: False}
        assert verify_solution(instance, assignment) == True

    def test_verify_simple_unsat(self):
        """Test 2.2: Simple unsatisfying assignment"""
        instance = [[1, 2, 3]]
        assignment = {1: False, 2: False, 3: False}
        assert verify_solution(instance, assignment) == False

    def test_verify_negative_literals(self):
        """Test 2.3: Negative literals"""
        instance = [[-1, -2, 3]]
        assignment = {1: False, 2: True, 3: False}  # -1 is True
        assert verify_solution(instance, assignment) == True

    def test_verify_multiple_clauses(self):
        """Test 2.4: Multiple clauses - all must be satisfied"""
        instance = [[1, 2, 3], [-1, 2, 3]]
        assignment = {1: True, 2: True, 3: False}
        assert verify_solution(instance, assignment) == True

        assignment_bad = {1: True, 2: False, 3: False}  # Fails clause 2
        assert verify_solution(instance, assignment_bad) == False


# =============================================================================
# Stage 3: SAT Solver Tests
# =============================================================================

class TestStage3Solver:
    """Tests for the SAT solver."""

    def test_empty_instance(self):
        """Test 3.1: Empty instance is satisfiable"""
        assert solve([]) == True

    def test_single_clause_sat(self):
        """Test 3.2: Single clause - trivially satisfiable"""
        assert solve([[1, 2, 3]]) == True

    def test_unit_clauses_sat(self):
        """Test 3.3: Known SAT - unit clauses"""
        instance = [[1, 1, 1], [2, 2, 2], [3, 3, 3]]
        assert solve(instance) == True

    def test_simple_contradiction(self):
        """Test 3.4: Known UNSAT - direct contradiction"""
        instance = [[1, 1, 1], [-1, -1, -1]]
        assert solve(instance) == False

    def test_all_combinations_unsat(self):
        """Test 3.5: Known UNSAT - all 8 combinations of 3 vars"""
        instance = [
            [1, 2, 3], [1, 2, -3], [1, -2, 3], [1, -2, -3],
            [-1, 2, 3], [-1, 2, -3], [-1, -2, 3], [-1, -2, -3]
        ]
        assert solve(instance) == False

    def test_complex_sat(self):
        """Test 3.6: Complex satisfiable instance"""
        instance = [[1, -2, 3], [-1, 2, 3], [1, 2, -3], [-1, -2, 3]]
        assert solve(instance) == True

    def test_solver_with_verification(self):
        """Test 3.7: Solver returns correct results for verifiable instances"""
        for _ in range(10):
            instance = generate(10, 1.0)
            result, assignment = solve(instance, return_assignment=True)
            if result:
                assert verify_solution(instance, assignment), \
                    "Solver returned SAT but assignment doesn't satisfy instance"

    def test_extreme_alpha_low(self):
        """Test 3.8a: Extreme alpha values - low alpha mostly SAT"""
        sat_count = sum(1 for _ in range(20) if solve(generate(20, 1.0)))
        assert sat_count >= 18, f"Expected mostly SAT at alpha=1.0, got {sat_count}/20"

    def test_extreme_alpha_high(self):
        """Test 3.8b: Extreme alpha values - high alpha mostly UNSAT"""
        sat_count = sum(1 for _ in range(20) if solve(generate(20, 8.0)))
        assert sat_count <= 2, f"Expected mostly UNSAT at alpha=8.0, got {sat_count}/20"


# =============================================================================
# Stage 4: Experiment Harness Tests
# =============================================================================

class TestStage4Harness:
    """Tests for the experiment harness."""

    def test_experiment_structure(self):
        """Test 4.1: Returns correct structure"""
        alphas = [2.0, 4.0, 6.0]
        results = run_experiment(20, alphas, trials=5)
        assert isinstance(results, dict)
        assert set(results.keys()) == set(alphas)
        for v in results.values():
            assert 0.0 <= v <= 1.0

    def test_experiment_reproducibility(self):
        """Test 4.2: Results are reproducible with seed"""
        alphas = [3.0, 5.0]
        random.seed(42)
        results1 = run_experiment(20, alphas, trials=10)
        random.seed(42)
        results2 = run_experiment(20, alphas, trials=10)
        assert results1 == results2

    def test_experiment_trend(self):
        """Test 4.3: Trend check - sat fraction decreases with alpha"""
        alphas = [1.0, 3.0, 5.0, 7.0]
        results = run_experiment(30, alphas, trials=20)
        fractions = [results[a] for a in alphas]
        assert fractions[0] > fractions[-1], "SAT fraction should decrease with alpha"

    def test_csv_save_load(self):
        """Test 4.4: CSV save/load roundtrip"""
        results = {1.0: 0.95, 2.0: 0.80, 3.0: 0.60}
        save_results_csv(results, "test_results.csv")
        assert os.path.exists("test_results.csv")
        # Verify file contents
        with open("test_results.csv") as f:
            lines = f.readlines()
            assert len(lines) >= 4  # header + 3 data rows
        os.remove("test_results.csv")


# =============================================================================
# Stage 5: Visualization Tests
# =============================================================================

class TestStage5Visualization:
    """Tests for the visualization."""

    def test_plot_creation(self):
        """Test 5.1: Plot file is created"""
        results = {1.0: 0.98, 2.0: 0.92, 3.0: 0.75, 4.0: 0.50, 5.0: 0.20, 6.0: 0.05}
        plot_results(results, "test_plot.png")
        assert os.path.exists("test_plot.png")
        assert os.path.getsize("test_plot.png") > 1000  # Non-trivial file size
        os.remove("test_plot.png")

    def test_plot_full_range(self):
        """Test 5.2: Handles full alpha range"""
        alphas = [round(1.0 + 0.25 * i, 2) for i in range(29)]
        results = {a: max(0, 1 - (a - 1) / 7) for a in alphas}  # Fake linear decrease
        plot_results(results, "test_full_plot.png")
        assert os.path.exists("test_full_plot.png")
        os.remove("test_full_plot.png")


# =============================================================================
# Stage 6: Integration Tests
# =============================================================================

class TestStage6Integration:
    """Integration tests for the full experiment."""

    def test_small_integration(self):
        """Test 6.1: Small-scale integration test"""
        alphas = [2.0, 4.0, 6.0]
        results = run_experiment(30, alphas, trials=10)
        save_results_csv(results, "integration_test.csv", trials=10)
        plot_results(results, "integration_test.png")

        # Verify files created
        assert os.path.exists("integration_test.csv")
        assert os.path.exists("integration_test.png")

        # Cleanup
        os.remove("integration_test.csv")
        os.remove("integration_test.png")

    def test_phase_transition_visible(self):
        """Test 6.2: Phase transition is visible"""
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

    def test_main_smoke(self):
        """Test 6.3: End-to-end smoke test with small params"""
        # Run main with reduced parameters
        results = main(n=20, trials=5, seed=42,
                       results_file="smoke_test.csv",
                       plot_file="smoke_test.png")

        # Verify results structure
        assert isinstance(results, dict)
        assert len(results) == 29  # All alpha values

        # Verify files created
        assert os.path.exists("smoke_test.csv")
        assert os.path.exists("smoke_test.png")

        # Cleanup
        os.remove("smoke_test.csv")
        os.remove("smoke_test.png")
