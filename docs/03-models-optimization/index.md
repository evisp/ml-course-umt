# Block 2 · Models & Optimization

<p class="block-sub">Weeks 5 to 9 · Hotel bookings</p>

Block 1 built something you can trust: a question with a precise target, data split the way the model will be used, features that cannot leak, and an evaluation that reports where the model fails. Project 1 proved you can do all of it yourself, on data nobody had prepared for you. What neither did is take the model seriously. Logistic regression and a single tree were tools borrowed to make a point about method.

This block opens them up. What is a model actually doing when it fits? How does it find its answer, and when does that search fail? What makes a model memorise instead of learn, and how do you stop it? And when a model tells you it is 80% sure, what is that worth?

<div class="roadmap-track">
  <div class="track-seg seg-1"><span class="track-weeks">Week 05</span><b>Fit</b><br>A shape, a loss, and coefficients you can read</div>
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

## A bench and a field { .section-label }

Block 1 taught on Olist and set Project 1 on New York taxis. Neither comes with us. A model block needs data chosen for what it shows about **models**, and taxi fares are nearly a formula — perfect for reading a coefficient, useless for watching a model overfit.

From here the running example is **hotel bookings**: 119,390 reservations at two Portuguese hotels, arrivals from July 2015 to August 2017. The data half is already done, in the open, on [the dataset page](dataset.md) and the notebook beside it. Every lab from Week 5 starts with the same two lines and the same table.

Each week then works at two levels, and the labs say which one they are on.

<div class="outcomes">
  <div class="outcome"><b>The bench.</b> Small, clean, often made up on purpose. You turn one knob and watch one thing move. Nothing is hidden, and nothing is realistic.</div>
  <div class="outcome"><b>The field.</b> The hotel data, with the split by booking date, a baseline beside every score, and the mess left in. Everything Block 1 taught still applies here, unchanged.</div>
</div>

The bench is where a mechanism becomes visible. The field is where you find out how much of it survives contact with real columns. Most weeks you will be surprised by how much smaller the effect is in the second place than the first — that gap is the lesson, not a disappointment.

## Two tracks, one table { .section-label }

The class splits in two. Both halves work the same rows, the same split and the same pipeline, and predict a different column.

| | The question | Target | What a model must beat |
|---|---|---|---|
| **A** | What will this booking pay per night? | `adr`, in euros | predicting the mean: **€29.92** average error |
| **B** | Will this booking be cancelled? | `is_canceled`, 0 or 1 | guessing: **lift 1.00**, at a 38.6% base rate |

They are not two halves of one lesson. They disagree, and the disagreement is the point:

- **Cancellation** has the dramatic failures. Two leaked columns, one of which gives three perfect scores, and a base rate that moves between periods so a raw score cannot be compared across them.
- **The nightly rate** has the clearest model gap. A straight line reaches R² 0.42; boosting reaches 0.74 without being told anything new.

Neither group sees the whole picture alone, so Week 8 puts you back together and you compare findings.

!!! note "Why not everybody does both"
    Because doing one properly is worth more than doing two approximately, and because having someone in the room who got a different answer is the cheapest way to learn that the answer depends on the question.

## The bar to beat { .section-label }

Both tracks start from a model you can read end to end, fitted in Week 5. Everything after that is measured against it, on the same validation period.

| | Floor | Week 5 | What later weeks have to clear |
|---|---|---|---|
| **A · the nightly rate** | €29.92 average error | **€21.31**, R² 0.421 | a lower error, with an interval that clears this one |
| **B · cancellation** | lift 1.00 | **lift 1.99**, PR AUC 0.795 | a higher lift, on the same period |

!!! note "What counts as progress"
    Not a better number on its own. A better number **on the same validation period**, with an interval that clears the old one, from a model whose extra complexity you can justify. Week 9 makes that standard precise.

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
  <div class="week-body"><b>Fit.</b> A model is a shape and a rule for being wrong. The nightly rate read as a starting price and a price per guest; cancellation read as odds. Two models, one idea, and the only week where you can see all the way through.</div>
</div>

<div class="week-row">
  <div class="week-num">06</div>
  <div class="week-body"><b>Optimization.</b> Gradient descent written out once, by hand, then left to the library. Learning rates that diverge, stall, or work. Why scaling changes everything, measured rather than asserted.</div>
</div>

<div class="week-row">
  <div class="week-num">07</div>
  <div class="week-body"><b>Generalize.</b> Why a deeper tree stops helping. Learning curves that say whether more data would help. Ridge and lasso across hundreds of one-hot columns — and the discovery that a penalty buys you almost nothing once you already have the data.</div>
</div>

<div class="week-row">
  <div class="week-num">08</div>
  <div class="week-body"><b>Ensemble.</b> One tree, many trees, and trees that correct each other. Where boosting wins, by how much, and the week the two tracks compare notes.</div>
</div>

<div class="week-row">
  <div class="week-num">09</div>
  <div class="week-body"><b>Choose.</b> Cross-validation done properly on data with time in it. An equal tuning budget for every candidate. Turning scores into probabilities you can quote, and handling a rare class without lying about it.</div>
</div>

<div class="block-project" markdown>
**Project 2 · A defensible model comparison.** Opens in Week 5, due at the end of Week 9. Several model families, an equal tuning budget, and an explicit claim about which differences are real.
</div>

</div>

## What you build { .section-label }

<div class="outcomes">
  <div class="outcome"><b>A gradient descent you wrote yourself</b>, once, so the library's version is never mysterious again.</div>
  <div class="outcome"><b>A regularized model across hundreds of columns</b>, with the coefficients it keeps, the ones it zeroes, and an honest account of whether it helped.</div>
  <div class="outcome"><b>A boosted model, and an honest account</b> of what it bought you compared with the readable model from Week 5.</div>
  <div class="outcome"><b>A tuning protocol</b> that spends the same budget on every candidate, so the comparison means something.</div>
  <div class="outcome"><b>A calibrated classifier</b> whose probabilities can be quoted to someone who will act on them.</div>
</div>

## Before you start { .section-label }

<div class="principle" markdown>

**Everything in Block 1 still applies.**

The split is still by time, learned steps still live inside a pipeline, and test is still looked at once. A better model does not buy you a looser method: it makes a loose method more dangerous, because the score is now impressive enough to believe.

</div>

Worth rereading: [Block 1 in review](../02-data-pipeline/review.md), and your own Project 1 repository — not for its data, which we are leaving behind, but for the decisions you made in it and the reasons you wrote down.

**Next:** [The dataset](dataset.md), then [Week 05 · Fit](week-05-linear-models.md)
