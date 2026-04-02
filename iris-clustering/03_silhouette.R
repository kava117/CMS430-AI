# Script 03: Silhouette Plot
# Purpose: Compute and plot average silhouette scores for k=2 through k=10 to identify the optimal number of clusters.

if (!require("ggplot2")) install.packages("ggplot2", repos = "https://cloud.r-project.org")
if (!require("cluster")) install.packages("cluster", repos = "https://cloud.r-project.org")
library(ggplot2)
library(cluster)

if (!dir.exists("output")) dir.create("output")

# The silhouette score measures how similar a point is to its own cluster compared
# to other clusters. Scores range from -1 to 1: values near 1 mean the point is
# well-matched to its cluster, values near 0 mean it sits on a boundary, and
# negative values suggest misassignment. The best k is typically the one with the
# highest average silhouette score.

data(iris)
iris_scaled <- scale(iris[, 1:4])

avg_silhouette_scores <- numeric(9)

for (k in 2:10) {
  set.seed(42)
  kmeans_result <- kmeans(iris_scaled, centers = k, nstart = 25)
  sil <- silhouette(kmeans_result$cluster, dist(iris_scaled))
  avg_silhouette_scores[k - 1] <- mean(sil[, 3])
}

sil_df <- data.frame(
  k = 2:10,
  avg_sil = avg_silhouette_scores
)

best_k <- sil_df$k[which.max(sil_df$avg_sil)]

silhouette_plot <- ggplot(sil_df, aes(x = k, y = avg_sil)) +
  geom_line(color = "steelblue") +
  geom_point(aes(color = (k == best_k)), size = 3) +
  scale_color_manual(values = c("FALSE" = "steelblue", "TRUE" = "red"),
                     guide = "none") +
  geom_vline(xintercept = best_k, linetype = "dashed", color = "red", alpha = 0.6) +
  scale_x_continuous(breaks = 2:10) +
  labs(
    title = "Average Silhouette Score by Number of Clusters (k)",
    x = "Number of Clusters (k)",
    y = "Average Silhouette Score"
  ) +
  theme_minimal()

ggsave("output/silhouette_plot.png", silhouette_plot,
       width = 1000 / 150, height = 700 / 150, dpi = 150)

cat("Plot saved to output/silhouette_plot.png\n")
