# Project Specs: Iris Clustering Analysis in R

## Overview

Build a modular R project that performs clustering analysis on the Fisher iris dataset. The project consists of five separate, independently runnable R scripts. All plots are saved as PNG files. The iris dataset is built into R via the `datasets` package (no external data download needed).

---

## Project Structure

```
iris-clustering/
├── 01_kmeans.R
├── 02_petal_scatter.R
├── 03_silhouette.R
├── 04_dendrogram.R
├── 05_gmm.R
└── output/
    ├── kmeans_pca_scatter.png
    ├── petal_scatter.png
    ├── silhouette_plot.png
    ├── dendrogram.png
    └── gmm_pca_scatter.png
```

Each script is self-contained: it loads its own libraries, loads the iris data, performs its analysis, saves its PNG output to the `output/` directory, and exits cleanly. The `output/` directory should be created automatically if it does not exist.

---

## Required Packages

All scripts should install missing packages automatically using the following pattern at the top of each script:

```r
if (!require("package_name")) install.packages("package_name", repos = "https://cloud.r-project.org")
library(package_name)
```

Packages needed across the project:

- `ggplot2` — all plotting
- `cluster` — silhouette scores and hierarchical clustering
- `factoextra` — PCA visualization, dendrogram visualization, silhouette plots
- `mclust` — Gaussian mixture models
- `dplyr` — data manipulation (if needed)

---

## Script Specifications

---

### 01_kmeans.R — K-Means Clustering on PCA Projection

**Purpose:** Perform PCA on the 4-feature iris dataset to reduce to 2 dimensions, run k-means clustering with k=3, and visualize both the true species labels and the cluster assignments side by side.

**Steps:**

1. Load the iris dataset.
2. Scale the four numeric features (petal length, petal width, sepal length, sepal width) using `scale()` before running PCA. This is important because PCA is sensitive to variable scale.
3. Run PCA using `prcomp()` on the scaled features.
4. Extract the **loadings** for PC1 and PC2. For each component, identify the **top 1-2 features** with the highest absolute loading values. Use these to construct human-readable axis labels in the following format:
   - `"PC1 (XX.X% variance) — driven by: petal length, petal width"`
   - `"PC2 (XX.X% variance) — driven by: sepal width"`
   The variance percentages should be computed from the PCA output (`sdev^2 / sum(sdev^2) * 100`). The threshold for including a second feature in the label is if its absolute loading is at least 70% of the top feature's absolute loading. Otherwise only list the top feature.
5. Run k-means clustering on the **scaled 4-feature data** (not the PCA projection) with `k=3`, `nstart=25` (to reduce sensitivity to initialization), and a fixed random seed (`set.seed(42)`) for reproducibility.
6. Add a **brief comment block** near the top of the script (after the library calls) explaining what PCA is in plain language. Something like:
   > "PCA (Principal Component Analysis) reduces the 4 original measurements into new composite axes that capture the most variation in the data. PC1 captures the most variation, PC2 the second most. The axis labels below show which original features drive each component."
7. Produce **two side-by-side scatter plots** on the PCA projection (PC1 vs PC2), using `ggplot2` and `patchwork` (add `patchwork` to the required packages list):
   - **Left plot:** Points colored by **true species** (Setosa, Versicolor, Virginica). Title: "True Species Labels".
   - **Right plot:** Points colored by **k-means cluster assignment** (Cluster 1, 2, 3). Title: "K-Means Clusters (k=3)".
   - Both plots share the same axis labels (the PCA labels constructed in step 4).
   - Use a clean `theme_minimal()` style.
   - Use colorblind-friendly colors (e.g., the `viridis` or `RColorBrewer "Set2"` palette).
8. Save the combined plot to `output/kmeans_pca_scatter.png` at 1600x800 pixels, 150 dpi.

---

### 02_petal_scatter.R — Petal-Only Scatter Plot

**Purpose:** Create a simple scatter plot using only petal length and petal width, colored by true species, to visually assess whether petal measurements alone can separate the three species.

**Steps:**

1. Load the iris dataset.
2. Create a scatter plot with:
   - X axis: Petal Length
   - Y axis: Petal Width
   - Points colored by Species
   - Title: `"Iris Species by Petal Measurements"`
   - Subtitle: `"Can petal measurements alone separate the three species?"`
   - Use `theme_minimal()` and colorblind-friendly colors.
3. Save to `output/petal_scatter.png` at 1000x800 pixels, 150 dpi.

---

### 03_silhouette.R — Silhouette Plot

**Purpose:** Compute silhouette scores for k-means clustering across k=2 through k=10, and plot the average silhouette score for each k to help identify the optimal number of clusters.

**Background comment to include in script:**
> "The silhouette score measures how similar a point is to its own cluster compared to other clusters. Scores range from -1 to 1: values near 1 mean the point is well-matched to its cluster, values near 0 mean it sits on a boundary, and negative values suggest misassignment. The best k is typically the one with the highest average silhouette score."

**Steps:**

