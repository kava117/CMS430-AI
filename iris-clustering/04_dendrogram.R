# Script 04: Hierarchical Clustering Dendrogram
# Purpose: Perform agglomerative hierarchical clustering using Ward's linkage and visualize the result as a dendrogram.

if (!require("factoextra")) install.packages("factoextra", repos = "https://cloud.r-project.org")
if (!require("cluster")) install.packages("cluster", repos = "https://cloud.r-project.org")
library(factoextra)
library(cluster)

if (!dir.exists("output")) dir.create("output")

# Hierarchical (agglomerative) clustering starts with each point as its own cluster
# and repeatedly merges the two most similar clusters until all points belong to one
# top-level cluster. Ward's linkage merges the pair of clusters that minimizes the
# increase in total within-cluster variance. The dendrogram shows the full sequence
# of merges; cutting it at a chosen height yields a flat clustering.

data(iris)
iris_scaled <- scale(iris[, 1:4])

dist_matrix <- dist(iris_scaled, method = "euclidean")
hclust_result <- hclust(dist_matrix, method = "ward.D2")

dendrogram_plot <- fviz_dend(hclust_result,
                             k = 3,
                             show_labels = FALSE,
                             main = "Hierarchical Clustering Dendrogram (Ward's Linkage, k=3)",
                             ggtheme = theme_minimal())

# fviz_dend maps linewidth from a data column (hardcoded to 3.5).
# Override by removing the mapping and setting a fixed linewidth instead.
dendrogram_plot$layers[[1]]$mapping$linewidth <- NULL
dendrogram_plot$layers[[1]]$aes_params$linewidth <- 0.3

ggsave("output/dendrogram.png", dendrogram_plot,
       width = 1200 / 150, height = 800 / 150, dpi = 150)

cat("Plot saved to output/dendrogram.png\n")
