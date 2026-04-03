# 1. Load Libraries
.libPaths(c("~/R/library", .libPaths()))

library(ggplot2)
library(dplyr)
library(tidyr)
library(readr)
library(tibble)
library(scales)
library(caret)
library(randomForest)

# 2. Load & Clean Data
df_raw <- read.csv("WA_Fn-UseC_-Telco-Customer-Churn.csv", stringsAsFactors = FALSE)

df <- df_raw %>%
  select(-customerID) %>%
  mutate(TotalCharges = as.numeric(TotalCharges)) %>%
  drop_na() %>%
  mutate(across(where(is.character), as.factor)) %>%
  mutate(SeniorCitizen = factor(SeniorCitizen, levels = c(0, 1), labels = c("No", "Yes")))

# Validation checkpoint
cat("Rows:", nrow(df), "\n")
cat("Cols:", ncol(df), "\n")
print(table(df$Churn))

# 3. Exploratory Analysis

## Plot 1 — Contract Type vs. Churn
contract_data <- df %>%
  group_by(Contract, Churn) %>%
  summarise(n = n(), .groups = "drop") %>%
  group_by(Contract) %>%
  mutate(pct = n / sum(n))

p1 <- ggplot(contract_data, aes(x = Contract, y = pct, fill = Churn)) +
  geom_col(position = "dodge") +
  scale_y_continuous(labels = percent_format()) +
  scale_fill_manual(values = c("No" = "#4CAF50", "Yes" = "#F44336")) +
  labs(title = "Churn Rate by Contract Type",
       x = "Contract", y = "Percentage of Customers") +
  theme_minimal()

ggsave("plot_contract_churn.png", plot = p1, width = 7, height = 5)

## Plot 2 — Tenure vs. Churn
p2 <- ggplot(df, aes(x = Churn, y = tenure, fill = Churn)) +
  geom_boxplot() +
  scale_fill_manual(values = c("No" = "#4CAF50", "Yes" = "#F44336")) +
  labs(title = "Tenure Distribution by Churn Status",
       x = "Churn", y = "Tenure (Months)") +
  theme_minimal() +
  theme(legend.position = "none")

ggsave("plot_tenure_churn.png", plot = p2, width = 6, height = 5)

# 4. Train / Test Split
set.seed(42)
train_idx <- createDataPartition(df$Churn, p = 0.80, list = FALSE)
train_df  <- df[ train_idx, ]
test_df   <- df[-train_idx, ]

cat("Train size:", nrow(train_df), "\n")
cat("Test size: ", nrow(test_df),  "\n")

# 5. Evaluation Helper
eval_model <- function(actual, predicted, model_name) {
  cm <- confusionMatrix(predicted, actual, positive = "Yes")

  accuracy  <- cm$overall["Accuracy"]
  precision <- cm$byClass["Pos Pred Value"]
  recall    <- cm$byClass["Sensitivity"]
  f1        <- cm$byClass["F1"]

  cat("\n===", model_name, "===\n")
  print(cm$table)
  cat(sprintf("Accuracy:  %.4f\n", accuracy))
  cat(sprintf("Precision: %.4f\n", precision))
  cat(sprintf("Recall:    %.4f\n", recall))
  cat(sprintf("F1 Score:  %.4f\n", f1))

  list(
    Model     = model_name,
    Accuracy  = round(accuracy,  4),
    Precision = round(precision, 4),
    Recall    = round(recall,    4),
    F1        = round(f1,        4),
    CM        = cm$table
  )
}

plot_confusion_matrix <- function(result) {
  cm_df <- as.data.frame(result$CM)
  safe_name <- gsub(" ", "_", tolower(result$Model))

  p <- ggplot(cm_df, aes(x = Reference, y = Prediction, fill = Freq)) +
    geom_tile(color = "white") +
    geom_text(aes(label = Freq), size = 6, fontface = "bold") +
    scale_fill_gradient(low = "#E3F2FD", high = "#1565C0") +
    labs(title = paste("Confusion Matrix —", result$Model),
         x = "Actual", y = "Predicted", fill = "Count") +
    theme_minimal()

  ggsave(paste0("plot_cm_", safe_name, ".png"), plot = p, width = 5, height = 4)
}

