# scikit-learn Cheatsheet

!!! abstract "At a glance"
    **Use it:** whenever you write pipeline code, in any week
    **Version:** scikit-learn 1.5 or later. Older tutorials online use names that have since changed.
    **The rule behind every snippet:** preprocessing is fitted on training data only. Copy from here and you cannot leak by accident.

Patterns in the order a project uses them: split, preprocess, model, evaluate, tune, save. Section 1 is the complete template. Everything after it explains a piece of it, or swaps one piece for another.

---

## 1. The template

Every project in this course can start from this. It runs as written once you point it at your data and name your target.

```python
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

RANDOM_STATE = 42

df = pd.read_csv("data/raw/listings.csv")
X = df.drop(columns=["target"])
y = df["target"]

# 1. Split first. Everything after this line sees only X_train.
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE
)

numeric = X.select_dtypes("number").columns
categorical = X.select_dtypes(exclude="number").columns

# 2. Preprocessing, declared but not yet fitted.
preprocess = ColumnTransformer([
    ("num", Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
    ]), numeric),
    ("cat", Pipeline([
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ]), categorical),
])

# 3. Preprocessing and model as one object.
model = Pipeline([
    ("prep", preprocess),
    ("clf", LogisticRegression(max_iter=1000)),
])

# 4. Cross-validate on the training data.
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
scores = cross_val_score(model, X_train, y_train, cv=cv, scoring="roc_auc")
print(f"CV ROC AUC: {scores.mean():.3f} ± {scores.std():.3f}")

# 5. Touch the test set once, at the very end.
model.fit(X_train, y_train)
test_auc = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])
print(f"Test ROC AUC: {test_auc:.3f}")
```

For regression, swap three things: drop `stratify=y`, use `KFold` instead of `StratifiedKFold`, and replace the classifier and metric with, for example, `Ridge()` and `scoring="neg_mean_absolute_error"`.

## 2. The API in one idea

Every object in scikit-learn follows the same three verbs.

| Method | Does | Called on |
|---|---|---|
| `fit(X, y)` | Learns something from data and stores it | Training data only |
| `transform(X)` | Applies what was learned | Any data |
| `predict(X)` | Produces predictions | Any data |

`fit_transform` is a shortcut for fitting then transforming the same data, which is exactly why you should only ever call it on training data.

Whatever an object learned during `fit` is stored in attributes ending in an underscore: `scaler.mean_`, `model.coef_`. This is the same pattern as the `MedianImputer` class in the [Python refresher](../01-toolkit/python-refresher.md), and it is how every transformer and model in the library works.

## 3. Choosing a splitter

The split is a statement about how your model will be used. The [probability page](probability-statistics.md) explains the assumption each one makes.

| Your data | Use | Why |
|---|---|---|
| Independent rows, balanced | `KFold(shuffle=True)` | The default case |
| A rare class | `StratifiedKFold` | Keeps the class ratio in every fold |
| Several rows per building, patient, or user | `GroupKFold` | Keeps each group entirely on one side |
| Ordered in time | `TimeSeriesSplit` | Always trains on the past, tests on the future |

```python
from sklearn.model_selection import GroupKFold, GroupShuffleSplit, TimeSeriesSplit

# groups: one label per row saying which group it belongs to
groups = df["building_id"]

# a single grouped train/test split
gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=RANDOM_STATE)
train_idx, test_idx = next(gss.split(X, y, groups=groups))

# grouped cross-validation
cross_val_score(model, X, y, cv=GroupKFold(n_splits=5), groups=groups)

# time-ordered cross-validation, rows must already be sorted by time
cross_val_score(model, X, y, cv=TimeSeriesSplit(n_splits=5))
```

!!! danger "Drop the group column from the features"
    `building_id` tells the splitter which rows belong together. It should not also be a feature, or the model learns to recognise buildings instead of learning about apartments.

## 4. Preprocessing with `ColumnTransformer`

Different columns need different treatment. `ColumnTransformer` routes each group of columns through its own pipeline and joins the results.

| Step | Numeric columns | Categorical columns |
|---|---|---|
| Missing values | `SimpleImputer(strategy="median")` | `SimpleImputer(strategy="most_frequent")` |
| Transform | `StandardScaler()` | `OneHotEncoder(handle_unknown="ignore")` |

**`handle_unknown="ignore"` is not optional.** Without it, any category that appears in the test set but not in training, a new city or a rare heating type, crashes the pipeline.

Other transformers worth knowing:

