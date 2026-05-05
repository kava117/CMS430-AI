import os
import argparse
import numpy as np
from utils import build_bigram_matrix, save_heatmap, ensure_output_dir

ensure_output_dir()

parser = argparse.ArgumentParser()
parser.add_argument('--vmax', type=int, default=None)
args = parser.parse_args()

# Step 1: Load original name set as reference
names_path = os.path.join('makemore', 'names.txt')
with open(names_path, 'r', encoding='utf-8') as f:
    original_names = {line.strip().lower() for line in f if line.strip()}

# Step 2: Load, deduplicate, and filter generated names
generated_path = 'generated_names.txt'
with open(generated_path, 'r', encoding='utf-8') as f:
    raw_lines = [line.strip().lower() for line in f if line.strip()]

seen = set()
novel_names = []
for name in raw_lines:
    if name not in seen:
        seen.add(name)
        if name not in original_names:
            novel_names.append(name)

if len(novel_names) < 200:
    print(f'Warning: only {len(novel_names)} novel names found. Add more names to generated_names.txt.')

novel_path = os.path.join('output', 'novel_names.txt')
with open(novel_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(novel_names) + '\n')

print(f'Retained {len(novel_names)} novel names for analysis.')

# Step 3: Build and save heatmap
matrix = build_bigram_matrix(novel_names)
vmax = args.vmax if args.vmax is not None else int(matrix.max())
save_heatmap(
    matrix,
    title='Bigram Transition Counts — Makemore Generated Names',
    filepath=os.path.join('output', 'heatmap_generated.png'),
    vmax=vmax,
)
print('Saved output/heatmap_generated.png')
