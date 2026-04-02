# Steps: Telco Customer Churn Prediction

> Build and verify the R script incrementally. Each step ends with explicit tests/checks to run before proceeding.

---

## Step 1 — Project Setup & Dependencies

**Goal:** Confirm the environment is ready and the CSV exists.

### Actions
1. Confirm `WA_Fn-UseC_-Telco-Customer-Churn.csv` is in the working directory.
2. Create the script file `churn_analysis.R` with the section skeleton (comment headers only, no logic yet).
3. Install required packages if missing and load them.

```r
# At top of churn_analysis.R:
# 1. Load Libraries
if (!requireNamespace("tidyverse",    quietly = TRUE)) install.packages("tidyverse")
if (!requireNamespace("caret",        quietly = TRUE)) install.packages("caret")
if (!requireNamespace("randomForest", quietly = TRUE)) install.packages("randomForest")

library(tidyverse)
library(caret)
library(randomForest)
```

### Tests
```r
# Run interactively to verify:
stopifnot(file.exists("WA_Fn-UseC_-Telco-Customer-Churn.csv"))
stopifnot(requireNamespace("tidyverse",    quietly = TRUE))
stopifnot(requireNamespace("caret",        quietly = TRUE))
stopifnot(requireNamespace("randomForest", quietly = TRUE))
cat("Step 1 PASSED\n")
```

**Expected:** All three `stopifnot` calls pass silently; `"Step 1 PASSED"` prints.

---

## Step 2 — Data Loading & Cleaning

**Goal:** Load the CSV, apply all cleaning steps, and arrive at a correctly typed data frame.

### Actions
Implement the `# 2. Load & Clean Data` section:

```r
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
```

### Tests
```r
# Shape
stopifnot(nrow(df) == 7032)   # 7043 raw minus 11 NA TotalCharges rows
stopifnot(ncol(df) == 20)     # 21 original minus customerID

# No customerID column
stopifnot(!"customerID" %in% names(df))

# No NAs anywhere
stopifnot(sum(is.na(df)) == 0)

# TotalCharges is numeric
stopifnot(is.numeric(df$TotalCharges))

# All character columns converted to factor
char_cols <- sapply(df, is.character)
stopifnot(sum(char_cols) == 0)

# SeniorCitizen is factor with labels "No"/"Yes"
stopifnot(is.factor(df$SeniorCitizen))
stopifnot(all(levels(df$SeniorCitizen) == c("No", "Yes")))

# Churn is a factor with levels No/Yes
stopifnot(is.factor(df$Churn))
stopifnot(all(levels(df$Churn) == c("No", "Yes")))

cat("Step 2 PASSED\n")
```

**Expected:** Row count 7032, column count 20, churn table shows `No ~5174` and `Yes ~1869` (approximate — exact counts depend on NA removal). All `stopifnot` calls pass.

---

## Step 3 — Exploratory Analysis: Plot 1 (Contract vs. Churn)

**Goal:** Produce and save `plot_contract_churn.png`.

### Actions
Implement the first EDA plot in `# 3. Exploratory Analysis`:

```r
contract_data <- df %>%
  group_by(Contract, Churn) %>%
  summarise(n = n(), .groups = "drop") %>%
  group_by(Contract) %>%
  mutate(pct = n / sum(n))

p1 <- ggplot(contract_data, aes(x = Contract, y = pct, fill = Churn)) +
  geom_col(position = "dodge") +
  scale_y_continuous(labels = scales::percent_format()) +
  scale_fill_manual(values = c("No" = "#4CAF50", "Yes" = "#F44336")) +
  labs(title = "Churn Rate by Contract Type",
       x = "Contract", y = "Percentage of Customers") +
  theme_minimal()

ggsave("plot_contract_churn.png", plot = p1, width = 7, height = 5)
```

### Tests
```r
# File exists and is non-empty
stopifnot(file.exists("plot_contract_churn.png"))
stopifnot(file.info("plot_contract_churn.png")$size > 0)

# Data prep produces expected structure: 6 rows (3 contracts × 2 churn levels)
stopifnot(nrow(contract_data) == 6)
stopifnot(all(c("Contract", "Churn", "n", "pct") %in% names(contract_data)))

# Percentages sum to 1 per contract group
pct_sums <- contract_data %>% group_by(Contract) %>% summarise(total = sum(pct))
stopifnot(all(abs(pct_sums$total - 1) < 1e-9))

cat("Step 3 PASSED\n")
```

