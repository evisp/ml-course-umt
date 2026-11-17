# Block 2 · Models & Optimization

<p class="block-sub">Weeks 5 to 9 · New York taxi trips</p>

Block 1 built something you can trust: a question with a precise target, data split the way the model will be used, features that cannot leak, and an evaluation that reports where the model fails. What it did not do is take the model seriously. Logistic regression and a single tree were tools borrowed to make a point about method.

This block opens them up. What is a model actually doing when it fits? How does it find its answer, and when does that search fail? What makes a model memorise instead of learn, and how do you stop it? And when a model tells you it is 80% sure, what is that worth?

<div class="roadmap-track">
  <div class="track-seg seg-1"><span class="track-weeks">Week 05</span><b>Fit</b><br>Loss, coefficients, two models from one idea</div>
  <div class="track-seg seg-2"><span class="track-weeks">Week 06</span><b>Optimize</b><br>Gradient descent, learning rates, scaling</div>
  <div class="track-seg seg-3"><span class="track-weeks">Week 07</span><b>Generalize</b><br>Bias, variance, regularization</div>
  <div class="track-seg seg-4"><span class="track-weeks">Week 08</span><b>Ensemble</b><br>Trees, forests, boosting</div>
  <div class="track-seg seg-4"><span class="track-weeks">Week 09</span><b>Choose</b><br>Selection, calibration, imbalance</div>
  <div class="track-seg seg-project"><span class="track-weeks">Weeks 5 to 9</span><b>Project 2</b><br>A defensible model comparison</div>
</div>

## Four promises a model makes { .section-label }

Block 1 was organised around four ways a score can lie. This block is organised around four promises every model makes, and the week that checks each one.

<div class="grid cards" markdown>

-   :material-function-variant:{ .lg .middle } **"I found the pattern"**

    ---

    A model is a shape plus a loss: a rule for what counts as a mistake, and a search for the parameters that make mistakes smallest. Once you can read a coefficient, a linear model stops being a black box.

    **Checked in Week 05**

-   :material-stairs-down:{ .lg .middle } **"I will find it reliably"**

    ---

    Fitting is a search, and searches fail. Too large a step and it diverges; too small and it never arrives; badly scaled inputs and it crawls. All three are visible, and all three are fixable.

    **Checked in Week 06**

-   :material-mirror:{ .lg .middle } **"I did not just memorise"**

    ---

    Any model complex enough can reproduce its training data perfectly and be useless. The gap between what it knows and what it has learned is measurable, and regularization is how you close it.

    **Checked in Weeks 07 and 08**

-   :material-scale-balance:{ .lg .middle } **"My confidence is honest"**

    ---

    A score of 0.8 should mean something. Choosing between models, tuning them without fooling yourself, and making probabilities mean what they say are the last steps before anyone can rely on the output.

    **Checked in Week 09**

</div>

## The same city, the same questions { .section-label }

Block 1 taught on Olist and set Project 1 on New York taxi trips. From here, the taxi data is the running example too: you have already cleaned it, split it, and argued about it for four weeks, which means no time is spent explaining what a column means.

Three of Project 1's four questions come with us, and the fourth stays as a reminder.

| | The question | Why it is here |
|---|---|---|
| **A** | What will this trip cost? | Nearly a straight line, with coefficients you can check against the published meter rate |
| **B** | How long will this trip take? | Not a straight line at all. This is where trees and boosting earn their keep |
| **C** | Will this trip crawl? | Classification, with enough signal to compare models honestly |
| **D** | Will this passenger tip well? | The counterexample. No amount of modelling fixes a question the data cannot answer |

Everything starts from `taxi.py`, with the cleaning decisions made in Project 1. Labs work on a sample so they stay fast on a laptop; the numbers on these pages come from the full months.

## The bar to beat { .section-label }

Project 1 answered all four questions with simple tools: linear and logistic regression, and a single decision tree. Those results are the baseline for everything in this block.

