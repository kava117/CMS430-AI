"""
3-CNF-SAT Phase Transition Experiment

This module implements a complete experiment to investigate the phase transition
behavior of randomized 3-CNF-SAT problems as a function of the clause-to-variable ratio.
"""

import random
from typing import Optional

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt


def generate(n: int, alpha: float, seed: Optional[int] = None) -> list[list[int]]:
    """
    Generate a random 3-CNF-SAT instance.

    Args:
        n: Number of boolean variables (variables numbered 1 to n)
        alpha: Clause-to-variable ratio
        seed: Optional random seed for reproducibility

    Returns:
        List of clauses, where each clause is a list of 3 integers.
        Positive integer k represents literal x_k (variable k is TRUE).
        Negative integer -k represents literal ¬x_k (variable k is FALSE).
    """
    if seed is not None:
        random.seed(seed)

    m = int(n * alpha)  # Number of clauses
    instance = []

    for _ in range(m):
        clause = []
        for _ in range(3):
            # Select a variable from 1 to n
            var = random.randint(1, n)
            # Randomly choose polarity (positive or negative)
            if random.random() < 0.5:
                clause.append(var)
            else:
                clause.append(-var)
        instance.append(clause)

    return instance


def verify_solution(instance: list[list[int]], assignment: dict[int, bool]) -> bool:
    """
    Verify that an assignment satisfies all clauses in a 3-CNF instance.

    Args:
        instance: List of clauses (each clause is a list of 3 integers)
        assignment: Dictionary mapping variable numbers to True/False

    Returns:
        True if the assignment satisfies all clauses, False otherwise
    """
    for clause in instance:
        clause_satisfied = False
        for lit in clause:
            var = abs(lit)
            # Get the value of the variable (default to False if not assigned)
            var_value = assignment.get(var, False)
            # Literal is true if: positive and var is True, or negative and var is False
            if lit > 0:
                lit_value = var_value
            else:
                lit_value = not var_value

            if lit_value:
                clause_satisfied = True
                break

        if not clause_satisfied:
            return False

    return True


def solve(instance: list[list[int]], return_assignment: bool = False):
    """
    Determine if a 3-CNF instance is satisfiable using a CDCL SAT solver.

    Args:
        instance: List of clauses (each clause is a list of 3 integers)
        return_assignment: If True, return (is_sat, assignment) tuple

    Returns:
        True if satisfiable, False if unsatisfiable.
        If return_assignment is True, returns (bool, dict) where dict maps
        variable numbers to True/False values.
    """
    if not instance:
        return (True, {}) if return_assignment else True

    # Collect variables
    all_vars = set()
    for clause in instance:
        for lit in clause:
            all_vars.add(abs(lit))

    if not all_vars:
        return (True, {}) if return_assignment else True

    # Use pysat for efficient solving
    from pysat.solvers import Solver

    with Solver(name='g3') as solver:
        for clause in instance:
            solver.add_clause(list(clause))

        is_sat = solver.solve()

        if not is_sat:
            return (False, {}) if return_assignment else False

        if return_assignment:
            model = solver.get_model()
            assignment = {}
            for lit in model:
                var = abs(lit)
                assignment[var] = (lit > 0)
            # Fill in any unassigned variables
            for var in all_vars:
                if var not in assignment:
                    assignment[var] = True
            return True, assignment

        return True


def run_experiment(n: int, alpha_values: list[float], trials: int = 100,
                   verbose: bool = False) -> dict[float, float]:
    """
    Run the phase transition experiment.

    Args:
        n: Number of variables
        alpha_values: List of clause-to-variable ratios to test
        trials: Number of random instances per ratio
        verbose: If True, print progress

    Returns:
        Dictionary mapping alpha -> fraction of satisfiable instances
    """
    results = {}

    for alpha in alpha_values:
        sat_count = 0

        for trial in range(trials):
            instance = generate(n, alpha)
            if solve(instance):
                sat_count += 1

        sat_fraction = sat_count / trials
        results[alpha] = sat_fraction

        if verbose:
            print(f"Testing alpha = {alpha:.2f}... ({trials} trials) → {sat_fraction*100:.0f}% satisfiable")

    return results


