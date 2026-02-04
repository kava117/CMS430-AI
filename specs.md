# 3-CNF-SAT Phase Transition Project Specification

## Project Overview

This project investigates the phase transition behavior of randomized 3-CNF-SAT problems as a function of the clause-to-variable ratio. The goal is to empirically demonstrate that there exists a critical ratio where problems transition from "mostly satisfiable" to "mostly unsatisfiable."

**Key Insight**: The difficulty of a randomized 3-CNF instance is determined by the clause-to-variable ratio (α = m/n), not the absolute number of variables.

- **Low ratio** (underconstrained): Few conflicts, easily satisfiable
- **High ratio** (overconstrained): Many conflicts, quickly proven unsatisfiable  
- **Critical ratio** (~4.26 for 3-SAT): Sharp phase transition occurs

## Experimental Parameters

### Fixed Parameters
- **n** = 100 (number of boolean variables, fixed throughout)
- **Trials per ratio** = 100 (number of random instances generated for each α value)
- **Ratio range** = [1.0, 8.0] in steps of 0.25
  - This gives 29 different α values: 1.0, 1.25, 1.50, ..., 7.75, 8.0

### Variable Parameters
- **α** (clause-to-variable ratio): Varies from 1.0 to 8.0
- **m** (number of clauses): Calculated as `int(n * α)` for each ratio

## Data Representation

### Variable and Literal Encoding
- Variables are numbered **1 to n** (so for n=100: variables 1, 2, 3, ..., 100)
- **Positive integer k** represents the literal x_k (variable k is TRUE)
- **Negative integer -k** represents the literal ¬x_k (variable k is FALSE)

### 3-CNF Instance Format
A 3-CNF instance is represented as a **list of clauses**, where each clause is a **list of exactly 3 integers**.

**Example**:
```python
instance = [
    [1, -2, 3],      # Clause: (x₁ ∨ ¬x₂ ∨ x₃)
    [-1, 2, 3],      # Clause: (¬x₁ ∨ x₂ ∨ x₃)
    [1, 2, -3]       # Clause: (x₁ ∨ x₂ ∨ ¬x₃)
]
# This represents: (x₁ ∨ ¬x₂ ∨ x₃) ∧ (¬x₁ ∨ x₂ ∨ x₃) ∧ (x₁ ∨ x₂ ∨ ¬x₃)
```

## Component 1: Random Instance Generator

### Function Signature
```python
def generate(n: int, alpha: float) -> list[list[int]]:
    """
    Generate a random 3-CNF-SAT instance.
    
    Args:
        n: Number of boolean variables
        alpha: Clause-to-variable ratio
        
    Returns:
        List of clauses, where each clause is a list of 3 integers
    """
```

### Generation Algorithm
1. **Calculate number of clauses**: `m = int(n * alpha)`
2. **For each of the m clauses**:
   - Generate 3 literals by:
     - Randomly selecting a variable number from 1 to n (3 times, with replacement)
     - Randomly choosing polarity (positive or negative) for each selected variable
   - Store as a list of 3 integers

### Random Sampling Details
- **Sample with replacement**: A variable can appear multiple times in the same clause
  - Example: `[1, 1, -2]` is valid (though redundant: x₁ ∨ x₁ ∨ ¬x₂)
- **Each literal independently sampled**: For n variables, there are 2n possible literals
  - For n=100: 200 possible literals (1, -1, 2, -2, ..., 100, -100)
- **Uniform random selection**: Each literal has equal probability of being chosen
- **Polarity randomization**: Each variable should be negated with 50% probability

