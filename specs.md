# Project Spec: Telco Customer Churn Prediction
> Scaffolding document for a coding agent. Follow each section in order.

---

## 1. Project Overview

Build an R script that loads a telecom customer churn dataset, performs exploratory analysis, trains and compares two predictive models (Logistic Regression and Random Forest), and reports evaluation metrics. The final deliverable is a single `.R` file.

---

## 2. Input

- **File:** `WA_Fn-UseC_-Telco-Customer-Churn.csv` (assumed to be in the working directory)
- **Source:** IBM Telco Customer Churn dataset via Kaggle
- **Format:** CSV with a header row

### Key columns

| Column | Type | Notes |
|---|---|---|
| `customerID` | character | Unique ID — **exclude from all models** |
| `Churn` | character (`"Yes"` / `"No"`) | Target variable |
| `SeniorCitizen` | integer (`0` / `1`) | Must be converted to factor |
| `TotalCharges` | character | Contains blank strings — convert to numeric, drop resulting NAs |
| `tenure` | integer | Months as a customer |
| `Contract` | character | `"Month-to-month"`, `"One year"`, `"Two year"` |
| *(all other columns)* | character | Convert to factor |

---

## 3. Dependencies

Install if not already present:

```r
install.packages(c("tidyverse", "caret", "randomForest"))
```

Load at the top of the script:

```r
library(tidyverse)
library(caret)
library(randomForest)
```

---

## 4. Data Loading & Cleaning

**Steps, in order:**

1. Read the CSV with `read.csv(..., stringsAsFactors = FALSE)`
2. Drop the `customerID` column
3. Convert `TotalCharges` to numeric with `as.numeric()`
4. Drop all rows with `NA` using `drop_na()`
5. Convert all remaining `character` columns to factors using `mutate(across(where(is.character), as.factor))`
6. Re-encode `SeniorCitizen` as a factor: levels `c(0, 1)`, labels `c("No", "Yes")`

**Validation checkpoint:** Print `nrow(df)`, `ncol(df)`, and `table(df$Churn)` to confirm data loaded correctly.

---

## 5. Exploratory Data Analysis

Create **two plots** using `ggplot2` showing how churn rate differs across a feature. Save each plot as a PNG file in the working directory.

### Plot 1 — Contract Type vs. Churn

- **Hypothesis:** Month-to-month customers churn at a higher rate than customers on longer contracts
- **Chart type:** Grouped bar chart (dodge position)
- **X-axis:** `Contract` (the three contract types)
- **Y-axis:** Percentage of customers, formatted as `%`
- **Fill:** `Churn` (two bars per contract type — Yes and No)
- **Colors:** `"No"` → `#4CAF50`, `"Yes"` → `#F44336`
- **Output file:** `plot_contract_churn.png`

**Data prep required:**
```r
df %>%
  group_by(Contract, Churn) %>%
  summarise(n = n(), .groups = "drop") %>%
  group_by(Contract) %>%
  mutate(pct = n / sum(n))
```

### Plot 2 — Tenure vs. Churn

- **Hypothesis:** Customers who churn have shorter tenure
- **Chart type:** Side-by-side boxplot
- **X-axis:** `Churn`
- **Y-axis:** `tenure` (months)
- **Fill:** `Churn`
- **Colors:** same as Plot 1
- **Legend:** hide (redundant with x-axis)
- **Output file:** `plot_tenure_churn.png`

---

## 6. Train / Test Split

- Use `set.seed(42)` for reproducibility
- Use `caret::createDataPartition()` with `p = 0.80` for a **stratified** split (preserves churn class ratio)
- Name the resulting data frames `train_df` and `test_df`
- Print train and test sizes to console

> **Note on validation set:** No separate validation set is needed. Neither model requires iterative hyperparameter tuning that would leak signal from the test set. The 80/20 split is sufficient.

---

## 7. Evaluation Helper Function

Define a reusable function `eval_model(actual, predicted, model_name)` that:

1. Calls `caret::confusionMatrix(predicted, actual, positive = "Yes")`
2. Prints the model name, confusion matrix table, and the following metrics formatted to 4 decimal places:
   - Accuracy (`cm$overall["Accuracy"]`)
   - Precision (`cm$byClass["Pos Pred Value"]`)
   - Recall (`cm$byClass["Sensitivity"]`)
   - F1 Score (`cm$byClass["F1"]`)
3. Returns a named list of all four metrics plus the model name, for use in the comparison summary

---

## 8. Model 1 — Logistic Regression

- **Function:** `glm(Churn ~ ., data = train_df, family = binomial)`
- **Prediction:** Use `predict(..., type = "response")` to get probabilities
- **Threshold:** Convert probabilities ≥ 0.5 to `"Yes"`, else `"No"`
- **Ensure predicted values are a factor** with levels `c("No", "Yes")`
- Call `eval_model()` and store the result as `lr_results`

---

## 9. Model 2 — Random Forest

- **Function:** `randomForest(Churn ~ ., data = train_df, ...)`
- **Parameters:**
  - `ntree = 300`
  - `mtry = floor(sqrt(ncol(train_df) - 1))`
  - `importance = TRUE`
- **Prediction:** `predict(rf_model, newdata = test_df)` (returns factors directly)
- Call `eval_model()` and store the result as `rf_results`

---

## 10. Model Comparison Summary

- Combine `lr_results` and `rf_results` into a single data frame using `bind_rows()`
- Rename columns to: `Model`, `Accuracy`, `Precision`, `Recall`, `F1`
- Round all numeric columns to 4 decimal places
- Print the comparison table to console with a clear header

---

## 11. Feature Importance Plot (Random Forest)

- Extract importance with `importance(rf_model)` and convert to a data frame
- Sort descending by `MeanDecreaseGini`
- Plot the **top 10 features** as a horizontal bar chart using `coord_flip()`
- Bar fill color: `#2196F3`
- Output file: `plot_feature_importance.png`

---

## 12. Output Files

| File | Description |
|---|---|
| `plot_contract_churn.png` | EDA plot 1 |
| `plot_tenure_churn.png` | EDA plot 2 |
| `plot_feature_importance.png` | Random Forest feature importance |

All plots should be saved with `ggsave()`. Recommended dimensions: 7×5 inches for bar charts, 6×5 for the boxplot.

---

## 13. Script Structure

The script should follow this section order, with clear comment headers for each:

```
# 1. Load Libraries
# 2. Load & Clean Data
# 3. Exploratory Analysis
# 4. Train / Test Split
# 5. Evaluation Helper
# 6. Model 1: Logistic Regression
# 7. Model 2: Random Forest
# 8. Model Comparison Summary
# 9. Feature Importance Plot
```

---

## 14. Writeup Summary (inline comments at end of script)

Include a commented block at the bottom of the script summarizing:

- **EDA findings:** What each plot revealed about the relationship between the feature and churn
- **Model results:** Which model performed better and on which metrics
- **Recommendation:** A concrete, actionable suggestion for how the business should use the model (e.g., which customer segment to target, what probability threshold to flag, what retention action to take)