# Implementation Steps: Iris Clustering Analysis in R

Each step ends with a **Validation** section the agent must run and pass before moving to the next step.

---

## Step 0 — Project Scaffold

Create the project directory layout and verify the R environment is ready.

**Actions:**
1. Create the top-level project directory `iris-clustering/`.
2. Create an empty `output/` subdirectory inside it.
3. Verify that `Rscript` is available on the system path.
4. Write a one-line smoke-test script `iris-clustering/check_env.R` that loads the iris dataset and prints the number of rows:
   ```r
   data(iris)
   cat(nrow(iris), "\n")
   ```

**Validation:**
```bash
cd iris-clustering
Rscript check_env.R
```
- Expected output: `150`
- The `output/` directory must exist.
- If either check fails, install R or fix the working directory before proceeding.

---

## Step 1 — Script 02: Petal Scatter Plot (`02_petal_scatter.R`)

Start with the simplest script — no clustering, no PCA — to confirm ggplot2 works and the `ggsave()` → PNG pipeline is functioning end-to-end.

**Actions:**
1. Create `iris-clustering/02_petal_scatter.R`.
2. Add header comment block: script number, title, one-sentence purpose.
3. Auto-install and load `ggplot2`.
4. Add `if (!dir.exists("output")) dir.create("output")`.
5. Load `data(iris)`.
6. Build a ggplot2 scatter plot:
   - `x = Petal.Length`, `y = Petal.Width`, `color = Species`
   - Title: `"Iris Species by Petal Measurements"`
   - Subtitle: `"Can petal measurements alone separate the three species?"`
   - `theme_minimal()`
   - Colorblind-friendly palette (e.g., `scale_color_brewer(palette = "Set2")`)
7. Save with `ggsave("output/petal_scatter.png", width = 1000/150, height = 800/150, dpi = 150)`.
8. Print: `cat("Plot saved to output/petal_scatter.png\n")`.

**Validation:**
```bash
cd iris-clustering
Rscript 02_petal_scatter.R
```
- Script exits with code 0 (no errors).
- Console prints `Plot saved to output/petal_scatter.png`.
- File `output/petal_scatter.png` exists and is non-empty (size > 0 bytes).
- Spot-check: open the PNG and confirm three visually distinct color groups appear (setosa separates cleanly in the bottom-left).

```bash
# File existence and size check
test -s output/petal_scatter.png && echo "PASS" || echo "FAIL"
```

---

## Step 2 — Script 03: Silhouette Plot (`03_silhouette.R`)

Introduces the `cluster` package and the silhouette score loop. No PCA or side-by-side plots yet.

**Actions:**
1. Create `iris-clustering/03_silhouette.R`.
2. Add header comment block.
3. Auto-install and load: `ggplot2`, `cluster`.
4. `if (!dir.exists("output")) dir.create("output")`.
5. Add the background comment block from the spec (explaining silhouette scores).
6. Load `data(iris)`.
7. Scale the four numeric columns: `iris_scaled <- scale(iris[, 1:4])`.
8. Loop `k` from 2 to 10:
   - `set.seed(42)`, run `kmeans(iris_scaled, centers = k, nstart = 25)`.
   - Compute `sil <- silhouette(km$cluster, dist(iris_scaled))`.
   - Store `mean(sil[, 3])` in a results vector.
9. Build a data frame `sil_df` with columns `k` (2:10) and `avg_sil`.
10. Find `best_k <- sil_df$k[which.max(sil_df$avg_sil)]`.
11. Build line + point plot:
    - Color the best-k point differently (e.g., red) or add a vertical dashed line at `best_k`.
    - Title: `"Average Silhouette Score by Number of Clusters (k)"`.
    - `theme_minimal()`.
12. Save: `ggsave("output/silhouette_plot.png", width = 1000/150, height = 700/150, dpi = 150)`.
13. Print completion message.

**Validation:**
```bash
cd iris-clustering
Rscript 03_silhouette.R
```
- Script exits with code 0.
- Console prints the completion message.
- File `output/silhouette_plot.png` exists and is non-empty.
- The expected optimal k for the scaled iris data is **k=2** (setosa vs. the rest); confirm `best_k` is printed or verifiable from the plot.

```bash
test -s output/silhouette_plot.png && echo "PASS" || echo "FAIL"
```

---

## Step 3 — Script 04: Hierarchical Clustering Dendrogram (`04_dendrogram.R`)

Introduces `factoextra` and hierarchical clustering with `hclust`.