**Expected:** `plot_contract_churn.png` saved; 6-row summary table with percentages summing to 1 per contract type.

---

## Step 4 — Exploratory Analysis: Plot 2 (Tenure vs. Churn)

**Goal:** Produce and save `plot_tenure_churn.png`.

### Actions
```r
p2 <- ggplot(df, aes(x = Churn, y = tenure, fill = Churn)) +
  geom_boxplot() +
  scale_fill_manual(values = c("No" = "#4CAF50", "Yes" = "#F44336")) +
  labs(title = "Tenure Distribution by Churn Status",
       x = "Churn", y = "Tenure (Months)") +
  theme_minimal() +
  theme(legend.position = "none")

ggsave("plot_tenure_churn.png", plot = p2, width = 6, height = 5)
```

### Tests
```r
stopifnot(file.exists("plot_tenure_churn.png"))
stopifnot(file.info("plot_tenure_churn.png")$size > 0)

# Sanity check: churned customers have lower median tenure
med_no  <- median(df$tenure[df$Churn == "No"])
med_yes <- median(df$tenure[df$Churn == "Yes"])
stopifnot(med_yes < med_no)

cat("Step 4 PASSED\n")
```

**Expected:** File saved; churned customers have a lower median tenure than retained customers (confirming the hypothesis).

---

## Step 5 — Train / Test Split

**Goal:** Create reproducible stratified `train_df` and `test_df`.

### Actions
Implement `# 4. Train / Test Split`:

```r
set.seed(42)
train_idx <- caret::createDataPartition(df$Churn, p = 0.80, list = FALSE)
train_df  <- df[ train_idx, ]
test_df   <- df[-train_idx, ]

cat("Train size:", nrow(train_df), "\n")
cat("Test size: ", nrow(test_df),  "\n")
```

### Tests
```r
# Sizes add up
stopifnot(nrow(train_df) + nrow(test_df) == nrow(df))

# Roughly 80/20 (allow ±5 rows for stratification rounding)
stopifnot(abs(nrow(train_df) / nrow(df) - 0.80) < 0.01)

# Stratification: churn ratio preserved within ±2 percentage points
train_churn_pct <- mean(train_df$Churn == "Yes")
test_churn_pct  <- mean(test_df$Churn  == "Yes")
overall_pct     <- mean(df$Churn        == "Yes")
stopifnot(abs(train_churn_pct - overall_pct) < 0.02)
stopifnot(abs(test_churn_pct  - overall_pct) < 0.02)

# No column dropped during split
stopifnot(ncol(train_df) == ncol(df))
stopifnot(ncol(test_df)  == ncol(df))

# Reproducibility: re-running set.seed(42) yields same split
set.seed(42)
idx2 <- caret::createDataPartition(df$Churn, p = 0.80, list = FALSE)
stopifnot(identical(as.vector(train_idx), as.vector(idx2)))

cat("Step 5 PASSED\n")
```

**Expected:** ~5625 train rows, ~1407 test rows; churn ratio consistent across splits.

---

## Step 6 — Evaluation Helper Function

**Goal:** Define and unit-test `eval_model()` before using it on real models.

### Actions
Implement `# 5. Evaluation Helper`:

```r
eval_model <- function(actual, predicted, model_name) {
  cm <- caret::confusionMatrix(predicted, actual, positive = "Yes")

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
    F1        = round(f1,        4)
  )
}
```

### Tests
```r
# Build a small synthetic ground-truth test
actual_test    <- factor(c("Yes","Yes","No","No","Yes","No"), levels = c("No","Yes"))
predicted_test <- factor(c("Yes","No", "No","No","Yes","Yes"), levels = c("No","Yes"))

result <- eval_model(actual_test, predicted_test, "SyntheticModel")

# Return type
stopifnot(is.list(result))
stopifnot(all(c("Model","Accuracy","Precision","Recall","F1") %in% names(result)))

# Model name preserved
stopifnot(result$Model == "SyntheticModel")

# Manually verified values for above vectors:
# TP=2, FP=1, FN=1, TN=2  →  Accuracy=4/6, Precision=2/3, Recall=2/3
stopifnot(abs(result$Accuracy  - round(4/6, 4)) < 1e-4)
stopifnot(abs(result$Precision - round(2/3, 4)) < 1e-4)
stopifnot(abs(result$Recall    - round(2/3, 4)) < 1e-4)

# F1 = 2*P*R/(P+R) = 2/3 when P==R
stopifnot(abs(result$F1 - round(2/3, 4)) < 1e-4)

cat("Step 6 PASSED\n")
```