def save_results_csv(results: dict[float, float], filename: str, trials: int = 100):
    """
    Save experiment results to a CSV file.

    Args:
        results: Dictionary mapping alpha -> sat_fraction
        filename: Path to output CSV file
        trials: Number of trials per alpha (for calculating sat_count)
    """
    with open(filename, 'w') as f:
        f.write("alpha,sat_fraction,sat_count,total_trials\n")
        for alpha in sorted(results.keys()):
            sat_fraction = results[alpha]
            sat_count = int(sat_fraction * trials)
            f.write(f"{alpha:.2f},{sat_fraction:.4f},{sat_count},{trials}\n")


def plot_results(results: dict[float, float], output_file: str = "phase_transition.png"):
    """
    Create a plot showing the phase transition.

    Args:
        results: Dictionary mapping alpha -> sat_fraction
        output_file: Path to save the plot
    """
    alphas = sorted(results.keys())
    fractions = [results[a] for a in alphas]

    plt.figure(figsize=(10, 6))
    plt.plot(alphas, fractions, marker='o', linestyle='-', linewidth=2, markersize=6,
             color='#2E86AB', markerfacecolor='#2E86AB', markeredgecolor='white', markeredgewidth=1)

    plt.xlabel("Clause-to-Variable Ratio (α = m/n)", fontsize=12)
    plt.ylabel("Fraction of Satisfiable Instances", fontsize=12)
    plt.title("Phase Transition in Random 3-CNF-SAT (n=100)", fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.xlim(0.5, 8.5)
    plt.ylim(-0.05, 1.05)

    # Mark theoretical transition point
    plt.axvline(x=4.26, color='red', linestyle='--', alpha=0.7, label='Theoretical transition (α ≈ 4.26)')
    plt.legend(loc='upper right')

    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    plt.close()


def main(n: int = 100, trials: int = 100, seed: Optional[int] = None,
         results_file: str = "results.csv", plot_file: str = "phase_transition.png"):
    """
    Main driver for the 3-CNF-SAT phase transition experiment.

    Args:
        n: Number of variables (default 100)
        trials: Number of trials per alpha value (default 100)
        seed: Optional random seed for reproducibility
        results_file: Path to save results CSV
        plot_file: Path to save plot image
    """
    if seed is not None:
        random.seed(seed)

    # Generate alpha values from 1.0 to 8.0 in steps of 0.25
    alpha_values = [round(1.0 + 0.25 * i, 2) for i in range(29)]

    print(f"Running phase transition experiment:")
    print(f"  Variables: n = {n}")
    print(f"  Alpha range: {min(alpha_values)} to {max(alpha_values)}")
    print(f"  Trials per alpha: {trials}")
    print(f"  Total trials: {len(alpha_values) * trials}")
    print()

    # Run experiment
    results = run_experiment(n, alpha_values, trials, verbose=True)

    # Save results
    save_results_csv(results, results_file, trials)

    # Plot results
    plot_results(results, plot_file)

    print()
    print("Experiment complete!")
    print(f"Results saved to: {results_file}")
    print(f"Plot saved to: {plot_file}")

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="3-CNF-SAT Phase Transition Experiment")
    parser.add_argument("--n", type=int, default=100, help="Number of variables")
    parser.add_argument("--trials", type=int, default=100, help="Trials per alpha value")
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    parser.add_argument("--output-csv", type=str, default="results.csv", help="Output CSV file")
    parser.add_argument("--output-plot", type=str, default="phase_transition.png", help="Output plot file")

    args = parser.parse_args()

    main(n=args.n, trials=args.trials, seed=args.seed,
         results_file=args.output_csv, plot_file=args.output_plot)
