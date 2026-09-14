# Python Refresher

!!! abstract "At a glance"
    **Estimated time:** 30 minutes
    **You need:** a working [environment](environment-setup.md)
    **This is not:** a Python course. It is the specific subset this course leans on, plus the traps that cost people hours.

## Why this page exists

You already know Python. What follows is the part of it that shows up constantly in machine learning code, written in the style you will see in lectures and labs. Skim it. Where something looks unfamiliar, stop and try it.

If a whole section feels new, the [official tutorial](https://docs.python.org/3/tutorial/) and [Real Python](https://realpython.com/) are better places to learn it properly than this page.

---

## Comprehensions

You will read these far more often than you write loops.

```python
prices = [120, 340, 95, 410]

# list
doubled = [p * 2 for p in prices]

# with a condition
expensive = [p for p in prices if p > 200]

# dict
labels = {p: "high" if p > 200 else "low" for p in prices}

# nested, the readable limit
pairs = [(a, b) for a in "ab" for b in [1, 2]]
```

!!! tip "When not to use one"
    If a comprehension needs a line break to stay readable, write the loop. Clever one-liners are not a virtue when a classmate has to review your code.

## Functions worth writing properly

Type hints are optional in Python and expected in this course. They cost you five seconds and they document the function better than a comment.

```python
def train_test_sizes(n_rows: int, test_frac: float = 0.2) -> tuple[int, int]:
    """Return the number of training and test rows."""
    n_test = int(n_rows * test_frac)
    return n_rows - n_test, n_test
```

Default arguments, keyword arguments, and unpacking:

```python
def score(y_true, y_pred, *, metric: str = "rmse") -> float:
    ...

score(y, preds, metric="mae")   # keyword-only after the *
```

The `*` forces everything after it to be passed by name. Useful when a function has several options and positional order would be a guessing game.

!!! danger "The mutable default argument"
    This is the single most common Python bug in student code.

    ```python
    def add_feature(features=[]):     # wrong
        features.append("new")
        return features
    ```

    The list is created once, when the function is defined, and shared by every call. Do this instead:

    ```python
    def add_feature(features: list | None = None) -> list:
        features = [] if features is None else features
        features.append("new")
        return features
    ```

## Dictionaries

The workhorse for configuration, results, and anything keyed.

```python
results = {"model": "ridge", "rmse": 0.42}

results["r2"] = 0.81
alpha = results.get("alpha", 1.0)      # default instead of KeyError

for key, value in results.items():
    print(f"{key}: {value}")

merged = {**results, "fold": 3}        # copy with additions
```

Storing experiment results as a list of dicts is a pattern you will use all semester, because pandas turns it into a table in one line.

```python
runs = [
    {"model": "ridge", "alpha": 0.1, "rmse": 0.44},
    {"model": "ridge", "alpha": 1.0, "rmse": 0.42},
]
# later: pd.DataFrame(runs)
```

## Unpacking, `zip`, `enumerate`

```python
a, b = b, a                              # swap

first, *rest = [1, 2, 3, 4]              # first=1, rest=[2,3,4]

for i, name in enumerate(columns):       # index and value
    print(i, name)

for name, score in zip(names, scores):   # walk two lists together
    print(name, score)
```

## f-strings

```python
rmse = 0.4237
print(f"RMSE: {rmse:.3f}")          # RMSE: 0.424
print(f"{0.8123:.1%}")              # 81.2%
print(f"{1234567:,}")               # 1,234,567
print(f"{rmse=}")                   # rmse=0.4237, handy when debugging
```

## Paths, not strings

Hard-coded paths with slashes break when someone else runs your code on another operating system. Use `pathlib`.

```python
from pathlib import Path

DATA = Path("data/raw")
df_path = DATA / "listings.csv"

df_path.exists()
list(DATA.glob("*.csv"))
```

This matters for your grade. A project with `C:\Users\evis\Desktop\data.csv` in it cannot be run by anyone else.

## Errors

Catch what you expect, not everything.

```python
try:
    df = pd.read_csv(path)
except FileNotFoundError:
    raise FileNotFoundError(f"Missing dataset at {path}. See README for download steps.")
```

A bare `except:` hides real bugs and makes debugging much harder later.

## Classes, lightly

You will write few classes in this course, but you will read many, since scikit-learn is built on them. The pattern to recognise:

```python
class MedianImputer:
    def __init__(self, column: str):
        self.column = column
        self.median_ = None

    def fit(self, df):
        self.median_ = df[self.column].median()
        return self

    def transform(self, df):
        df = df.copy()
        df[self.column] = df[self.column].fillna(self.median_)
        return df
```

`fit` learns something from the training data and stores it with a trailing underscore. `transform` applies it. Every scikit-learn transformer follows this shape, and understanding it is most of what you need to build your own in Week 3.

## Two traps that cost real time

!!! failure "Assignment does not copy"
    ```python
    a = [1, 2, 3]
    b = a
    b.append(4)
    print(a)        # [1, 2, 3, 4]
    ```

    `b` is another name for the same list. To copy, use `a.copy()` for a shallow copy or `copy.deepcopy(a)` for a nested structure. The pandas version of this trap is `SettingWithCopyWarning`, covered in the [NumPy and pandas refresher](numpy-pandas.md).

!!! failure "Floating point equality"
    ```python
    0.1 + 0.2 == 0.3        # False
    ```

    Compare with a tolerance instead: `abs(a - b) < 1e-9`, or `numpy.isclose(a, b)`.

## Quick self-check

If you can answer these without looking, you are ready.

- [ ] What does `[x for x in data if x > 0]` produce, and how would you write it as a loop?
- [ ] Why is `def f(items=[])` a bug?
- [ ] What is the difference between `d["key"]` and `d.get("key")`?
- [ ] After `b = a` for a list, what happens to `a` when you modify `b`?
- [ ] Why use `Path("data") / "file.csv"` instead of `"data/file.csv"`?

## Summary and next steps

Nothing here is advanced. It is the vocabulary that lecture code assumes, and the four or five mistakes that reliably eat an afternoon.

**Next:** [NumPy and pandas refresher](numpy-pandas.md), which is where most of your actual course time will be spent.

## Resources

- [Python tutorial, official](https://docs.python.org/3/tutorial/) for the language itself
- [Real Python](https://realpython.com/) for readable deep dives on individual topics
- [Fluent Python](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/) if you want to go properly deep, after this course rather than during it
