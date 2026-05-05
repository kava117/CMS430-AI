import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

CHARS = ['.'] + list('abcdefghijklmnopqrstuvwxyz')
CHAR_TO_IDX = {c: i for i, c in enumerate(CHARS)}
IDX_TO_CHAR = {i: c for i, c in enumerate(CHARS)}


def build_bigram_matrix(names: list) -> np.ndarray:
    matrix = np.zeros((27, 27), dtype=int)
    for name in names:
        wrapped = '.' + name.lower() + '.'
        for a, b in zip(wrapped, wrapped[1:]):
            i = CHAR_TO_IDX[a]
            j = CHAR_TO_IDX[b]
            matrix[i][j] += 1
    return matrix


def save_heatmap(matrix: np.ndarray, title: str, filepath: str, vmax: int):
    fig, ax = plt.subplots(figsize=(16, 14))
    sns.heatmap(
        matrix,
        ax=ax,
        xticklabels=CHARS,
        yticklabels=CHARS,
        cmap='YlOrRd',
        vmax=vmax,
    )
    ax.set_xlabel('Second letter (follows)')
    ax.set_ylabel('First letter (starts)')
    ax.set_title(title)
    plt.tight_layout()
    plt.savefig(filepath, dpi=150)
    plt.close()


def ensure_output_dir():
    os.makedirs('output', exist_ok=True)
