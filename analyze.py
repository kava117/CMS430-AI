import os
import numpy as np
from utils import CHARS, CHAR_TO_IDX, build_bigram_matrix, save_heatmap, ensure_output_dir

ensure_output_dir()

# Step 1: Load and preprocess names
names_path = os.path.join('makemore', 'names.txt')
with open(names_path, 'r', encoding='utf-8') as f:
    names = [line.strip().lower() for line in f if line.strip()]

# Step 2: Build and save heatmap
matrix = build_bigram_matrix(names)
vmax = int(matrix.max())
print(f'Original heatmap vmax: {vmax}')
save_heatmap(
    matrix,
    title='Bigram Transition Counts — Original Names',
    filepath=os.path.join('output', 'heatmap_original.png'),
    vmax=vmax,
)
print('Saved output/heatmap_original.png')

# Step 3: Generate 25 names using the statistical model
row_sums = matrix.sum(axis=1, keepdims=True)
prob_matrix = np.where(row_sums > 0, matrix / row_sums, 0.0)
save_heatmap(
    prob_matrix,
    title='Bigram Transition Probabilities — Original Names',
    filepath=os.path.join('output', 'heatmap_prob_original.png'),
    vmax=float(prob_matrix.max()),
)
print('Saved output/heatmap_prob_original.png')

generated = []
while len(generated) < 25:
    current_char = '.'
    name = ''
    while True:
        row = prob_matrix[CHAR_TO_IDX[current_char]]
        next_char = np.random.choice(CHARS, p=row)
        if next_char == '.':
            break
        name += next_char
        current_char = next_char
    if len(name) >= 3:
        generated.append(name)
        print(name)
