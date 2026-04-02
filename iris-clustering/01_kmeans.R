# Script 01: K-Means Clustering on PCA Projection
# Purpose: Perform PCA on the iris dataset, run k-means (k=3), and visualize true species labels vs. cluster assignments side by side.

if (!require("ggplot2")) install.packages("ggplot2", repos = "https://cloud.r-project.org")
if (!require("patchwork")) install.packages("patchwork", repos = "https://cloud.r-project.org")
library(ggplot2)
library(patchwork)

if (!dir.exists("output")) dir.create("output")

# PCA (Principal Component Analysis) reduces the 4 original measurements into new
# composite axes that capture the most variation in the data. PC1 captures the most
# variation, PC2 the second most. The axis labels below show which original features
# drive each component.

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

pca_result <- prcomp(iris_scaled, center = FALSE, scale. = FALSE)
variance_pct <- pca_result$sdev^2 / sum(pca_result$sdev^2) * 100

x_label <- make_pca_label(pca_result, 1, variance_pct)
y_label <- make_pca_label(pca_result, 2, variance_pct)

pca_df <- data.frame(
  PC1 = pca_result$x[, 1],
  PC2 = pca_result$x[, 2],
  Species = iris$Species
)

set.seed(42)
kmeans_result <- kmeans(iris_scaled, centers = 3, nstart = 25)
pca_df$Cluster <- factor(kmeans_result$cluster)

plot_species <- ggplot(pca_df, aes(x = PC1, y = PC2, color = Species)) +
  geom_point(size = 2.5, alpha = 0.8) +
  scale_color_brewer(palette = "Set2") +
  labs(title = "True Species Labels", x = x_label, y = y_label) +
  theme_minimal()

plot_clusters <- ggplot(pca_df, aes(x = PC1, y = PC2, color = Cluster)) +
  geom_point(size = 2.5, alpha = 0.8) +
  scale_color_brewer(palette = "Set2", labels = c("Cluster 1", "Cluster 2", "Cluster 3")) +
  labs(title = "K-Means Clusters (k=3)", x = x_label, y = y_label, color = "Cluster") +
  theme_minimal()

combined_plot <- plot_species + plot_clusters

ggsave("output/kmeans_pca_scatter.png", combined_plot,
       width = 1600 / 150, height = 800 / 150, dpi = 150)

cat("Plot saved to output/kmeans_pca_scatter.png\n")
