# Projects

<p class="block-sub">Three projects, three blocks, one portfolio.</p>

Each block ends with a project your team builds on real data. Each one is less guided than the last: in Project 1 the question is given, in Project 2 the comparison is yours to design, and in the capstone even the problem is yours to choose. By the end of the semester you have three repositories you can show anyone who asks what you can do.

<div class="roadmap-track">
  <div class="track-seg seg-1">
    <span class="track-weeks">Weeks 1–4</span>
    <b>Project 1 · A validated baseline</b>
  </div>
  <div class="track-seg seg-2">
    <span class="track-weeks">Weeks 5–9</span>
    <b>Project 2 · A model comparison</b>
  </div>
  <div class="track-seg seg-3">
    <span class="track-weeks">Weeks 10–14</span>
    <b>Project 3 · Capstone</b>
  </div>
</div>

<div class="grid cards" markdown>

-   :material-taxi:{ .lg .middle } **Project 1 · Raw data to a validated baseline**

    ---

    *One city, four questions.* New York taxi trips from 2026. Each team owns one question, from what a trip will cost to whether its passenger will tip well, and takes it through the four stages of Block 1.

    **Open now** · due end of Week 4 · 20 points

    [:octicons-arrow-right-24: Project 1 brief](project-1-pipeline.md)

-   :material-scale-balance:{ .lg .middle } **Project 2 · A defensible model comparison**

    ---

    Several model families, an equal tuning budget, and an honest claim about which differences are real. Written up in the shape of a short technical report.

    **Opens in Week 5** · due end of Week 9 · 20 points

    [:octicons-arrow-right-24: Project 2](project-2-comparison.md)

-   :material-rocket-launch:{ .lg .middle } **Project 3 · Capstone**

    ---

    Your own problem, end to end: framing, pipeline, evaluation, and a deployed model, presented live and defended under questions.

    **Opens in Week 10** · presented in Week 14 · 20 points

    [:octicons-arrow-right-24: Project 3](project-3-capstone.md)

</div>

## How every project works { .section-label }

<div class="beats">
  <div class="beat">
    <span class="beat-time">Every week</span>
    <b>Build in the open</b>
    <p>Each lab ends with a project step. Commit as you go: your history is part of the work.</p>
  </div>
  <div class="beat">
    <span class="beat-time">Before the deadline</span>
    <b>Swap and review</b>
    <p>Another team clones your repository, runs it from the README, and tells you what broke.</p>
  </div>
  <div class="beat">
    <span class="beat-time">At the end</span>
    <b>Defend it</b>
    <p>Present what you built and found. Anyone on the team may be asked to explain any part.</p>
  </div>
</div>

## What every repository contains { .section-label }

<div class="outcomes">
  <div class="outcome"><b><code>PROBLEM.md</code></b>, written before any modelling: the question, the target and its decisions, the moment of prediction, the metric, and the baseline.</div>
  <div class="outcome"><b>A cleaning function and a pipeline</b> that rebuild everything from the raw data, and never learn from rows they should not see.</div>
  <div class="outcome"><b><code>MODEL_CARD.md</code></b>, written at the end: what the model does, how well, where it fails, and when not to use it.</div>
  <div class="outcome"><b>A README a stranger can follow</b>, from a fresh clone to the final number, including where you used AI.</div>
</div>

The [repo conventions](../01-toolkit/repo-conventions.md) set out the layout, and the [grading page](../00-course/grading.md) how the 20 points of each project are awarded.

!!! quote
    The method, not the score. A modest result you can defend beats an impressive one you cannot.
