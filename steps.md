# Makemore Name Analysis — Build Steps

## Step 1: Project Scaffold

Create the directory structure and install dependencies.

```
project-root/
├── makemore/
│   └── names.txt
├── output/           ← will be auto-created by scripts
├── utils.py
├── analyze.py
└── compare.py
```

**Install dependencies:**
```bash
pip install numpy matplotlib seaborn
```

**Test:** Confirm `makemore/names.txt` exists and has names (one per line). Run:
```bash
wc -l makemore/names.txt
head -5 makemore/names.txt
```

---

## Step 2: Implement `utils.py`

Implement three shared utilities:

1. **`CHARS`, `CHAR_TO_IDX`, `IDX_TO_CHAR`** — 27-character set (`.` then `a–z`)
2. **`build_bigram_matrix(names)`** — wraps each name with `.`, builds 27×27 numpy count matrix
3. **`save_heatmap(matrix, title, filepath, vmax)`** — saves seaborn heatmap, 16×14 inches, `YlOrRd`, 150 DPI, no interactive display
4. **`ensure_output_dir()`** — creates `output/` if it doesn't exist

**Test manually:**
```python
# python3 -c "..."
from utils import CHARS, build_bigram_matrix, ensure_output_dir
assert len(CHARS) == 27
assert CHARS[0] == '.'
m = build_bigram_matrix(['ann', 'bob'])
assert m.shape == (27, 27)
ensure_output_dir()
import os; assert os.path.isdir('output')
print("utils.py OK")
```

---

## Step 3: Implement `analyze.py` — Load & Heatmap

Implement the first two steps of `analyze.py`:

1. Read `makemore/names.txt` — strip, lowercase, skip blank lines
2. Call `build_bigram_matrix()`, compute `vmax` (matrix max)
3. Print: `Original heatmap vmax: N`
4. Call `save_heatmap()` → `output/heatmap_original.png`
5. Print: `Saved output/heatmap_original.png`

**Test:**
```bash
python3 analyze.py
```
Expected output includes:
```
Original heatmap vmax: <some integer>
Saved output/heatmap_original.png
```
Confirm `output/heatmap_original.png` exists and is a valid image file.

---

## Step 4: Implement `analyze.py` — Name Generation

Add name generation to `analyze.py`:

1. Normalize bigram matrix rows into probabilities (divide by row sum; skip zero rows)
2. Loop until 25 names accepted: start from `.`, sample next char via `numpy.random.choice`, stop at `.`, skip names shorter than 3 characters
3. Print each accepted name to stdout

**Test:**
```bash
python3 analyze.py
```
Expected: 25 names printed, each at least 3 characters, all lowercase. Re-run a few times to confirm non-deterministic output. Confirm `output/heatmap_original.png` is still produced correctly.

---

## Step 5: Implement `compare.py` — Load & Filter

Implement the first two steps of `compare.py`:

1. Read `makemore/names.txt` into a lowercase set (reference)
2. Accept `--vmax N` as an optional CLI argument (`argparse`)
3. Read `generated_names.txt` — lowercase, strip, skip blanks, deduplicate in order, remove names in the reference set
4. If fewer than 200 novel names remain, print warning: `Warning: only N novel names found. Add more names to generated_names.txt.`
5. Save filtered list to `output/novel_names.txt`
6. Print: `Retained N novel names for analysis.`

**Test with a stub file:**
```bash
# Create a minimal generated_names.txt for testing
echo -e "emma\nzorblax\nXylia\nemma\nann" > generated_names.txt
python3 compare.py
```
Expected:
- `emma` and `ann` filtered out (in original set)
- `zorblax` and `xylia` retained (novel, deduped, lowercased)
- Warning printed (fewer than 200 novel names)
- `output/novel_names.txt` contains only the novel names

---

## Step 6: Implement `compare.py` — Heatmap

Add heatmap generation to `compare.py`:

1. Call `build_bigram_matrix()` on the novel names list
2. If `--vmax` provided, use it; otherwise compute from matrix max
3. Call `save_heatmap()` → `output/heatmap_generated.png`
4. Print: `Saved output/heatmap_generated.png`

**Test:**
```bash
python3 compare.py
python3 compare.py --vmax 200
```
Confirm `output/heatmap_generated.png` is produced both times. With `--vmax`, the color scale ceiling should be fixed regardless of the generated dataset's actual max.

---

## Step 7: End-to-End Test (Stub Data)

Run both scripts in sequence with the stub `generated_names.txt` and verify all outputs are produced cleanly.

```bash
python3 analyze.py
python3 compare.py --vmax <N from above>
```

Verify:
- `output/heatmap_original.png` — exists, non-zero size
- `output/heatmap_generated.png` — exists, non-zero size
- `output/novel_names.txt` — contains only names not in `makemore/names.txt`
- No script crashes or interactive plot windows open

---

## Step 8: Run with Real `generated_names.txt` (Makemore Output)

Replace the stub `generated_names.txt` with the file produced by makemore (one name per line, any casing). Then run the full pipeline:

```bash
python3 analyze.py
```
Note the printed `vmax` value, then:
```bash
python3 compare.py --vmax <N>
```

**Verify:**
- At least 200 novel names retained (no warning printed)
- `output/novel_names.txt` populated with filtered novel names
- Both heatmaps saved with aligned color scales for visual comparison
- Visually compare `heatmap_original.png` vs `heatmap_generated.png` — the generated names should show similar but distinct bigram patterns vs. the training set
