# Roadmap

Fourteen weeks, three blocks, three projects. Each block ends with something you built and can defend, and each one is less scaffolded than the last.

The sequence is deliberate. You spend the first four weeks barely modelling at all, because everything that quietly ruins a machine learning project happens before the model is trained.

<div class="roadmap-track">
  <div class="track-seg seg-1">
    <span class="track-weeks">Weeks 1–4</span>
    <b>Data &amp; the Pipeline</b>
  </div>
  <div class="track-seg seg-2">
    <span class="track-weeks">Weeks 5–9</span>
    <b>Models &amp; Optimization</b>
  </div>
  <div class="track-seg seg-3">
    <span class="track-weeks">Weeks 10–14</span>
    <b>Representation &amp; Systems</b>
  </div>
</div>

<div class="block-card" markdown>

<div class="block-head">
<span class="block-num">Block 1</span>
<span class="block-weeks">Weeks 1–4</span>
</div>

### Data &amp; the Pipeline

<p class="block-sub">A model is the easy part.</p>

<div class="weeks">
<div class="week-row">
<span class="week-num">01</span>
<div class="week-body">
<b>Problem framing &amp; baselines</b>
<p>Define a target, a metric, and a baseline before writing any model code.</p>
</div>
</div>
<div class="week-row">
<span class="week-num">02</span>
<div class="week-body">
<b>Data quality &amp; splitting</b>
<p>Choose the right split, and explore only the training data.</p>
</div>
</div>
<div class="week-row">
<span class="week-num">03</span>
<div class="week-body">
<b>Feature engineering</b>
<p>Build preprocessing that is fitted on the training set alone.</p>
</div>
</div>
<div class="week-row">
<span class="week-num">04</span>
<div class="week-body">
<b>Evaluation &amp; error analysis</b>
<p>Pick a metric that matches the cost of error, and find where the model fails.</p>
</div>
</div>
</div>

<p class="block-label">You can now</p>

<div class="chips chips-left">
<span class="chip">Frame a problem</span>
<span class="chip">Split without leaking</span>
<span class="chip">Engineer features</span>
<span class="chip">Evaluate honestly</span>
</div>

[Project 1 · Raw data to a validated baseline](../05-projects/project-1-pipeline.md){ .block-project }

</div>

<div class="block-card" markdown>

<div class="block-head">
<span class="block-num">Block 2</span>
<span class="block-weeks">Weeks 5–9</span>
</div>

### Models &amp; Optimization

<p class="block-sub">Understand what the fitting procedure is actually doing.</p>

<div class="weeks">
<div class="week-row">
<span class="week-num">05</span>
<div class="week-body">
<b>Linear models &amp; the loss landscape</b>
<p>Derive linear and logistic regression from the loss up, and read the coefficients honestly.</p>
</div>
</div>
<div class="week-row">
<span class="week-num">06</span>
<div class="week-body">
<b>Optimization</b>
<p>Implement gradient descent, and diagnose why it stalls or diverges.</p>
</div>
</div>
<div class="week-row">
<span class="week-num">07</span>
<div class="week-body">
<b>Bias, variance &amp; regularization</b>
<p>Read a learning curve, and reach for ridge or lasso for the right reason.</p>
</div>
</div>
<div class="week-row">
<span class="week-num">08</span>
<div class="week-body">
<b>Tree-based models</b>
<p>Tune gradient boosting, and know when it beats a neural network.</p>
</div>
</div>
<div class="week-row">
<span class="week-num">09</span>
<div class="week-body">
<b>Model selection &amp; calibration</b>
<p>Run nested cross-validation, calibrate probabilities, and handle class imbalance.</p>
</div>
</div>
</div>

<p class="block-label">You can now</p>

<div class="chips chips-left">
<span class="chip">Compare fairly</span>
<span class="chip">Tune without cheating</span>
<span class="chip">Read a learning curve</span>
<span class="chip">Report variance</span>
</div>

[Project 2 · A defensible model comparison](../05-projects/project-2-comparison.md){ .block-project }

</div>

<div class="block-card" markdown>

<div class="block-head">
<span class="block-num">Block 3</span>
<span class="block-weeks">Weeks 10–14</span>
</div>

### Representation &amp; Systems

<p class="block-sub">Unlabeled data, and getting the thing out of the notebook.</p>

<div class="weeks">
<div class="week-row">
<span class="week-num">10</span>
<div class="week-body">
<b>Clustering</b>
<p>Cluster three ways and defend your choice of <i>k</i> without ground truth.</p>
</div>
</div>
<div class="week-row">
<span class="week-num">11</span>
<div class="week-body">
<b>Dimensionality reduction</b>
<p>Run PCA via SVD, and read a t-SNE plot without being fooled by it.</p>
</div>
</div>
<div class="week-row">
<span class="week-num">12</span>
<div class="week-body">
<b>Bridge to neural networks</b>
<p>Build an MLP as stacked linear models, and say honestly when it beats boosting.</p>
</div>
</div>
<div class="week-row">
<span class="week-num">13</span>
<div class="week-body">
<b>ML systems &amp; responsibility</b>
<p>Serve a model behind an API, and explain a single prediction to someone who is not you.</p>
</div>
</div>
<div class="week-row">
<span class="week-num">14</span>
<div class="week-body">
<b>Synthesis &amp; presentations</b>
<p>Present a complete system and defend its design under questioning.</p>
</div>
</div>
</div>

<p class="block-label">You can now</p>

<div class="chips chips-left">
<span class="chip">Work without labels</span>
<span class="chip">Reduce dimensions</span>
<span class="chip">Ship a model</span>
<span class="chip">Explain a prediction</span>
</div>

[Project 3 · Capstone](../05-projects/project-3-capstone.md){ .block-project }

</div>

## What this course does not cover { .section-label }

Deliberate omissions, so you know where to look instead.

<div class="outcomes">
  <div class="outcome"><b>Deep learning architectures.</b> CNNs, RNNs, transformers. Covered in your Deep Learning course. Week 12 is the bridge to it.</div>
  <div class="outcome"><b>Big data engineering.</b> Spark, distributed training, warehousing. An adjacent discipline with its own course.</div>
  <div class="outcome"><b>Reinforcement learning.</b> Mentioned in Week 1 so you know where it sits on the map, not taught.</div>
</div>

## Before Week 1 { .section-label }

!!! warning "Do this in the first days, not in Week 3"
    - [ ] A working Python environment, see [environment setup](../01-toolkit/environment-setup.md)
    - [ ] A GitHub account you can push to from your own machine
    - [ ] Comfortable with dataframes and arrays, see the [NumPy and pandas refresher](../01-toolkit/numpy-pandas.md)

Everything you need is in the [toolkit](../01-toolkit/index.md). Budget one afternoon.

---

**Next:** [how the grade works](grading.md), then [Week 1](../02-data-pipeline/week-01-problem-framing.md).