| Transformer | Use for |
|---|---|
| `OrdinalEncoder` | Categories with a genuine order, such as *poor*, *fair*, *good* |
| `TargetEncoder` | High-cardinality categories, with cross-fitting built in |
| `FunctionTransformer(np.log1p)` | A log transform inside the pipeline |
| `PolynomialFeatures` | Interaction and squared terms |

!!! tip "Seeing what the pipeline produces"
    By default the output is an unlabelled array. To get a dataframe with column names while debugging:

    ```python
    preprocess.set_output(transform="pandas")
    ```

    This needs `OneHotEncoder(..., sparse_output=False)`, since a dataframe cannot hold a sparse matrix.

## 5. Why the `Pipeline` matters

Without a pipeline, you would scale the data and then cross-validate. The scaler would have seen every row, including the ones in each validation fold, and every score would be slightly optimistic.

With a pipeline, `cross_val_score` refits the *entire* chain inside every fold. The imputer's median, the scaler's mean, and the encoder's categories are all learned from that fold's training rows alone. This is the whole reason the template is built the way it is.

## 6. Baselines

Before any real model, measure what doing nothing scores. The [metrics page](metrics.md) lists the baseline for every metric.

```python
from sklearn.dummy import DummyClassifier, DummyRegressor

baseline = DummyClassifier(strategy="most_frequent")
cross_val_score(baseline, X_train, y_train, cv=cv, scoring="accuracy")

DummyRegressor(strategy="median")    # the MAE baseline
```

If your model does not clearly beat this, nothing else on the page matters yet.

## 7. Cross-validation

`cross_val_score` gives one metric. `cross_validate` gives several at once, plus training scores.

```python
from sklearn.model_selection import cross_validate

res = cross_validate(
    model, X_train, y_train, cv=cv,
    scoring=["roc_auc", "average_precision", "f1"],
    return_train_score=True,
)

res["test_roc_auc"].mean(), res["train_roc_auc"].mean()
```

**A large gap between train and test scores is overfitting**, visible before you ever touch the test set.

To compare two models fairly, use the same `cv` object with a fixed `random_state` for both, so they see identical folds. Then count the folds each one wins, as described on the [probability page](probability-statistics.md).

## 8. Tuning

Parameters inside a pipeline are named `step__parameter`, with two underscores, following the path through the pipeline.

```python
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from scipy.stats import loguniform

param_grid = {"clf__C": [0.01, 0.1, 1, 10]}

search = GridSearchCV(model, param_grid, cv=cv, scoring="roc_auc")
search.fit(X_train, y_train)

search.best_params_
search.best_score_
best_model = search.best_estimator_
```

The naming reaches into preprocessing too: `"prep__num__impute__strategy": ["mean", "median"]`.

`RandomizedSearchCV` samples the space instead of trying every combination, and is the better choice once there are more than two or three parameters.

```python
RandomizedSearchCV(model, {"clf__C": loguniform(1e-3, 1e2)},
                   n_iter=30, cv=cv, scoring="roc_auc", random_state=RANDOM_STATE)
```

!!! warning "`best_score_` is optimistic"
    It is the best of many attempts on the same folds, so it is biased upwards. To report an honest estimate of a tuned model, use nested cross-validation: a search inside, an evaluation outside.

    ```python
    inner = StratifiedKFold(n_splits=5, shuffle=True, random_state=1)
    outer = StratifiedKFold(n_splits=5, shuffle=True, random_state=2)

    search = GridSearchCV(model, param_grid, cv=inner, scoring="roc_auc")
    nested = cross_val_score(search, X_train, y_train, cv=outer, scoring="roc_auc")
    ```

    Week 9 covers why this matters.

## 9. Evaluating

```python
from sklearn.metrics import classification_report

print(classification_report(y_test, model.predict(X_test)))
```

The `Display` classes draw the standard plots straight from a fitted model:

```python
from sklearn.calibration import CalibrationDisplay
from sklearn.metrics import ConfusionMatrixDisplay, PrecisionRecallDisplay, RocCurveDisplay

ConfusionMatrixDisplay.from_estimator(model, X_test, y_test)
RocCurveDisplay.from_estimator(model, X_test, y_test)
PrecisionRecallDisplay.from_estimator(model, X_test, y_test)
CalibrationDisplay.from_estimator(model, X_test, y_test, n_bins=10)
```

For regression:

```python
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error

y_pred = model.predict(X_test)
mean_absolute_error(y_test, y_pred)
root_mean_squared_error(y_test, y_pred)
```

## 10. The models in this course

