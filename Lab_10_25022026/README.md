# Lab 10 — K-Means & K-Medians Clustering

**Date:** February 25, 2026  
**Dataset:** `Mall_Customers.csv` (200 records, 5 features)

---

## Objective

Learn **unsupervised learning** through clustering. Apply K-Means clustering to group customers based on purchasing patterns, visualize the clusters, and analyze customer segments.

---

## Dataset Overview

| Column | Description | Type |
|---|---|---|
| `CustomerID` | Unique customer identifier | Categorical |
| `Genre` | Gender (Male / Female) | Categorical |
| `Age` | Customer age | Numeric |
| `Annual Income (k$)` | Annual income in thousands of dollars (15–137) | Numeric |
| `Spending Score (1-100)` | Mall-assigned spending score (1–100) | Numeric |

**Records:** 200 customers, no missing values.

---

## Notebooks

### 1. `KMeans2Dim.ipynb` — Sklearn K-Means (2D)

**Features used:** `Annual Income (k$)`, `Spending Score (1-100)`

| Step | Detail |
|---|---|
| EDA | Shape, head, info, null check |
| Preprocessing | `StandardScaler` for feature scaling |
| Clustering | `sklearn.cluster.KMeans` with `n_clusters=5`, `random_state=42` |
| Visualization | 2D scatter plot (`matplotlib`) — points colored by cluster, centroids marked in red |
| Analysis | Group-by cluster mean for income and spending |

**Key code highlights:**

- Uses `fit_predict()` to assign cluster labels directly to the DataFrame.
- Centroids are plotted in scaled space using red **X** markers.
- Cluster analysis prints mean income and spending per cluster.

---

### 2. `KMeans3Dim.ipynb` — Sklearn K-Means (3D)

**Features used:** `Annual Income (k$)`, `Spending Score (1-100)`, `Age`

| Step | Detail |
|---|---|
| EDA | Shape, head, info, null check |
| Preprocessing | `StandardScaler` on 3 features |
| Clustering | `sklearn.cluster.KMeans`, 5 clusters |
| Visualization | Interactive 3D scatter plot (`plotly.graph_objects`) |
| Analysis | Group-by cluster mean for income, spending, and age |

**Key differences from 2D version:**

- Adds `Age` as a third clustering dimension.
- Uses **Plotly** `Scatter3d` for an interactive, rotatable 3D visualization.
- Centroids shown as red **x** symbols in 3D space.

---

### 3. `KMeans4Dim.ipynb` — Sklearn K-Means (4D)

**Features used:** `Age`, `Annual Income (k$)`, `Spending Score (1-100)`, `Genre` (one-hot encoded)

| Step | Detail |
|---|---|
| EDA | Shape, head, info, null check |
| Encoding | One-hot encoding of `Genre` using `pd.get_dummies(drop_first=True)` → creates `Genre_Male` column |
| Feature Selection | All columns except `CustomerID` |
| Preprocessing | `StandardScaler` on 4 features |
| Clustering | `sklearn.cluster.KMeans`, 5 clusters |
| Visualization | Interactive 3D scatter (`plotly`) projecting onto Income × Spending × Age axes |
| Analysis | Full cluster mean across all encoded features |

**Key differences from 3D version:**

- Incorporates **gender** as a binary feature via one-hot encoding.
- Clustering is performed in 4D, but visualization projects down to 3D (Income, Spending, Age).
- Hover tooltips display original feature values including gender.

---

### 4. `Manual_2D_Kmeans.ipynb` — Manual K-Means Implementation

**Features used:** `Annual Income (k$)`, `Spending Score (1-100)`

A from-scratch implementation of K-Means **without any ML libraries** (only `csv`, `random`, `math`).

| Step | Detail |
|---|---|
| Data Loading | `csv.DictReader` to parse the CSV |
| Standardization | Manual Z-score: $z = \frac{x - \mu}{\sigma}$ |
| Initialization | Random selection of 5 data points as initial centroids (`random.seed(42)`) |
| Distance Metric | **Squared Euclidean**: $(x_1 - x_2)^2 + (y_1 - y_2)^2$ |
| Assignment | Each point assigned to the nearest centroid |
| Update | Centroid = mean of all points in the cluster |
| Convergence | Stops when centroid movement < $10^{-6}$ (checked but loop runs up to 1000 iterations) |
| Output | Cluster size, centroid in original scale, sample points |

**Algorithm pseudocode:**

```
1. Initialize K centroids randomly from the data
2. Repeat until convergence or max_iters:
   a. Assign each point to its nearest centroid (Euclidean distance)
   b. Recompute each centroid as the MEAN of its assigned points
   c. If any cluster is empty, reinitialize its centroid randomly
3. Output final clusters and centroids
```

