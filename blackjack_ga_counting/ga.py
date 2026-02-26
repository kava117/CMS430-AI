import numpy as np
from chromosome import random_chromosome
from simulator import evaluate_fitness

POPULATION_SIZE = 100
N_GENERATIONS   = 75
N_HANDS         = 1000
MUTATION_RATE   = 0.01
N_ELITES        = 2


def initialize_population(size: int = POPULATION_SIZE) -> list:
    """Return a list of `size` random 294-bit chromosomes."""
    return [random_chromosome() for _ in range(size)]


def roulette_select(population: list, fitnesses: np.ndarray) -> np.ndarray:
    """
    Tournament selection (k=3): pick 3 individuals at random, return the fittest.

    Raw roulette wheel fails for bankroll fitness because all bankrolls cluster
    near the same value (e.g. $800–$1200), making selection probabilities nearly
    uniform and preventing play-strategy convergence. Tournament selection gives
    consistent, strong selection pressure — the best individual is always ~N/k
    times more likely to be selected than the worst — regardless of the absolute
    fitness scale or how tightly values cluster.
    """
    fitnesses = np.clip(fitnesses, 0, None)
    k = min(3, len(population))
    indices = np.random.choice(len(population), size=k, replace=False)
    best = indices[np.argmax(fitnesses[indices])]
    return population[best].copy()


def crossover(parent_a: np.ndarray, parent_b: np.ndarray) -> tuple:
    """Single-point crossover on 294-bit chromosomes. Returns two offspring."""
    point = np.random.randint(1, len(parent_a) - 1)  # [1, 292] inclusive
    child_a = np.concatenate([parent_a[:point], parent_b[point:]])
    child_b = np.concatenate([parent_b[:point], parent_a[point:]])
    return child_a, child_b


def mutate(chrom: np.ndarray, rate: float = MUTATION_RATE) -> np.ndarray:
    """Flip each bit independently with probability `rate`. Returns mutated copy."""
    mask = np.random.random(len(chrom)) < rate
    return chrom.copy() ^ mask.astype(np.uint8)


def evolve(population: list, fitnesses: np.ndarray) -> list:
    """Produce the next generation via elitism, roulette selection, crossover, mutation."""
    # Elitism: carry top N_ELITES unchanged
    sorted_indices = np.argsort(fitnesses)[::-1]
    new_population = [population[i].copy() for i in sorted_indices[:N_ELITES]]

    # Fill remainder with offspring
    while len(new_population) < POPULATION_SIZE:
        pa = roulette_select(population, fitnesses)
        pb = roulette_select(population, fitnesses)
        child_a, child_b = crossover(pa, pb)
        new_population.append(mutate(child_a))
        if len(new_population) < POPULATION_SIZE:
            new_population.append(mutate(child_b))

    return new_population[:POPULATION_SIZE]


def run_ga() -> tuple:
    """
    Run the full genetic algorithm.
    Returns: (final_population, history)
    history is a list of dicts: {'generation', 'min', 'max', 'mean', 'median'}
    Fitness values are raw bankroll amounts ($).
    """
    population = initialize_population(POPULATION_SIZE)
    history = []

    for g in range(N_GENERATIONS):
        fitnesses = np.array([evaluate_fitness(chrom, N_HANDS) for chrom in population])

        entry = {
            'generation': g,
            'min':    float(fitnesses.min()),
            'max':    float(fitnesses.max()),
            'mean':   float(fitnesses.mean()),
            'median': float(np.median(fitnesses)),
        }
        history.append(entry)

        print(f"Gen {g + 1}/{N_GENERATIONS} | "
              f"Max: ${entry['max']:.2f} | Mean: ${entry['mean']:.2f}")

        population = evolve(population, fitnesses)

    return population, history