**Actions:**
1. Create `iris-clustering/04_dendrogram.R`.
2. Add header comment block.
3. Auto-install and load: `factoextra`, `cluster`.
4. `if (!dir.exists("output")) dir.create("output")`.
5. Add the background comment block from the spec (explaining agglomerative clustering and Ward's linkage).
6. Load `data(iris)`.
7. Scale: `iris_scaled <- scale(iris[, 1:4])`.
8. Compute distance matrix: `dist_matrix <- dist(iris_scaled, method = "euclidean")`.
9. Run hierarchical clustering: `hclust_result <- hclust(dist_matrix, method = "ward.D2")`.
10. Visualize with `factoextra::fviz_dend()`:
    - `k = 3` (colored branches)
    - `show_labels = FALSE`
    - `main = "Hierarchical Clustering Dendrogram (Ward's Linkage, k=3)"`
11. Save with `ggsave()` or `ggplot2::ggsave()`: `output/dendrogram.png`, 1200x800 px, 150 dpi.
    - Note: `fviz_dend()` returns a ggplot object — use `ggsave()` directly.
12. Print completion message.

**Validation:**
```bash
cd iris-clustering
Rscript 04_dendrogram.R
```
- Script exits with code 0.
- `output/dendrogram.png` exists and is non-empty.
- Spot-check: three distinctly colored branch groups should be visible in the dendrogram.

```bash
test -s output/dendrogram.png && echo "PASS" || echo "FAIL"
```

---

## Step 4 — PCA Label Helper (shared logic, tested in isolation)

Both `01_kmeans.R` and `05_gmm.R` need the same PCA axis label construction. Before writing those scripts, define and manually verify the logic.

**Actions:**
1. Write a throwaway test script `iris-clustering/test_pca_labels.R` (will be deleted after validation):
   ```r
   data(iris)
   iris_scaled <- scale(iris[, 1:4])
   pca_result <- prcomp(iris_scaled, center = FALSE, scale. = FALSE)

   # Variance explained
   variance_pct <- pca_result$sdev^2 / sum(pca_result$sdev^2) * 100

   # Helper function (copy this into 01 and 05)
   make_pca_label <- function(pca_result, pc_index, variance_pct) {
     loadings <- abs(pca_result$rotation[, pc_index])
     top_idx <- which.max(loadings)
     top_val <- loadings[top_idx]
     feature_names <- rownames(pca_result$rotation)
     # Include second feature if its loading >= 70% of top
     included <- feature_names[loadings >= 0.70 * top_val]
     # Prettify names
     pretty <- gsub("\\.", " ", tolower(included))
     sprintf("PC%d (%.1f%% variance) — driven by: %s",
             pc_index, variance_pct[pc_index], paste(pretty, collapse = ", "))
   }

   cat(make_pca_label(pca_result, 1, variance_pct), "\n")
   cat(make_pca_label(pca_result, 2, variance_pct), "\n")
   ```

**Validation:**
```bash
cd iris-clustering
Rscript test_pca_labels.R
```
- Expected PC1 label mentions `petal length` and `petal width` (they dominate PC1 for iris).
- Expected PC2 label mentions `sepal width` (it dominates PC2).
- Example acceptable output:
  ```
  PC1 (72.9% variance) — driven by: petal length, petal width
  PC2 (22.5% variance) — driven by: sepal width
  ```
  (Exact percentages may differ slightly — verify they sum to ~95%+ for PC1+PC2.)
- Delete `test_pca_labels.R` after passing.

---

## Step 5 — Script 01: K-Means + PCA Side-by-Side (`01_kmeans.R`)

The most complex script: PCA, k-means, informative axis labels, and side-by-side plots via `patchwork`.

**Actions:**
1. Create `iris-clustering/01_kmeans.R`.
2. Add header comment block.
3. Auto-install and load: `ggplot2`, `patchwork`.
4. `if (!dir.exists("output")) dir.create("output")`.
5. Add the PCA explanation comment block from the spec.
6. Load `data(iris)`.
7. Scale: `iris_scaled <- scale(iris[, 1:4])`.
8. Run PCA: `pca_result <- prcomp(iris_scaled, center = FALSE, scale. = FALSE)`.
9. Extract PC scores for PC1 and PC2 into a data frame `pca_df` with columns `PC1`, `PC2`, `Species`.
10. Compute variance percentages: `variance_pct <- pca_result$sdev^2 / sum(pca_result$sdev^2) * 100`.
11. Define `make_pca_label()` helper (from Step 4) and construct `x_label` and `y_label`.
12. Run k-means on `iris_scaled`: `set.seed(42)`, `centers = 3`, `nstart = 25`. Store as `kmeans_result`.
13. Add `Cluster = factor(kmeans_result$cluster)` to `pca_df`.
14. Build **left plot** (`plot_species`): color by `Species`, title `"True Species Labels"`, `theme_minimal()`, `scale_color_brewer(palette = "Set2")`.
15. Build **right plot** (`plot_clusters`): color by `Cluster`, title `"K-Means Clusters (k=3)"`, `theme_minimal()`, `scale_color_brewer(palette = "Set2")`.
16. Both plots use `xlab = x_label`, `ylab = y_label`.
17. Combine: `combined_plot <- plot_species + plot_clusters`.
18. Save: `ggsave("output/kmeans_pca_scatter.png", combined_plot, width = 1600/150, height = 800/150, dpi = 150)`.
19. Print completion message.

**Validation:**
```bash
cd iris-clustering
Rscript 01_kmeans.R
```
- Script exits with code 0.
- `output/kmeans_pca_scatter.png` exists and is non-empty.
- PNG is wide (roughly 2:1 aspect ratio) containing two side-by-side panels.
- PC1 axis label mentions `petal length` and/or `petal width`.
- PC2 axis label mentions `sepal width`.

```bash
test -s output/kmeans_pca_scatter.png && echo "PASS" || echo "FAIL"
```

---

## Step 6 — Script 05: GMM + PCA Side-by-Side (`05_gmm.R`)

Very similar structure to `01_kmeans.R` but uses `mclust` instead of `kmeans`.

**Actions:**
1. Create `iris-clustering/05_gmm.R`.
2. Add header comment block.
3. Auto-install and load: `ggplot2`, `patchwork`, `mclust`.
4. `if (!dir.exists("output")) dir.create("output")`.
5. Add the GMM background comment block from the spec.
6. Load `data(iris)`.
7. Scale: `iris_scaled <- scale(iris[, 1:4])`.
8. Fit GMM: `set.seed(42)`, `gmm_result <- Mclust(iris_scaled, G = 3)`.
9. Extract cluster assignments: `gmm_clusters <- factor(gmm_result$classification)`.
10. Run PCA (same as Step 5) and construct the same `x_label` / `y_label` using `make_pca_label()`.
11. Build `pca_df` with `PC1`, `PC2`, `Species`, `GMMCluster = gmm_clusters`.
12. Build **left plot** (`plot_species`): color by `Species`, title `"True Species Labels"`, `theme_minimal()`, colorblind palette.
13. Build **right plot** (`plot_gmm`): color by `GMMCluster`, title `"GMM Cluster Assignments (k=3)"`, `theme_minimal()`, colorblind palette.
14. Combine with `patchwork` and save: `output/gmm_pca_scatter.png`, 1600x800 px, 150 dpi.
15. Print completion message.

**Validation:**
```bash
cd iris-clustering
Rscript 05_gmm.R
```
- Script exits with code 0.
- `output/gmm_pca_scatter.png` exists and is non-empty.
- The `mclust` package's BIC-based model selection output will appear in the console — this is expected and acceptable.

```bash
test -s output/gmm_pca_scatter.png && echo "PASS" || echo "FAIL"
```

---

## Step 7 — Full Integration Pass

Run all five scripts in order, verify all five PNGs are present, and confirm no script errors out.

**Validation:**
```bash
cd iris-clustering
Rscript 01_kmeans.R && \
Rscript 02_petal_scatter.R && \
Rscript 03_silhouette.R && \
Rscript 04_dendrogram.R && \
Rscript 05_gmm.R && \
echo "All scripts completed successfully"
```

Check all output files exist and are non-empty:
```bash
for f in output/kmeans_pca_scatter.png output/petal_scatter.png output/silhouette_plot.png output/dendrogram.png output/gmm_pca_scatter.png; do
  test -s "$f" && echo "PASS: $f" || echo "FAIL: $f"
done
```

Expected output:
```
PASS: output/kmeans_pca_scatter.png
PASS: output/petal_scatter.png
PASS: output/silhouette_plot.png
PASS: output/dendrogram.png
PASS: output/gmm_pca_scatter.png
```

Confirm all five completion messages printed (one per script). If any script fails, re-run it in isolation to diagnose the error before re-running the full integration pass.

---

## Step 8 — Code Style Audit

Do a final pass on all five scripts to ensure conformance with the spec's style requirements.

**Checklist (verify each item in each script):**

| Requirement | Check |
|---|---|
| Header comment block (script number, title, one-sentence purpose) | All 5 scripts |
| `set.seed(42)` present wherever randomness is used | 01, 03, 05 |
| No global `suppressWarnings()` | All 5 scripts |
| Descriptive variable names (`kmeans_result` not `km`) | All 5 scripts |
| `if (!dir.exists("output")) dir.create("output")` (exact wording) | All 5 scripts |
| `cat("Plot saved to output/...\n")` completion message | All 5 scripts |
| `ggsave()` called with explicit `width`, `height`, `dpi` | All 5 scripts |
| Pixel dimensions match spec (see table below) | All 5 scripts |
| Background comment block included where spec requires it | 01, 03, 04, 05 |

**Pixel dimension reference:**

| Script | Output file | Width (px) | Height (px) | DPI |
|---|---|---|---|---|
| 01 | kmeans_pca_scatter.png | 1600 | 800 | 150 |
| 02 | petal_scatter.png | 1000 | 800 | 150 |
| 03 | silhouette_plot.png | 1000 | 700 | 150 |
| 04 | dendrogram.png | 1200 | 800 | 150 |
| 05 | gmm_pca_scatter.png | 1600 | 800 | 150 |

**Validation:**
Re-run the full integration pass from Step 7 one final time after any style fixes. All five PNGs must regenerate without errors.
