import random
import numpy as np
import matplotlib
matplotlib.use('Agg')  # non-interactive backend for headless environments
import matplotlib.pyplot as plt

from ga import run_ga, N_GENERATIONS
from chromosome import get_decision

SEED = 42
random.seed(SEED)
np.random.seed(SEED)


def build_heatmaps(final_population):
    """Compute hard (17x10) and soft (9x10) hit-percentage matrices."""
    upcards = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    hard_matrix = np.zeros((17, 10))
    for row, total in enumerate(range(4, 21)):
        for col, upcard in enumerate(upcards):
            hard_matrix[row, col] = np.mean(
                [get_decision(c, total, False, upcard) for c in final_population]
            ) * 100

    soft_matrix = np.zeros((9, 10))
    for row, total in enumerate(range(12, 21)):
        for col, upcard in enumerate(upcards):
            soft_matrix[row, col] = np.mean(
                [get_decision(c, total, True, upcard) for c in final_population]
            ) * 100

    return hard_matrix, soft_matrix


def plot_fitness(history):
    generations = [h['generation'] for h in history]
    maxes   = [h['max']    for h in history]
    means   = [h['mean']   for h in history]
    medians = [h['median'] for h in history]
    mins    = [h['min']    for h in history]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(generations, maxes,   color='red',    linestyle='-',  label='Max')
    ax.plot(generations, means,   color='blue',   linestyle='-',  label='Mean')
    ax.plot(generations, medians, color='green',  linestyle='--', label='Median')
    ax.plot(generations, mins,    color='orange', linestyle='-',  label='Min')
    ax.axhline(y=0.495, color='grey', linestyle='--', label='Theoretical optimum (~49.5%)')

    ax.set_title('Blackjack GA: Fitness Over Generations')
    ax.set_xlabel('Generation')
    ax.set_ylabel('Fitness (win rate)')
    ax.legend(loc='upper right')
    ax.grid(alpha=0.3)

    fig.tight_layout()
    fig.savefig('fitness_over_generations.png', dpi=120)
    return fig


def plot_heatmap(hard_matrix, soft_matrix):
    upcards = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    hard_yticks = [str(t) for t in range(4, 21)]
    soft_yticks = [f'S{t}' for t in range(12, 21)]

    fig, axes = plt.subplots(1, 2, figsize=(16, 9))
    fig.suptitle('Final Population Strategy Consensus (% Hitting)', fontsize=14)

    for ax, matrix, yticks, title in [
        (axes[0], hard_matrix, hard_yticks, 'Hard Hands — % of Population Hitting'),
        (axes[1], soft_matrix, soft_yticks, 'Soft Hands — % of Population Hitting'),
    ]:
        # origin='lower' puts lowest total at bottom
        im = ax.imshow(matrix, cmap='RdBu_r', vmin=0, vmax=100,
                       aspect='auto', origin='lower')
        ax.set_title(title)
        ax.set_xlabel('Dealer Upcard')
        ax.set_ylabel('Player Total')
        ax.set_xticks(range(10))
        ax.set_xticklabels(upcards)
        ax.set_yticks(range(len(yticks)))
        ax.set_yticklabels(yticks)

        for row in range(matrix.shape[0]):
            for col in range(matrix.shape[1]):
                ax.text(col, row, str(int(matrix[row, col])),
                        ha='center', va='center', fontsize=7, color='black')

        plt.colorbar(im, ax=ax, label='% Hitting')

    fig.tight_layout()
    fig.savefig('strategy_heatmap.png', dpi=120)
    return fig


if __name__ == '__main__':
    final_population, history = run_ga()

    hard_matrix, soft_matrix = build_heatmaps(final_population)

    fig1 = plot_fitness(history)
    fig2 = plot_heatmap(hard_matrix, soft_matrix)

    plt.show()
