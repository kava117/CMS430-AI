# Makemore Name Analysis — Project Specification

## Overview

This project consists of two Python scripts that analyze the statistical properties of name datasets using bigram transition matrices and heatmap visualizations. Script 1 analyzes an existing dataset of real names and generates new names statistically. Script 2 analyzes a set of externally provided generated names and compares their statistical properties to the original dataset.

---

## Repository & File Structure

```
project-root/
├── makemore/
│   └── names.txt               # source dataset, one name per line
├── analyze.py                  # Script 1: analyze names.txt, generate names
├── compare.py                  # Script 2: analyze makemore-generated names
├── utils.py                    # shared utility functions used by both scripts
├── generated_names.txt         # provided externally: one name per line, plain text
└── output/
    ├── heatmap_original.png
    ├── heatmap_generated.png
    └── novel_names.txt         # auto-produced by compare.py
```

---

## Dependencies

```
pip install numpy matplotlib seaborn
```

---

## Shared Utilities: `utils.py`

Both scripts share the following logic. Place it in `utils.py` and import from it.

### Character Set

- 27 characters total: `.` followed by `a` through `z`
- `CHARS = ['.'] + list('abcdefghijklmnopqrstuvwxyz')`
- `CHAR_TO_IDX = {c: i for i, c in enumerate(CHARS)}`
- `IDX_TO_CHAR = {i: c for i, c in enumerate(CHARS)}`

### `build_bigram_matrix(names: list[str]) -> np.ndarray`

- Takes a list of raw name strings
- Wraps each name with `.` on both ends (e.g. `chelsea` → `.chelsea.`)
- Builds and returns a 27×27 numpy integer matrix where `matrix[i][j]` is the number of times character `j` follows character `i` across all names

### `save_heatmap(matrix: np.ndarray, title: str, filepath: str, vmax: int)`

- Renders `matrix` as a heatmap using `seaborn.heatmap()`
- x-axis: second letter (character that follows), labeled with `CHARS`
- y-axis: first letter (starting character), labeled with `CHARS`
- Colormap: `'YlOrRd'`
- `vmax` is passed directly to `seaborn.heatmap()` to fix the color scale ceiling
- Figure size: 16×14 inches
- Title set to the `title` parameter
- Saves to `filepath` at 150 DPI
- Does not display interactively — calls `plt.savefig()` then `plt.close()`

### `ensure_output_dir()`

- Creates the `output/` directory if it does not already exist
- Called at the start of both scripts

---

## Script 1: `analyze.py`

### Purpose
Read `makemore/names.txt`, build a bigram transition matrix, save a heatmap, and generate 25 new names using the statistical model.

---

### Step 1: Load and Preprocess Names

- Read `makemore/names.txt`, one name per line
- Strip whitespace and convert all names to lowercase
- Skip any empty lines

---

### Step 2: Build and Save the Heatmap

- Call `build_bigram_matrix()` from `utils.py` with the loaded names
- Compute `vmax` as the maximum value in the matrix
- Print `vmax` to stdout in the format: `Original heatmap vmax: N`
  - This value is needed when running `compare.py` to align color scales
- Call `save_heatmap()` with:
  - `title = "Bigram Transition Counts — Original Names"`
  - `filepath = "output/heatmap_original.png"`
  - `vmax` as computed above
- Print confirmation: `Saved output/heatmap_original.png`

---

### Step 3: Generate 25 Names Using the Statistical Model

- Normalize the raw count matrix into a probability matrix:
  - For each row, divide by the row sum
  - If a row sum is zero, leave the row as zero
- Use the probability matrix to generate names via the following algorithm:

```
for each of 25 accepted names needed:
    current_char = '.'
    name = ''

    loop:
        get the probability row for current_char
        sample the next character using numpy.random.choice
            with p = probability row for current_char

        if next_char == '.':
            break
        else:
            name += next_char
            current_char = next_char

    if len(name) >= 3:
        count this as an accepted name and print it
    else:
        do not count it; try again
```

- Print all 25 accepted names to stdout, one per line
- Names must have at least 3 characters (not counting dot markers)

---

## Script 2: `compare.py`

### Purpose
Read `generated_names.txt`, filter it against the original training set to retain only novel names, save those names, build a bigram transition matrix, and save a heatmap.

### Input File Format: `generated_names.txt`

This file is provided externally and is not produced by any script in this project. It must be:
- Plain text, UTF-8 encoded
- One name per line
- Names may be mixed case — the script will normalize to lowercase
- May contain duplicates — the script will deduplicate
- May contain names that also appear in the training set — the script will filter these out

---

### Step 1: Load the Original Name Set

- Read `makemore/names.txt` into a Python set
- Normalize to lowercase and strip whitespace
- This is the reference set used to identify novel names

---

### Step 2: Load, Deduplicate, and Filter Generated Names

- Read `generated_names.txt`, one name per line
- Normalize to lowercase and strip whitespace
- Skip empty lines
- Deduplicate while preserving order (use a seen set)
- Remove any name that appears in the original name set
- If fewer than 200 novel names remain after filtering, print a warning:
  ```
  Warning: only N novel names found. Add more names to generated_names.txt.
  ```
  and continue with however many are available
- Save the final filtered list to `output/novel_names.txt`, one name per line
- Print to stdout: `Retained N novel names for analysis.`

---

### Step 3: Build and Save the Heatmap

- Call `build_bigram_matrix()` from `utils.py` with the novel names list
- Accept `vmax` as a command-line argument: `--vmax N`
  - If provided, pass it to `save_heatmap()` to align the color scale with the original heatmap
  - If not provided, compute `vmax` as the maximum value in this matrix
- Call `save_heatmap()` with:
  - `title = "Bigram Transition Counts — Makemore Generated Names"`
  - `filepath = "output/heatmap_generated.png"`
  - `vmax` as determined above
- Print confirmation: `Saved output/heatmap_generated.png`

---

## Color Scale Alignment

To make the two heatmaps visually comparable, they should use the same `vmax`. The recommended workflow is:

1. Run `analyze.py` first. Note the printed `vmax` value.
2. Run `compare.py --vmax N` using that value.

This ensures both heatmaps use the same color scale ceiling.

---

## Output Summary

| File | Produced by | Description |
|------|-------------|-------------|
| `output/heatmap_original.png` | `analyze.py` | Bigram heatmap from `names.txt` |
| `output/heatmap_generated.png` | `compare.py` | Bigram heatmap from novel generated names |
| `output/novel_names.txt` | `compare.py` | Filtered novel names used for analysis |
| stdout from `analyze.py` | `analyze.py` | 25 statistically generated names and vmax |
| stdout from `compare.py` | `compare.py` | Retained name count and confirmation |

---

## Constraints and Notes

- All matrix operations must use `numpy` — no manual Python loops for matrix math
- The character ordering must be consistent between both scripts: `.` first, then `a–z`, defined once in `utils.py`
- All file paths must use `os.path.join()` — no hardcoded path separators
- Neither script should display plots interactively
- Both scripts must call `ensure_output_dir()` before writing any output files