---

### 5. `Manual_2D_Kmedian.ipynb` — Manual K-Medians Implementation

**Features used:** `Annual Income (k$)`, `Spending Score (1-100)`

A from-scratch implementation of K-Medians — identical structure to the manual K-Means but with two critical differences:

| Aspect | K-Means | K-Medians |
|---|---|---|
| **Distance Metric** | Squared Euclidean: $(x_1-x_2)^2 + (y_1-y_2)^2$ | Manhattan: $|x_1-x_2| + |y_1-y_2|$ |
| **Centroid Update** | Mean of cluster points | **Median** of cluster points (component-wise) |

**Median computation:**

- Sort each dimension independently.
- If the cluster has an **odd** number of points: median = middle element.
- If **even**: median = average of the two middle elements.

$$\text{median}(x) = \begin{cases} x_{\lfloor n/2 \rfloor} & \text{if } n \text{ is odd} \\ \frac{x_{n/2-1} + x_{n/2}}{2} & \text{if } n \text{ is even} \end{cases}$$

---

### 6. `Comparision.ipynb` — K-Means vs K-Medians Benchmark

Compares the **execution time** of the manual K-Means and K-Medians implementations side by side.

| Parameter | Value |
|---|---|
| Clusters (k) | 5 |
| Max Iterations | 1,000 |
| Random Seed | 42 |
| Timer | `time.perf_counter()` |

**Output:**

- Execution time for K-Means and K-Medians.
- Which algorithm is faster.
- Absolute time difference.

---

### 7. `ExecutionTime.ipynb` — Extended Benchmark (100K Iterations)

Same structure as `Comparision.ipynb` but with `max_iters=100,000` (instead of 1,000) to amplify timing differences and produce a more reliable comparison.

---

## Key Concepts

### K-Means Clustering

- **Type:** Unsupervised, partitional clustering.
- **Objective:** Minimize within-cluster sum of squares (WCSS / inertia).
- **Centroid update:** Mean → sensitive to outliers.
- **Distance:** Euclidean.

### K-Medians Clustering

- **Type:** Unsupervised, partitional clustering.
- **Objective:** Minimize within-cluster sum of absolute deviations.
- **Centroid update:** Median → more robust to outliers.
- **Distance:** Manhattan (L1).

### Feature Scaling

All notebooks apply **Z-score standardization** before clustering:

$$z = \frac{x - \mu}{\sigma}$$

This ensures features with different ranges (e.g., income 15–137 vs. spending 1–100) contribute equally to distance calculations.

---

## Expected Customer Segments (5 Clusters)

| Cluster | Income | Spending | Label |
|---|---|---|---|
| A | High | High | Premium / VIP customers |
| B | High | Low | Careful / conservative spenders |
| C | Low | High | Impulsive / at-risk spenders |
| D | Low | Low | Budget-conscious customers |
| E | Medium | Medium | Average customers |

---

## File Structure

```
Lab_10_25022026/
├── Mall_Customers.csv          # Dataset (200 records)
├── Question.txt                # Lab instructions
├── KMeans2Dim.ipynb            # Sklearn K-Means, 2 features, matplotlib
├── KMeans3Dim.ipynb            # Sklearn K-Means, 3 features, plotly 3D
├── KMeans4Dim.ipynb            # Sklearn K-Means, 4 features (with gender)
├── Manual_2D_Kmeans.ipynb      # From-scratch K-Means (no libraries)
├── Manual_2D_Kmedian.ipynb     # From-scratch K-Medians (no libraries)
├── Comparision.ipynb           # K-Means vs K-Medians timing (1K iters)
├── ExecutionTime.ipynb         # K-Means vs K-Medians timing (100K iters)
└── README.md                   # This file
```

---

## Dependencies

| Library | Used In | Purpose |
|---|---|---|
| `pandas` | KMeans2Dim, 3Dim, 4Dim | Data loading and analysis |
| `numpy` | KMeans2Dim, 3Dim, 4Dim | Array operations |
| `matplotlib` | KMeans2Dim | 2D scatter plot |
| `plotly` | KMeans3Dim, 4Dim | Interactive 3D plots |
| `sklearn` | KMeans2Dim, 3Dim, 4Dim | KMeans algorithm, StandardScaler |
| `csv` | Manual notebooks, benchmarks | CSV file reading |
| `math` | Manual notebooks, benchmarks | `sqrt` for std deviation |
| `random` | Manual notebooks, benchmarks | Centroid initialization |
| `time` | Benchmark notebooks | `perf_counter()` for timing |
