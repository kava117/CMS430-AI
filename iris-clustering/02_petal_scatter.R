# Script 02: Petal Scatter Plot
# Purpose: Visualize whether petal measurements alone can separate the three iris species,
#          comparing true species labels to k-means clusters fit on petal features only.

if (!require("ggplot2")) install.packages("ggplot2", repos = "https://cloud.r-project.org")
if (!require("patchwork")) install.packages("patchwork", repos = "https://cloud.r-project.org")
library(ggplot2)
library(patchwork)

if (!dir.exists("output")) dir.create("output")

data(iris)
petal_data <- iris[, c("Petal.Length", "Petal.Width")]
petal_scaled <- scale(petal_data)

set.seed(42)
kmeans_petal <- kmeans(petal_scaled, centers = 3, nstart = 25)

# Remap cluster numbers so they align with species factor order
# (setosa=1, versicolor=2, virginica=3), ensuring colors match across panels.
cluster_species_table <- table(kmeans_petal$cluster, iris$Species)
dominant_species_idx <- apply(cluster_species_table, 1, which.max)
iris$Cluster <- factor(dominant_species_idx[as.character(kmeans_petal$cluster)])

plot_species <- ggplot(iris, aes(x = Petal.Length, y = Petal.Width, color = Species)) +
  geom_point(size = 2.5, alpha = 0.8) +
  scale_color_brewer(palette = "Set2") +
  labs(
    title = "True Species Labels",
    subtitle = "Can petal measurements alone separate the three species?",
    x = "Petal Length",
    y = "Petal Width"
  ) +
  theme_minimal()

plot_clusters <- ggplot(iris, aes(x = Petal.Length, y = Petal.Width, color = Cluster)) +
  geom_point(size = 2.5, alpha = 0.8) +
  scale_color_brewer(palette = "Set2", labels = c("Cluster 1", "Cluster 2", "Cluster 3")) +
  labs(
    title = "K-Means Clusters (k=3, petal features only)",
    subtitle = " ",
    x = "Petal Length",
    y = "Petal Width",
    color = "Cluster"
  ) +
  theme_minimal()

combined_plot <- plot_species + plot_clusters

ggsave("output/petal_scatter.png", combined_plot,
       width = 1600 / 150, height = 800 / 150, dpi = 150)

cat("Plot saved to output/petal_scatter.png\n")