### Implementation Notes
- Use Python's `random` module for random number generation
- Consider setting a random seed for reproducibility (optional parameter)
- No need to check for or eliminate duplicate clauses
- No need to simplify clauses (e.g., don't remove duplicate literals within a clause)

### Validation Requirements
Before proceeding to the solver, test the generator:

1. **Manual inspection** on small instances (n=3 to 5, α=1.0 to 2.0):
   - Verify clause count equals `int(n * α)`
   - Verify each clause has exactly 3 literals
   - Verify all literals use valid variable numbers (1 to n)
   
2. **Automated tests**:
   - Generate 100 instances with n=10, α=2.0
   - Check all have exactly 20 clauses
   - Check all clauses have exactly 3 literals
   - Check all variable numbers are in range [1, n] or [-n, -1] (excluding 0)

3. **Distribution check**:
   - Generate many clauses and verify variables appear with roughly uniform frequency
   - Verify positive and negative literals appear with roughly equal frequency

## Component 2: SAT Solver

### Function Signature
```python
def solve(instance: list[list[int]]) -> bool:
    """
    Determine if a 3-CNF instance is satisfiable using backtracking search.
    
    Args:
        instance: List of clauses (each clause is a list of 3 integers)
        
    Returns:
        True if satisfiable, False if unsatisfiable
    """
```

### Algorithm Requirements

**Core Algorithm**: Backtracking search with constraint propagation

**Minimum Requirements**:
1. **Backtracking search**:
   - Try assigning variables TRUE or FALSE
   - Recursively attempt to satisfy remaining clauses
   - Backtrack when a conflict is detected

2. **Constraint propagation** (at minimum, unit propagation):
   - **Unit clause**: A clause with only one unassigned literal
   - When a unit clause exists, the literal must be TRUE
   - Propagate this forced assignment before continuing search

3. **Conflict detection**:
   - If any clause has all literals FALSE, the current assignment is invalid
   - If a unit clause's literal is already FALSE, backtrack immediately

**Optional Enhancements** (implement if needed for performance):
- Pure literal elimination
- Two-watched literals
- More sophisticated variable ordering heuristics
- Clause learning (CDCL style)

### Output Requirements
- **Return value**: `True` if satisfiable, `False` if unsatisfiable
- **Do NOT print** satisfying assignments during the experiment
- **Do NOT print** search progress during the experiment
- Minimize all output to avoid slowing down the 2,900 trials (29 ratios × 100 trials)

### Optional: Return Satisfying Assignment for Testing
For validation purposes, you may want to return the satisfying assignment:
```python
def solve(instance: list[list[int]], return_assignment: bool = False) -> bool | tuple[bool, dict]:
    # If return_assignment is True, return (is_sat, assignment_dict)
    # where assignment_dict maps variable number to True/False
```

### Validation Requirements

**Known SAT Instances** (create manual test cases):
1. Simple satisfiable: `[[1, 2, 3]]` → TRUE (any assignment works)
2. Unit clauses: `[[1, 1, 1], [2, 2, 2]]` → TRUE (x₁=T, x₂=T satisfies)
3. Horn clauses or other easy satisfiable patterns

**Known UNSAT Instances**:
1. Simple conflict: `[[1, 1, 1], [-1, -1, -1]]` → FALSE
2. Larger UNSAT: Create a pigeonhole-style formula known to be unsatisfiable

**Validation Process**:
1. Test on manual SAT instances, verify returns `True`
2. Test on manual UNSAT instances, verify returns `False`
3. For SAT instances where you return the assignment:
   - Verify the assignment actually satisfies all clauses
   - Create a validator function: `verify_solution(instance, assignment) -> bool`

**Automated Testing on Generated Instances**:
- Generate instances with very low α (e.g., α=1.0): expect ~100% satisfiable
- Generate instances with very high α (e.g., α=8.0): expect ~100% unsatisfiable
- If results don't match expectations, debug before proceeding

## Component 3: Experimental Harness

### Function Signature
```python
def run_experiment(n: int, alpha_values: list[float], trials: int = 100) -> dict:
    """
    Run the phase transition experiment.
    
    Args:
        n: Number of variables (fixed at 100)
        alpha_values: List of clause-to-variable ratios to test
        trials: Number of random instances per ratio
        
    Returns:
        Dictionary mapping alpha -> fraction of satisfiable instances
    """
```

### Experimental Procedure

For each α in [1.0, 1.25, 1.50, ..., 7.75, 8.0]:

1. Initialize satisfiable count: `sat_count = 0`
2. For trial in range(100):
   - Generate random instance: `instance = generate(n, alpha)`
   - Solve instance: `is_sat = solve(instance)`
   - If `is_sat` is True: `sat_count += 1`
3. Calculate fraction: `sat_fraction = sat_count / 100`
4. Store result: `results[alpha] = sat_fraction`

### Progress Reporting (Optional but Recommended)
Since this experiment runs 2,900 trials, consider printing periodic progress:
```
Testing alpha = 1.00... (100 trials) → 98% satisfiable
Testing alpha = 1.25... (100 trials) → 96% satisfiable
...
Testing alpha = 4.25... (100 trials) → 51% satisfiable
...
Testing alpha = 8.00... (100 trials) → 2% satisfiable
```

### Data Persistence (Recommended)
Save intermediate results to a CSV file in case the experiment crashes:
```csv
alpha,sat_fraction,sat_count,total_trials
1.00,0.98,98,100
1.25,0.96,96,100
...
```

### Implementation Notes
- Use `alpha_values = [round(1.0 + 0.25 * i, 2) for i in range(29)]` to generate ratios
- Consider adding a `random_seed` parameter for reproducibility
- Optionally add a progress bar (e.g., using `tqdm`)

## Component 4: Visualization

### Function Signature
```python
def plot_results(results: dict, output_file: str = "phase_transition.png"):
    """
    Create a plot showing the phase transition.
    
    Args:
        results: Dictionary mapping alpha -> sat_fraction
        output_file: Path to save the plot
    """
```

### Plot Requirements

**Plot Type**: Line plot with markers

**Axes**:
- **X-axis**: Clause-to-variable ratio (α)
  - Range: 1.0 to 8.0
  - Label: "Clause-to-Variable Ratio (α = m/n)" or similar
  
- **Y-axis**: Fraction of satisfiable instances
  - Range: 0.0 to 1.0
  - Label: "Fraction of Satisfiable Instances" or similar

**Visual Elements**:
- Plot data points as markers (e.g., circles)
- Connect points with a line
- Add a grid for readability
- Add a title: "Phase Transition in Random 3-CNF-SAT (n=100)"

**Expected Behavior**:
- Low α values (1.0 - 3.0): Fraction near 1.0 (mostly satisfiable)
- High α values (6.0 - 8.0): Fraction near 0.0 (mostly unsatisfiable)
- Critical region (around α ≈ 4.26): Sharp transition/drop-off

**Optional Enhancements**:
- Mark the theoretical critical ratio (α ≈ 4.26) with a vertical line
- Add error bars (requires tracking individual trial results)
- Use a sigmoid curve fit to estimate the transition point

### Implementation
- Use `matplotlib.pyplot` for plotting
- Save plot to file (PNG or PDF)
- Optionally display plot interactively

**Example Code Structure**:
```python
import matplotlib.pyplot as plt

def plot_results(results, output_file="phase_transition.png"):
    alphas = sorted(results.keys())
    fractions = [results[a] for a in alphas]
    
    plt.figure(figsize=(10, 6))
    plt.plot(alphas, fractions, marker='o', linestyle='-', linewidth=2, markersize=6)
    plt.xlabel("Clause-to-Variable Ratio (α = m/n)", fontsize=12)
    plt.ylabel("Fraction of Satisfiable Instances", fontsize=12)
    plt.title("Phase Transition in Random 3-CNF-SAT (n=100)", fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.xlim(0.5, 8.5)
    plt.ylim(-0.05, 1.05)
    
    # Optional: Mark theoretical transition
    plt.axvline(x=4.26, color='red', linestyle='--', alpha=0.5, label='Theoretical transition')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    plt.show()
```

## Component 5: Main Driver

### Main Execution Flow
```python
def main():
    """
    Main driver for the 3-CNF-SAT phase transition experiment.
    """
    # Parameters
    n = 100
    alpha_values = [round(1.0 + 0.25 * i, 2) for i in range(29)]
    trials = 100
    
    print(f"Running phase transition experiment:")
    print(f"  Variables: n = {n}")
    print(f"  Alpha range: {min(alpha_values)} to {max(alpha_values)}")
    print(f"  Trials per alpha: {trials}")
    print(f"  Total trials: {len(alpha_values) * trials}")
    print()
    
    # Run experiment
    results = run_experiment(n, alpha_values, trials)
    
    # Save results
    save_results_csv(results, "results.csv")
    
    # Plot results
    plot_results(results, "phase_transition.png")
    
    print("\nExperiment complete!")
    print(f"Results saved to: results.csv")
    print(f"Plot saved to: phase_transition.png")

if __name__ == "__main__":
    main()
```

## Testing Strategy

### Stage 1: Test Generator
1. Manually inspect generated instances with n=3, α=1.5
2. Verify clause count, literal format, variable range
3. Generate 1000 clauses and check distribution statistics

### Stage 2: Test Solver
1. Test on hand-crafted SAT instances (verify returns `True`)
2. Test on hand-crafted UNSAT instances (verify returns `False`)
3. For SAT instances, verify returned assignments actually satisfy all clauses
4. Test on generated instances with extreme α values:
   - α = 1.0: Should be ~100% SAT
   - α = 8.0: Should be ~100% UNSAT

### Stage 3: Small-Scale Experiment
Before running the full experiment:
1. Test with n=20, α ∈ [2.0, 6.0, 0.5], trials=10
2. Verify the experiment completes without errors
3. Check that results show expected trend (high SAT at low α, low SAT at high α)

### Stage 4: Full Experiment
Run with specified parameters and generate final plot

## Expected Results

### Qualitative Behavior
- **α < 3.0**: >90% of instances satisfiable
- **α ≈ 4.26**: Sharp transition (30-70% satisfiable)
- **α > 6.0**: <10% of instances satisfiable

### Phase Transition Characteristics
- The transition should be relatively sharp (not gradual)
- The transition point should be near α ≈ 4.26 (theoretical value for 3-SAT)
- The curve should be roughly sigmoid-shaped

### Troubleshooting
If results don't show expected behavior:
1. **No transition visible**: Check solver for bugs (may be returning wrong results)
2. **Transition at wrong α**: Verify clause count calculation `int(n * α)`
3. **Too gradual transition**: May need more trials (increase from 100 to 200+)
4. **Noisy results**: Expected with only 100 trials; smooth with moving average

## Code Organization

### Recommended File Structure
```
3cnf_sat_experiment.py
├── generate(n, alpha) -> list[list[int]]
├── solve(instance) -> bool
├── verify_solution(instance, assignment) -> bool  [optional, for testing]
├── run_experiment(n, alpha_values, trials) -> dict
├── save_results_csv(results, filename)
├── plot_results(results, output_file)
└── main()
```

### Dependencies
- Python 3.8+
- `random` (standard library)
- `matplotlib` (for plotting)
- Optional: `numpy` (for statistical analysis), `tqdm` (for progress bars)

## Performance Considerations

### Expected Runtime
- Each trial: ~0.01 to 1 second (depending on α and solver efficiency)
- Total experiment: ~5-30 minutes for 2,900 trials
- Slowest region: Around the phase transition (α ≈ 4.0-4.5)

### Optimization Tips if Needed
1. **Start simple**: Get correctness first, optimize later
2. **Profile first**: Identify bottlenecks before optimizing
3. **Solver optimizations**:
   - Implement unit propagation (biggest win)
   - Use efficient data structures (sets for fast lookup)
   - Add timeout for very hard instances
4. **Parallel processing**: Run trials in parallel (use `multiprocessing`)

## Deliverables

1. **Python script**: `3cnf_sat_experiment.py` (working implementation)
2. **Results data**: `results.csv` (alpha values and sat fractions)
3. **Plot**: `phase_transition.png` (visualization of phase transition)
4. **Brief report** (optional): Observations about the transition point and behavior

## Additional Notes

### Reproducibility
Consider adding a `--seed` command-line argument to set the random seed:
```python
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--seed', type=int, default=None)
args = parser.parse_args()
if args.seed is not None:
    random.seed(args.seed)
```

### Extensions (Optional)
- Test different values of n (does transition point change?)
- Test k-SAT for different k (3-SAT vs 4-SAT vs 5-SAT)
- Measure and plot solver runtime vs. α
- Implement more sophisticated solvers (CDCL, WalkSAT)
- Analyze hardness: plot number of backtracks vs. α

### Common Pitfalls to Avoid
1. **Off-by-one errors**: Variables are 1 to n, not 0 to n-1
2. **Negation errors**: Make sure -k represents ¬x_k consistently
3. **Floating point**: Use `round(alpha, 2)` to avoid issues like 4.000000001
4. **Solver bugs**: Thoroughly test before running full experiment
5. **Memory**: Don't store all 2,900 instances in memory simultaneously

---

## Summary Checklist

- [ ] `generate(n, alpha)` function implemented and tested
- [ ] `solve(instance)` function implemented and tested  
- [ ] Solver verified on known SAT and UNSAT instances
- [ ] `run_experiment()` function implemented
- [ ] Results saved to CSV
- [ ] Plot generated showing phase transition
- [ ] Transition point observed near α ≈ 4.26
- [ ] Code is well-documented and organized