import numpy as np
from ga import (initialize_population, roulette_select, crossover, mutate,
                evolve, POPULATION_SIZE, N_ELITES, MUTATION_RATE)


def test_initialize_population_size():
    pop = initialize_population(50)
    assert len(pop) == 50


def test_initialize_population_default_size():
    pop = initialize_population()
    assert len(pop) == POPULATION_SIZE


def test_initialize_population_chromosome_shape():
    pop = initialize_population(10)
    for chrom in pop:
        assert chrom.shape == (260,)


def test_roulette_select_returns_copy():
    pop = initialize_population(10)
    fitnesses = np.random.uniform(0.4, 0.5, size=10)
    selected = roulette_select(pop, fitnesses)
    assert selected.shape == (260,)
    assert selected is not pop[0]  # must be a copy


def test_roulette_select_uniform_when_all_zero():
    pop = initialize_population(10)
    fitnesses = np.zeros(10)
    selected = roulette_select(pop, fitnesses)  # should not raise ZeroDivisionError
    assert selected.shape == (260,)


def test_crossover_output_shapes():
    pop = initialize_population(2)
    c1, c2 = crossover(pop[0], pop[1])
    assert c1.shape == (260,)
    assert c2.shape == (260,)


def test_crossover_combines_parents():
    a = np.zeros(260, dtype=np.uint8)
    b = np.ones(260, dtype=np.uint8)
    c1, c2 = crossover(a, b)
    # Each child must be composed entirely of 0s and 1s from parents
    assert set(c1).issubset({0, 1})
    assert set(c2).issubset({0, 1})
    # Together they contain all bits from both parents
    assert not np.array_equal(c1, a) or not np.array_equal(c2, b)


def test_mutate_returns_copy():
    chrom = np.zeros(260, dtype=np.uint8)
    mutated = mutate(chrom, rate=0.0)
    assert mutated is not chrom
    assert np.array_equal(mutated, chrom)


def test_mutate_zero_rate_unchanged():
    chrom = np.zeros(260, dtype=np.uint8)
    mutated = mutate(chrom, rate=0.0)
    assert np.array_equal(mutated, chrom)


def test_mutate_full_rate_all_flipped():
    chrom = np.zeros(260, dtype=np.uint8)
    mutated = mutate(chrom, rate=1.0)
    assert np.all(mutated == 1)


def test_evolve_population_size_preserved():
    pop = initialize_population(POPULATION_SIZE)
    fitnesses = np.random.uniform(0.4, 0.5, size=POPULATION_SIZE)
    new_pop = evolve(pop, fitnesses)
    assert len(new_pop) == POPULATION_SIZE


def test_evolve_elites_preserved():
    pop = initialize_population(POPULATION_SIZE)
    fitnesses = np.random.uniform(0.4, 0.5, size=POPULATION_SIZE)
    top_indices = np.argsort(fitnesses)[-N_ELITES:][::-1]
    top_chroms = [pop[i].copy() for i in top_indices]
    new_pop = evolve(pop, fitnesses)
    found = sum(any(np.array_equal(e, c) for c in new_pop) for e in top_chroms)
    assert found == N_ELITES


def test_run_ga_history_length():
    import ga as ga_module
    orig_gen = ga_module.N_GENERATIONS
    orig_size = ga_module.POPULATION_SIZE
    orig_hands = ga_module.N_HANDS
    ga_module.N_GENERATIONS = 3
    ga_module.POPULATION_SIZE = 10
    ga_module.N_HANDS = 50
    final_pop, history = ga_module.run_ga()
    ga_module.N_GENERATIONS = orig_gen
    ga_module.POPULATION_SIZE = orig_size
    ga_module.N_HANDS = orig_hands
    assert len(history) == 3
    assert all(k in history[0] for k in ('generation', 'min', 'max', 'mean', 'median'))
    assert len(final_pop) == 10
