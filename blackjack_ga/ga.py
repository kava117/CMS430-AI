import numpy as np
from chromosome import random_chromosome
from simulator import evaluate_fitness

POPULATION_SIZE = 100
N_GENERATIONS = 75
N_HANDS = 1000
MUTATION_RATE = 0.01
N_ELITES = 2
CROSSOVER_TYPE = 'single_point'


def initialize_population(size: int = POPULATION_SIZE) -> list:
    """Return a list of `size` random chromosomes."""
    return [random_chromosome() for _ in range(size)]


def roulette_select(population: list, fitnesses: np.ndarray) -> np.ndarray:
    """Select one individual using fitness-proportional roulette wheel selection.
    Fitness windowing (subtract minimum) is applied to amplify selection pressure
    when fitness values are closely bunched.
    """
    scaled = fitnesses - fitnesses.min()
    total = scaled.sum()
    if total == 0:
        idx = np.random.randint(len(population))
    else:
        probs = scaled / total
        idx = np.random.choice(len(population), p=probs)
    return population[idx].copy()


def crossover(parent_a: np.ndarray, parent_b: np.ndarray) -> tuple:
    """Single-point crossover. Returns two offspring."""
    point = np.random.randint(1, 259)  # 1 to 258 inclusive
    child_a = np.concatenate([parent_a[:point], parent_b[point:]])
    child_b = np.concatenate([parent_b[:point], parent_a[point:]])
    return child_a, child_b


def mutate(chrom: np.ndarray, rate: float = MUTATION_RATE) -> np.ndarray:
    """Flip each bit independently with probability `rate`. Returns mutated copy."""
    chrom_copy = chrom.copy()
    mask = np.random.random(260) < rate
    chrom_copy ^= mask.astype(np.uint8)
    return chrom_copy


def evolve(population: list, fitnesses: np.ndarray) -> list:
    """Produce the next generation from the current population and its fitnesses."""
    size = len(population)
    sorted_indices = np.argsort(fitnesses)[::-1]
    next_gen = [population[i].copy() for i in sorted_indices[:N_ELITES]]

    while len(next_gen) < size:
        pa = roulette_select(population, fitnesses)
        pb = roulette_select(population, fitnesses)
        ca, cb = crossover(pa, pb)
        next_gen.append(mutate(ca))
        if len(next_gen) < size:
            next_gen.append(mutate(cb))

    return next_gen[:size]


def run_ga() -> tuple:
    """
    Run the full genetic algorithm.
    Returns:
        final_population: list of chromosomes from the last generation
        history: list of dicts, one per generation, each containing:
            {'generation': int, 'min': float, 'max': float, 'mean': float, 'median': float}
    """
    population = initialize_population(POPULATION_SIZE)
    history = []

    for g in range(N_GENERATIONS):
        fitnesses = np.array([evaluate_fitness(chrom, N_HANDS) for chrom in population])
        record = {
            'generation': g,
            'min': float(fitnesses.min()),
            'max': float(fitnesses.max()),
            'mean': float(fitnesses.mean()),
            'median': float(np.median(fitnesses)),
        }
        history.append(record)
        print(f"Gen {g + 1}/{N_GENERATIONS} | Max: {record['max']:.4f} | Mean: {record['mean']:.4f}")
        population = evolve(population, fitnesses)

    return population, history