1. Load the iris dataset.
2. Scale the four numeric features.
3. For each value of k from 2 to 10:
   - Run k-means with `set.seed(42)` and `nstart=25`.
   - Compute the average silhouette score using the `silhouette()` function from the `cluster` package and Euclidean distance.
   - Store the result.
4. Plot average silhouette score (y-axis) vs. k (x-axis) as a line plot with points. Highlight the k with the highest score (e.g., with a different point color or a vertical dashed line). Title: `"Average Silhouette Score by Number of Clusters (k)"`. Use `theme_minimal()`.
5. Save to `output/silhouette_plot.png` at 1000x700 pixels, 150 dpi.

---

### 04_dendrogram.R — Hierarchical Clustering Dendrogram

**Purpose:** Perform agglomerative hierarchical clustering on the iris data using Ward's linkage and produce a dendrogram visualization.

**Background comment to include in script:**
> "Hierarchical (agglomerative) clustering starts with each point as its own cluster and repeatedly merges the two most similar clusters until all points belong to one top-level cluster. Ward's linkage merges the pair of clusters that minimizes the increase in total within-cluster variance. The dendrogram shows the full sequence of merges; cutting it at a chosen height yields a flat clustering."

**Steps:**

1. Load the iris dataset.
2. Scale the four numeric features.
3. Compute a Euclidean distance matrix using `dist()`.
4. Run hierarchical clustering using `hclust()` with `method = "ward.D2"`.
5. Visualize the dendrogram using `factoextra::fviz_dend()` with the following settings:
   - Cut the dendrogram into **k=3** clusters (use the `k` argument) so branches are colored by cluster.
   - Set `show_labels = FALSE` (150 points makes individual labels unreadable).
   - Add a title: `"Hierarchical Clustering Dendrogram (Ward's Linkage, k=3)"`.
   - Use `theme_minimal()` styling where possible.
6. Save to `output/dendrogram.png` at 1200x800 pixels, 150 dpi.

---

### 05_gmm.R — Gaussian Mixture Model Clustering

**Purpose:** Fit a Gaussian Mixture Model to the iris data, assign each point to its most probable cluster, and compare the result to the true species labels on a PCA scatter plot.

**Background comment to include in script:**
> "A Gaussian Mixture Model (GMM) takes a probabilistic approach to clustering. Instead of assigning each point to exactly one cluster, it assumes the data were drawn from a mixture of multivariate normal (Gaussian) distributions. The EM (expectation-maximization) algorithm finds the means and covariances of those distributions that best explain the data. Each point receives a probability of belonging to each cluster; the most probable cluster is used for visualization."

**Steps:**

1. Load the iris dataset.
2. Scale the four numeric features.
3. Fit a GMM using `mclust::Mclust()` with `G=3` (force 3 components to match the known number of species). Use `set.seed(42)`.
4. Extract the cluster assignments (the most probable component for each point).
5. Run PCA (same as in `01_kmeans.R`) and construct the same informative axis labels using loadings and variance explained (top 1-2 features per component, same threshold rule).
6. Produce **two side-by-side scatter plots** on the PCA projection:
   - **Left plot:** Points colored by **true species**. Title: `"True Species Labels"`.
   - **Right plot:** Points colored by **GMM cluster assignment**. Title: `"GMM Cluster Assignments (k=3)"`.
   - Same axis labels, `theme_minimal()`, colorblind-friendly palette.
   - Use `patchwork` to combine.
7. Save to `output/gmm_pca_scatter.png` at 1600x800 pixels, 150 dpi.

---

## General Code Style Requirements

- Every script begins with a comment block giving the script number, title, and one-sentence description of its purpose.
- Use `set.seed(42)` wherever randomness is involved.
- Avoid `suppressWarnings()` globally — let warnings surface so the user can learn from them.
- Variable names should be clear and descriptive (e.g., `kmeans_result` not `km`, `pca_loadings` not `ld`).
- The `output/` directory creation line should read: `if (!dir.exists("output")) dir.create("output")`.
- Scripts should print a brief message to the console on completion, e.g.: `cat("Plot saved to output/kmeans_pca_scatter.png\n")`.

---

## Notes for the Coding Agent

- The iris dataset in R is accessed via `data(iris)`. The four numeric columns are `Sepal.Length`, `Sepal.Width`, `Petal.Length`, `Petal.Width`. The species column is `Species` (a factor with levels setosa, versicolor, virginica).
- PCA axis label construction (the loading-based labels) is used in both `01_kmeans.R` and `05_gmm.R`. If desired, this logic can be extracted into a small helper function defined at the top of each script to avoid duplication.
- Do not use `ggbiplot` — use `factoextra::fviz_pca_ind()` or manual `ggplot2` construction from the PCA scores. Manual `ggplot2` construction is preferred for full label control.
- For saving plots, use `ggsave()` with explicit `width`, `height`, and `dpi` arguments. Widths/heights are in pixels divided by dpi (e.g., 1600px / 150dpi = 10.67 inches).