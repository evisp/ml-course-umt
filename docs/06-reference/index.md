# Reference

Material you come back to, rather than read once. Nothing here is assigned. Open a page when a week needs it, or when something in a lab stops making sense.

## When you need what { .section-label }

| Week | You are doing | Open this |
|:--:|---|---|
| **04** | Evaluation and error analysis | [Choosing a metric](metrics.md) |
| **05** | Linear models and the loss landscape | [Linear algebra](linear-algebra.md) |
| **06** | Optimization and gradient descent | [Calculus for ML](calculus.md) |
| **07** | Bias, variance and regularization | [Linear algebra](linear-algebra.md), norms section |
| **09** | Model selection and calibration | [Probability and statistics](probability-statistics.md) |
| **11** | Dimensionality reduction and PCA | [Linear algebra](linear-algebra.md), SVD section |
| **any** | Writing pipeline code | [scikit-learn cheatsheet](sklearn-cheatsheet.md) |

If you are in Weeks 1 to 3, you can ignore this whole section. The maths arrives in Block 2.

## Maths you actually use { .section-label }

Each page is scoped to the two or three weeks that need it, and says up front what it leaves out.

<div class="grid cards" markdown>

-   :material-matrix:{ .lg .middle } **Linear algebra**

    ---

    Vectors, dot products, matrix shapes, norms, projection, and the SVD that PCA is built on.

    [:octicons-arrow-right-24: Open](linear-algebra.md)

-   :material-function-variant:{ .lg .middle } **Calculus for ML**

    ---

    Derivatives, gradients, the chain rule, and deriving the update rule that gradient descent runs on.

    [:octicons-arrow-right-24: Open](calculus.md)

-   :material-chart-bell-curve-cumulative:{ .lg .middle } **Probability & statistics**

    ---

    Distributions, expectation and variance, sampling, and deciding whether a difference between two models is real.

    [:octicons-arrow-right-24: Open](probability-statistics.md)

</div>

## While you work { .section-label }

<div class="grid cards" markdown>

-   :material-scale-balance:{ .lg .middle } **Choosing a metric**

    ---

    Precision against recall, ROC against PR under imbalance, RMSE against MAE, and what each one hides from you.

    [:octicons-arrow-right-24: Open](metrics.md)

-   :material-language-python:{ .lg .middle } **scikit-learn cheatsheet**

    ---

    Pipelines, column transformers, cross-validation, and the API patterns worth committing to memory.

    [:octicons-arrow-right-24: Open](sklearn-cheatsheet.md)

</div>

## Where to find data { .section-label }

For the capstone, and for anything you build after this course. Your project dataset has to meet the requirements in the project brief, so read those before you fall in love with something.

<div class="outcomes">
  <div class="outcome"><b><a href="https://www.kaggle.com/datasets">Kaggle Datasets</a>.</b> Enormous and uneven. Filter hard, and avoid anything with a thousand published notebooks.</div>
  <div class="outcome"><b><a href="https://archive.ics.uci.edu/">UCI Machine Learning Repository</a>.</b> Small, clean, well documented. Good for drills, usually too tidy for a project.</div>
  <div class="outcome"><b><a href="https://open-data.europa.eu/">EU Open Data Portal</a> and <a href="https://www.instat.gov.al/">INSTAT</a>.</b> Real administrative data, genuinely messy, and local.</div>
  <div class="outcome"><b><a href="https://huggingface.co/datasets">Hugging Face Datasets</a>.</b> Strong for text and images, with licences stated properly.</div>
  <div class="outcome"><b><a href="https://datasetsearch.research.google.com/">Google Dataset Search</a>.</b> Use when you know the domain but not the source.</div>
</div>

## Going further { .section-label }

Five things worth your time, in rough order of how soon they are useful.

<div class="outcomes">
  <div class="outcome"><b><a href="https://www.3blue1brown.com/topics/linear-algebra">3Blue1Brown, Essence of Linear Algebra</a>.</b> Fifteen short videos. The best intuition for matrices anyone has built. Watch it even if you did linear algebra already.</div>
  <div class="outcome"><b><a href="https://mml-book.github.io/">Mathematics for Machine Learning</a>, Deisenroth, Faisal and Ong.</b> Free PDF. The maths pages here are a scoped version of its first five chapters.</div>
  <div class="outcome"><b><a href="https://www.oreilly.com/library/view/hands-on-machine-learning/9781098125967/">Hands-On Machine Learning</a>, Géron.</b> The closest thing to a textbook for this course. Chapters 1 to 7 track Blocks 1 and 2 closely.</div>
  <div class="outcome"><b><a href="https://www.statlearning.com/">An Introduction to Statistical Learning</a>, James et al.</b> Free PDF. Stronger than Géron on why methods work, lighter on code.</div>
  <div class="outcome"><b><a href="https://scikit-learn.org/stable/user_guide.html">scikit-learn user guide</a>.</b> Not a fallback for when documentation fails. It is genuinely one of the better explanations of applied machine learning in existence.</div>
</div>