![Project 1's results on the July trips](../assets/images/03-models-optimization/b2-bar-light.png#only-light)
![Project 1's results on the July trips](../assets/images/03-models-optimization/b2-bar-dark.png#only-dark)

*Measured once on July, with Project 1's tools. Every claim in Block 2 is made against these numbers, on the same trips.*

| Question | Project 1's answer | July result |
|---|---|---|
| **A · fare** | Tree, depth 12 | MAE **$2.40**, against $7.83 for predicting the median |
| **B · duration** | Tree, depth 16 | MAE **4.58 min**, against 8.48 |
| **C · crawl** | Logistic regression with zones | Lift **3.68**, against 1.0 for guessing |
| **D · tip** | Logistic regression with zones | Lift **1.27**. The ceiling, not a win |

!!! note "What counts as progress"
    Not a better number on its own. A better number **on the same test months**, with an interval that clears the old one, from a model whose extra complexity you can justify. Week 9 makes that standard precise.

## Week by week { .section-label }

<div class="block-card" markdown>

<div class="block-head">
  <span class="block-num">2</span>
  <span class="block-label">Models & Optimization</span>
  <span class="block-weeks">Weeks 5 to 9</span>
</div>

<p class="block-sub">From "it fits" to "I can defend why this model and not that one".</p>

<div class="week-row">
  <div class="week-num">05</div>
  <div class="week-body"><b>Linear models.</b> A loss turns a guess into a number you can improve. Linear regression on the fare, read as a starting charge and a price per mile. Logistic regression on the crawl, read as odds. Two models, one idea.</div>
</div>

<div class="week-row">
  <div class="week-num">06</div>
  <div class="week-body"><b>Optimization.</b> Gradient descent written out once, by hand, then left to the library. Learning rates that diverge, stall, or work. Why scaling changes everything, measured rather than asserted.</div>
</div>

<div class="week-row">
  <div class="week-num">07</div>
  <div class="week-body"><b>Bias, variance and regularization.</b> Why a deeper tree stops helping. Learning curves that say whether more data would help. Ridge and lasso across hundreds of one-hot zone columns, and what each one does to the coefficients.</div>
</div>

<div class="week-row">
  <div class="week-num">08</div>
  <div class="week-body"><b>Trees and boosting.</b> One tree, many trees, and trees that correct each other. Where boosting wins, by how much, and the questions where it changes nothing.</div>
</div>

<div class="week-row">
  <div class="week-num">09</div>
  <div class="week-body"><b>Model selection and calibration.</b> Cross-validation done properly on data with time in it. An equal tuning budget for every candidate. Turning scores into probabilities you can quote, and handling a rare class without lying about it.</div>
</div>

<div class="block-project" markdown>
**Project 2 · A defensible model comparison.** Opens in Week 5, due at the end of Week 9. Several model families, an equal tuning budget, and an explicit claim about which differences are real.
</div>

</div>

## What you build { .section-label }

<div class="outcomes">
  <div class="outcome"><b>A gradient descent you wrote yourself</b>, once, so the library's version is never mysterious again.</div>
  <div class="outcome"><b>A regularized model across hundreds of columns</b>, with the coefficients it keeps and the ones it zeroes.</div>
  <div class="outcome"><b>A boosted model, and an honest account</b> of what it bought you compared with Project 1's single tree.</div>
  <div class="outcome"><b>A tuning protocol</b> that spends the same budget on every candidate, so the comparison means something.</div>
  <div class="outcome"><b>A calibrated classifier</b> whose probabilities can be quoted to someone who will act on them.</div>
</div>

## Before you start { .section-label }

<div class="principle" markdown>

**Everything in Block 1 still applies.**

The split is still by time, learned steps still live inside a pipeline, and test is still looked at once. A better model does not buy you a looser method: it makes a loose method more dangerous, because the score is now impressive enough to believe.

</div>

Worth rereading: [Block 1 in review](../02-data-pipeline/review.md), and your own Project 1 repository, which is where the data decisions you are about to rely on were made.

**Next:** [Week 05 · Linear models](week-05-linear-models.md)