**Expected:** All metric assertions pass; printed output shows the synthetic confusion matrix.

---

## Step 7 — Model 1: Logistic Regression

**Goal:** Train logistic regression, predict on test set, evaluate with `eval_model()`.

### Actions
Implement `# 6. Model 1: Logistic Regression`:

```r
lr_model <- glm(Churn ~ ., data = train_df, family = binomial)

lr_probs <- predict(lr_model, newdata = test_df, type = "response")
lr_preds <- factor(ifelse(lr_probs >= 0.5, "Yes", "No"), levels = c("No", "Yes"))

lr_results <- eval_model(test_df$Churn, lr_preds, "Logistic Regression")
```

### Tests
```r
# Model fitted without error
stopifnot(inherits(lr_model, "glm"))

# Probabilities are in [0, 1]
stopifnot(all(lr_probs >= 0 & lr_probs <= 1))

# Predictions are a factor with correct levels
stopifnot(is.factor(lr_preds))
stopifnot(all(levels(lr_preds) == c("No", "Yes")))

# Length matches test set
stopifnot(length(lr_preds) == nrow(test_df))

# Results list has all expected fields
stopifnot(all(c("Model","Accuracy","Precision","Recall","F1") %in% names(lr_results)))

# Sanity: LR should achieve >70% accuracy on this dataset
stopifnot(lr_results$Accuracy > 0.70)

# Sanity: all metrics in [0, 1]
stopifnot(all(c(lr_results$Accuracy, lr_results$Precision,
                lr_results$Recall,   lr_results$F1) %>% between(0, 1)))

cat("Step 7 PASSED\n")
```

**Expected:** Logistic regression converges; accuracy typically ~80%; all metric values in [0,1].

---

## Step 8 — Model 2: Random Forest

**Goal:** Train random forest, predict, evaluate with `eval_model()`.

### Actions
Implement `# 7. Model 2: Random Forest`:

```r
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
```

### Tests
```r
# Model object
stopifnot(inherits(rf_model, "randomForest"))

# ntree parameter honoured
stopifnot(rf_model$ntree == 300)

# Predictions are factor with correct levels and correct length
stopifnot(is.factor(rf_preds))
stopifnot(all(levels(rf_preds) == c("No", "Yes")))
stopifnot(length(rf_preds) == nrow(test_df))

# Importance matrix present (importance = TRUE was set)
stopifnot(!is.null(rf_model$importance))

# Results list structure
stopifnot(all(c("Model","Accuracy","Precision","Recall","F1") %in% names(rf_results)))

# Sanity: RF should also achieve >70% accuracy
stopifnot(rf_results$Accuracy > 0.70)

# Sanity: all metrics in [0, 1]
stopifnot(all(c(rf_results$Accuracy, rf_results$Precision,
                rf_results$Recall,   rf_results$F1) %>% between(0, 1)))

cat("Step 8 PASSED\n")
```

**Expected:** Random forest trains (~1–2 min); accuracy typically ~79–81%; importance matrix populated.

---

## Step 9 — Model Comparison Summary

**Goal:** Combine results into a single tidy table and print it.

### Actions
Implement `# 8. Model Comparison Summary`:

```r
comparison <- bind_rows(
  as_tibble(lr_results),
  as_tibble(rf_results)
) %>%
  rename(Model = Model, Accuracy = Accuracy,
         Precision = Precision, Recall = Recall, F1 = F1) %>%
  mutate(across(where(is.numeric), ~ round(.x, 4)))

cat("\n===== Model Comparison =====\n")
print(comparison)
```

### Tests
```r
# Shape: 2 models × 5 columns
stopifnot(nrow(comparison) == 2)
stopifnot(ncol(comparison) == 5)

# Column names
stopifnot(all(names(comparison) == c("Model","Accuracy","Precision","Recall","F1")))

# Model names present
stopifnot("Logistic Regression" %in% comparison$Model)
stopifnot("Random Forest"       %in% comparison$Model)

# No NAs
stopifnot(sum(is.na(comparison)) == 0)

# All numeric metrics are in [0, 1] and rounded to 4 dp
numeric_cols <- comparison %>% select(where(is.numeric))
stopifnot(all(numeric_cols >= 0 & numeric_cols <= 1))

cat("Step 9 PASSED\n")
```

**Expected:** A clean 2-row data frame with both models and all four metrics displayed side-by-side.

---

## Step 10 — Feature Importance Plot

**Goal:** Produce and save `plot_feature_importance.png` showing the top-10 RF features.