# 6. Model 1: Logistic Regression
lr_model <- glm(Churn ~ ., data = train_df, family = binomial)

lr_probs <- predict(lr_model, newdata = test_df, type = "response")
lr_preds <- factor(ifelse(lr_probs >= 0.5, "Yes", "No"), levels = c("No", "Yes"))

lr_results <- eval_model(test_df$Churn, lr_preds, "Logistic Regression")
plot_confusion_matrix(lr_results)

# 7. Model 2: Random Forest
set.seed(42)
rf_model <- randomForest(
  Churn ~ .,
  data       = train_df,
  ntree      = 300,
  mtry       = floor(sqrt(ncol(train_df) - 1)),
  importance = TRUE
)

rf_preds   <- predict(rf_model, newdata = test_df)
rf_results <- eval_model(test_df$Churn, rf_preds, "Random Forest")
plot_confusion_matrix(rf_results)

# 8. Model Comparison Summary
to_row <- function(r) as_tibble(r[c("Model","Accuracy","Precision","Recall","F1")])
comparison <- bind_rows(to_row(lr_results), to_row(rf_results)) %>%
  mutate(across(where(is.numeric), ~ round(.x, 4)))

cat("\n===== Model Comparison =====\n")
print(comparison)

# 9. Feature Importance Plot
importance_df <- as.data.frame(importance(rf_model)) %>%
  rownames_to_column("Feature") %>%
  arrange(desc(MeanDecreaseGini)) %>%
  slice_head(n = 10)

p3 <- ggplot(importance_df,
             aes(x = reorder(Feature, MeanDecreaseGini), y = MeanDecreaseGini)) +
  geom_col(fill = "#2196F3") +
  coord_flip() +
  labs(title = "Top 10 Features by Importance (Random Forest)",
       x = "Feature", y = "Mean Decrease Gini") +
  theme_minimal()

ggsave("plot_feature_importance.png", plot = p3, width = 7, height = 5)

# 10. Model Comparison Plot
comparison_long <- comparison %>%
  pivot_longer(cols = c(Accuracy, Precision, Recall, F1),
               names_to = "Metric", values_to = "Value")

p4 <- ggplot(comparison_long, aes(x = Metric, y = Value, fill = Model)) +
  geom_col(position = "dodge") +
  scale_y_continuous(limits = c(0, 1), labels = percent_format()) +
  scale_fill_manual(values = c("Logistic Regression" = "#2196F3", "Random Forest" = "#FF9800")) +
  labs(title = "Model Comparison: Logistic Regression vs. Random Forest",
       x = "Metric", y = "Score") +
  theme_minimal()

ggsave("plot_model_comparison.png", plot = p4, width = 7, height = 5)

# =============================================================================
# WRITEUP SUMMARY
# =============================================================================
#
# EDA Findings:
#   Plot 1 (Contract vs. Churn): Month-to-month customers churn at a far higher
#   rate (~43%) than one-year (~11%) or two-year (~3%) contract holders. Contract
#   type is the single strongest categorical predictor visible in the raw data.
#
#   Plot 2 (Tenure vs. Churn): Customers who churn have a noticeably shorter
#   median tenure (~10 months) compared to retained customers (~38 months).
#   New customers are at the highest risk; reaching the ~2-year mark dramatically
#   reduces churn probability.
#
# Model Results:
#   Logistic Regression achieves ~80% accuracy with higher F1 (0.585) than
#   Random Forest (0.532) on this dataset, suggesting it generalises better
#   to the minority "Yes" class here. Random Forest matches on precision but
#   yields lower recall, meaning it misses more actual churners.
#
# Recommendation:
#   Deploy the Logistic Regression model for interpretability and performance.
#   Flag any customer with a predicted churn probability >= 0.40 (lower than
#   0.50 to increase recall for at-risk detection). Prioritise outreach to
#   month-to-month customers in their first 12 months of tenure — this segment
#   has the highest base-rate churn and the most to gain from early retention
#   interventions (e.g., a targeted offer to switch to a one-year contract).
# =============================================================================
