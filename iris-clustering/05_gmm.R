# Script 05: Gaussian Mixture Model Clustering
# Purpose: Fit a GMM to the iris data and compare cluster assignments to true species labels on a PCA scatter plot.

if (!require("ggplot2")) install.packages("ggplot2", repos = "https://cloud.r-project.org")
if (!require("patchwork")) install.packages("patchwork", repos = "https://cloud.r-project.org")
if (!require("mclust")) install.packages("mclust", repos = "https://cloud.r-project.org")
library(ggplot2)
library(patchwork)
library(mclust)

if (!dir.exists("output")) dir.create("output")

# A Gaussian Mixture Model (GMM) takes a probabilistic approach to clustering.
# Instead of assigning each point to exactly one cluster, it assumes the data were
# drawn from a mixture of multivariate normal (Gaussian) distributions. The EM
# (expectation-maximization) algorithm finds the means and covariances of those
# distributions that best explain the data. Each point receives a probability of
# belonging to each cluster; the most probable cluster is used for visualization.

# Helper: construct an informative PCA axis label from loadings (top 1-2 features, capped at 2)
make_pca_label <- function(pca_result, pc_index, variance_pct) {
  loadings <- abs(pca_result$rotation[, pc_index])
  feature_names <- rownames(pca_result$rotation)
  sorted_idx <- order(loadings, decreasing = TRUE)
  top_val <- loadings[sorted_idx[1]]
  included <- feature_names[sorted_idx[1]]
  if (length(sorted_idx) > 1 && loadings[sorted_idx[2]] >= 0.70 * top_val) {
    included <- c(included, feature_names[sorted_idx[2]])
  }
  pretty <- gsub("\\.", " ", tolower(included))
  sprintf("PC%d (%.1f%% variance) \u2014 driven by: %s",
          pc_index, variance_pct[pc_index], paste(pretty, collapse = ", "))
}

data(iris)
iris_scaled <- scale(iris[, 1:4])

set.seed(42)
gmm_result <- Mclust(iris_scaled, G = 3)
gmm_clusters <- factor(gmm_result$classification)

pca_result <- prcomp(iris_scaled, center = FALSE, scale. = FALSE)
variance_pct <- pca_result$sdev^2 / sum(pca_result$sdev^2) * 100

x_label <- make_pca_label(pca_result, 1, variance_pct)
y_label <- make_pca_label(pca_result, 2, variance_pct)

pca_df <- data.frame(
  PC1 = pca_result$x[, 1],
  PC2 = pca_result$x[, 2],
  Species = iris$Species,
  GMMCluster = gmm_clusters
)

plot_species <- ggplot(pca_df, aes(x = PC1, y = PC2, color = Species)) +
  geom_point(size = 2.5, alpha = 0.8) +
  scale_color_brewer(palette = "Set2") +
  labs(title = "True Species Labels", x = x_label, y = y_label) +
  theme_minimal()

plot_gmm <- ggplot(pca_df, aes(x = PC1, y = PC2, color = GMMCluster)) +
  geom_point(size = 2.5, alpha = 0.8) +
  scale_color_brewer(palette = "Set2", labels = c("Cluster 1", "Cluster 2", "Cluster 3")) +
  labs(title = "GMM Cluster Assignments (k=3)", x = x_label, y = y_label, color = "Cluster") +
  theme_minimal()

combined_plot <- plot_species + plot_gmm

ggsave("output/gmm_pca_scatter.png", combined_plot,
       width = 1600 / 150, height = 800 / 150, dpi = 150)

cat("Plot saved to output/gmm_pca_scatter.png\n")