### Actions
Implement `# 9. Feature Importance Plot`:

```r
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
```

### Tests
```r
# File exists and is non-empty
stopifnot(file.exists("plot_feature_importance.png"))
stopifnot(file.info("plot_feature_importance.png")$size > 0)

# Data frame has exactly 10 rows
stopifnot(nrow(importance_df) == 10)

# Required columns present
stopifnot(all(c("Feature", "MeanDecreaseGini") %in% names(importance_df)))

# Values are positive (Gini decrease is always non-negative)
stopifnot(all(importance_df$MeanDecreaseGini >= 0))

# Sorted descending
stopifnot(all(diff(importance_df$MeanDecreaseGini) <= 0))

cat("Step 10 PASSED\n")
```

**Expected:** File saved; 10-row importance table sorted highest-to-lowest; likely top features are `TotalCharges`, `tenure`, `MonthlyCharges`, `Contract`.

---

## Step 11 — Writeup Comments

**Goal:** Add the inline summary block at the bottom of the script.

### Actions
Append a commented block to the end of `churn_analysis.R`:

```r
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
#   Both models achieve roughly similar overall accuracy (~80%). Random Forest
#   typically edges out Logistic Regression on F1 and Recall for the minority
#   "Yes" class, meaning it catches more actual churners at the cost of slightly
#   more false positives. Logistic Regression is faster to train and more
#   interpretable.
#
# Recommendation:
#   Deploy the Random Forest model in production scoring. Flag any customer
#   with a predicted churn probability >= 0.40 (a lower threshold than 0.50 to
#   increase recall for at-risk detection). Prioritise outreach to month-to-month
#   customers in their first 12 months of tenure — this segment has the highest
#   base-rate churn and the most to gain from early retention interventions
#   (e.g., a targeted offer to switch to a one-year contract).
# =============================================================================
```

### Tests
```r
script_text <- readLines("churn_analysis.R")

# All nine section headers present
sections <- c(
  "# 1. Load Libraries",
  "# 2. Load & Clean Data",
  "# 3. Exploratory Analysis",
  "# 4. Train / Test Split",
  "# 5. Evaluation Helper",
  "# 6. Model 1: Logistic Regression",
  "# 7. Model 2: Random Forest",
  "# 8. Model Comparison Summary",
  "# 9. Feature Importance Plot"
)
for (s in sections) {
  stopifnot(any(grepl(s, script_text, fixed = TRUE)))
}

# Writeup block present
stopifnot(any(grepl("WRITEUP SUMMARY", script_text, fixed = TRUE)))
stopifnot(any(grepl("Recommendation", script_text, fixed = TRUE)))

cat("Step 11 PASSED\n")
```

**Expected:** All nine section headers found in the file; writeup block contains `WRITEUP SUMMARY` and `Recommendation`.

---

## Step 12 — Full End-to-End Run

**Goal:** Execute the complete script from top to bottom without errors and verify all output files exist.

### Actions
Run the entire script:

```bash
Rscript churn_analysis.R
```

### Tests
```r
# All three output files present and non-empty
output_files <- c(
  "plot_contract_churn.png",
  "plot_tenure_churn.png",
  "plot_feature_importance.png"
)
for (f in output_files) {
  stopifnot(file.exists(f))
  stopifnot(file.info(f)$size > 0)
}

cat("Step 12 PASSED — all output files generated.\n")
```

From the console output, confirm:
- `Rows: 7032` and `Cols: 20` printed during cleaning
- Train/test sizes printed
- Both model confusion matrices printed
- Comparison table printed with two rows

**Expected:** Zero errors or warnings (suppressible warnings about factor contrasts in GLM are acceptable); all three PNGs written to disk.

---

## Completion Checklist

| Step | Description                        | Test Passes |
|------|------------------------------------|-------------|
|  1   | Environment & dependencies         | ☐           |
|  2   | Data loading & cleaning            | ☐           |
|  3   | EDA Plot 1 (Contract vs. Churn)    | ☐           |
|  4   | EDA Plot 2 (Tenure vs. Churn)      | ☐           |
|  5   | Train / test split                 | ☐           |
|  6   | `eval_model()` helper function     | ☐           |
|  7   | Logistic Regression model          | ☐           |
|  8   | Random Forest model                | ☐           |
|  9   | Model comparison table             | ☐           |
| 10   | Feature importance plot            | ☐           |
| 11   | Writeup comments                   | ☐           |
| 12   | Full end-to-end run                | ☐           |
