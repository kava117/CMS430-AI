import random
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from ga import run_ga, N_GENERATIONS, POPULATION_SIZE
from chromosome import get_decision, get_count_values
from simulator import simulate_session, evaluate_fitness

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# ---------------------------------------------------------------------------
# Run GA
# ---------------------------------------------------------------------------

final_population, history = run_ga()

# Best individual by fitness
fitnesses = np.array([evaluate_fitness(chrom, n_hands=500) for chrom in final_population])
best_chrom = final_population[int(np.argmax(fitnesses))]

# ---------------------------------------------------------------------------
# Figure 1: Bankroll Over Generations
# ---------------------------------------------------------------------------

generations = [h['generation'] for h in history]
maxes   = [h['max']    for h in history]
means   = [h['mean']   for h in history]
medians = [h['median'] for h in history]
mins    = [h['min']    for h in history]

fig1, ax1 = plt.subplots(figsize=(10, 6))
ax1.plot(generations, maxes,   color='red',    label='Max')
ax1.plot(generations, means,   color='blue',   label='Mean')
ax1.plot(generations, medians, color='green',  linestyle='--', label='Median')
ax1.plot(generations, mins,    color='orange', label='Min')
ax1.axhline(y=1000, color='grey', linestyle='--', label='Starting bankroll ($1,000)')
ax1.set_title('Blackjack Counting GA: Bankroll Over Generations')
ax1.set_xlabel('Generation')
ax1.set_ylabel('Final Bankroll ($)')
ax1.legend(loc='upper right')
ax1.grid(alpha=0.3)
fig1.tight_layout()
fig1.savefig('fitness_over_generations.png')
plt.close(fig1)

# ---------------------------------------------------------------------------
# Figure 2: Strategy Heatmap (identical to Part 1 spec)
# ---------------------------------------------------------------------------

dealer_upcards = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
x_labels = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10']

# Hard hand consensus matrix (17 rows × 10 cols)
hard_matrix = np.zeros((17, 10))
for row, total in enumerate(range(4, 21)):
    for col, upcard in enumerate(dealer_upcards):
        hard_matrix[row, col] = np.mean(
            [get_decision(c, total, False, upcard) for c in final_population]
        ) * 100

# Soft hand consensus matrix (9 rows × 10 cols)
soft_matrix = np.zeros((9, 10))
for row, total in enumerate(range(12, 21)):
    for col, upcard in enumerate(dealer_upcards):
        soft_matrix[row, col] = np.mean(
            [get_decision(c, total, True, upcard) for c in final_population]
        ) * 100

fig2, (ax_hard, ax_soft) = plt.subplots(1, 2, figsize=(16, 9))

for ax, data, y_labels, title in [
    (ax_hard, hard_matrix,
     [str(t) for t in range(4, 21)],
     'Hard Hands — % of Population Hitting'),
    (ax_soft, soft_matrix,
     [f'S{t}' for t in range(12, 21)],
     'Soft Hands — % of Population Hitting'),
]:
    im = ax.imshow(data, cmap='RdBu_r', vmin=0, vmax=100,
                   aspect='auto', origin='lower')
    ax.set_xticks(range(10))
    ax.set_xticklabels(x_labels)
    ax.set_yticks(range(len(y_labels)))
    ax.set_yticklabels(y_labels)
    ax.set_xlabel('Dealer Upcard')
    ax.set_ylabel('Player Total')
    ax.set_title(title)
    for r in range(data.shape[0]):
        for c in range(data.shape[1]):
            ax.text(c, r, str(int(data[r, c])),
                    ha='center', va='center', fontsize=7, color='black')

fig2.colorbar(im, ax=[ax_hard, ax_soft], label='% Hitting')
fig2.suptitle('Final Population Strategy Consensus (% Hitting)')
fig2.subplots_adjust(top=0.92)
fig2.savefig('strategy_heatmap.png')
plt.close(fig2)

# ---------------------------------------------------------------------------
# Figure 3: Evolved Count Values vs. Hi-Lo
# ---------------------------------------------------------------------------

hilo = {1: -1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 0, 8: 0, 9: 0, 10: -1}
card_ranks = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
rank_labels = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10']

# Mean evolved count value per rank across population
evolved_means = []
for rank in card_ranks:
    vals = []
    for chrom in final_population:
        cv = get_count_values(chrom)
        vals.append(cv[rank])
    evolved_means.append(np.mean(vals))

hilo_vals = [hilo[r] for r in card_ranks]

x = np.arange(len(card_ranks))
width = 0.35

fig3, ax3 = plt.subplots(figsize=(12, 6))
bars_evolved = ax3.bar(x - width / 2, evolved_means, width,
                       color='steelblue', label='Evolved Consensus')
bars_hilo    = ax3.bar(x + width / 2, hilo_vals,     width,
                       color='coral',     label='Hi-Lo Reference')

ax3.axhline(y=0, color='black', linestyle='--', linewidth=0.8)
ax3.set_xticks(x)
ax3.set_xticklabels(rank_labels)
ax3.set_ylim(-1.2, 1.2)
ax3.set_xlabel('Card Rank')
ax3.set_ylabel('Count Value')
ax3.set_title('Evolved Count Values vs. Hi-Lo System')
ax3.legend()
ax3.grid(alpha=0.3)

# Annotate evolved bars
for bar, val in zip(bars_evolved, evolved_means):
    sign = '+' if val >= 0 else ''
    ax3.text(bar.get_x() + bar.get_width() / 2,
             bar.get_height() + (0.03 if val >= 0 else -0.08),
             f'{sign}{val:.2f}',
             ha='center', va='bottom', fontsize=8)

fig3.tight_layout()
fig3.savefig('count_values.png')
plt.close(fig3)

# ---------------------------------------------------------------------------
# Figure 4: Best Individual — Bankroll Over Time
# ---------------------------------------------------------------------------

random.seed(SEED)
np.random.seed(SEED)
bankroll_history = simulate_session(best_chrom, n_hands=1000)
hands = list(range(1, len(bankroll_history) + 1))
bankroll_arr = np.array(bankroll_history)

fig4, ax4 = plt.subplots(figsize=(12, 6))
ax4.plot(hands, bankroll_arr, color='steelblue', linewidth=1.5)
ax4.axhline(y=1000, color='grey', linestyle='--', label='Starting bankroll')

ax4.fill_between(hands, bankroll_arr, 1000,
                 where=(bankroll_arr > 1000),
                 alpha=0.15, color='green')
ax4.fill_between(hands, bankroll_arr, 1000,
                 where=(bankroll_arr <= 1000),
                 alpha=0.15, color='red')

final_br = bankroll_arr[-1] if len(bankroll_arr) > 0 else 0
ax4.text(0.98, 0.05, f'Final: ${final_br:.0f}',
         transform=ax4.transAxes, ha='right', va='bottom', fontsize=11)

ax4.set_xlabel('Hand')
ax4.set_ylabel('Bankroll ($)')
ax4.set_title('Best Individual: Bankroll Over 1,000 Hands')
ax4.legend()
ax4.grid(alpha=0.3)
fig4.tight_layout()
fig4.savefig('bankroll_over_time.png')
plt.close(fig4)

plt.show()