| Model | Hyperparameters that matter | Needs scaling | Week |
|---|---|:--:|:--:|
| `LinearRegression` | none | for interpreting coefficients | 05 |
| `Ridge` | `alpha` | yes | 07 |
| `Lasso` | `alpha` | yes | 07 |
| `LogisticRegression` | `C` (smaller means stronger regularization), `class_weight` | yes | 05 |
| `DecisionTreeClassifier` / `Regressor` | `max_depth`, `min_samples_leaf` | no | 01–04, 08 |
| `RandomForestClassifier` / `Regressor` | `n_estimators`, `max_features`, `min_samples_leaf` | no | 08 |
| `HistGradientBoostingClassifier` / `Regressor` | `learning_rate`, `max_iter`, `max_leaf_nodes` | no | 08 |
| `MLPClassifier` / `Regressor` | `hidden_layer_sizes`, `alpha`, `learning_rate_init` | yes | 12 |
| `KMeans` | `n_clusters`, `n_init` | yes | 10 |
| `PCA` | `n_components` | yes | 11 |

Everything linear or distance-based needs scaling. Trees split on thresholds and do not care.

!!! tip "`HistGradientBoosting` handles missing values itself"
    It needs no imputer, and with `categorical_features="from_dtype"` it handles pandas categorical columns directly, without one-hot encoding. On tabular data it is usually the strongest model in the library. XGBoost and LightGBM, added in Week 8, follow the same idea.

## 11. Looking inside

Column names after preprocessing, and linear coefficients:

```python
names = model.named_steps["prep"].get_feature_names_out()
coefs = pd.Series(model.named_steps["clf"].coef_[0], index=names).sort_values()
```

Coefficients are only comparable when features are on the same scale, which is one more reason the template scales them.

**Permutation importance** works for any model. It shuffles one column at a time and measures how much the score drops.

```python
from sklearn.inspection import permutation_importance

result = permutation_importance(
    model, X_test, y_test, n_repeats=10,
    scoring="roc_auc", random_state=RANDOM_STATE,
)
importance = pd.Series(result.importances_mean, index=X_test.columns)
importance.sort_values(ascending=False)
```

Run on the whole pipeline, it reports importance per *original* column, which is what you usually want to explain.

!!! warning "Be suspicious of `feature_importances_`"
    The built-in importance on tree models is computed from training data and is biased towards columns with many distinct values. Prefer permutation importance on held-out data.

## 12. Saving and loading

Save the whole pipeline, never just the model. The model alone cannot handle raw input, because it depends on the fitted imputer, scaler, and encoder.

```python
import joblib

joblib.dump(model, "models/pipeline.joblib")

model = joblib.load("models/pipeline.joblib")
model.predict(new_listings)    # raw data in, predictions out
```

Load with the same scikit-learn version you saved with. Week 13 builds on this.

## 13. Errors you will see

| You see | It means | Fix |
|---|---|---|
| `could not convert string to float: 'Tirana'` | A text column reached a model unencoded | Add it to the categorical list in the `ColumnTransformer` |
| `Input X contains NaN` | Missing values reached a model that cannot take them | Add a `SimpleImputer`, or use `HistGradientBoosting` |
| `Found unknown categories ... during transform` | A category in new data was never seen in training | `OneHotEncoder(handle_unknown="ignore")` |
| `Expected 2D array, got 1D array instead` | You passed one column as a flat array | `df[["col"]]` rather than `df["col"]`, or `.reshape(-1, 1)` |
| `Invalid parameter 'C' for estimator Pipeline` | Tuning parameter not prefixed with its step | `"clf__C"` rather than `"C"` |
| `ConvergenceWarning: lbfgs failed to converge` | The optimiser ran out of iterations | Scale the features, then raise `max_iter` |
| `The least populated class in y has only 1 member` | A class too rare to stratify | Merge rare classes, or collect more data |
| **No error, and a suspiciously good score** | Almost always leakage | Check what was fitted before the split, and whether any feature encodes the target |

The last row is the one that matters most, because nothing warns you. If a score looks too good, assume a leak until you have proved otherwise.

---

## Resources

- [scikit-learn user guide](https://scikit-learn.org/stable/user_guide.html). One of the best written explanations of applied machine learning, not just a reference.
- [Common pitfalls and recommended practices](https://scikit-learn.org/stable/common_pitfalls.html). Short, official, and entirely about leakage and reproducibility. Read it once.
- [Choosing the right estimator](https://scikit-learn.org/stable/machine_learning_map.html). The library's own flowchart.
