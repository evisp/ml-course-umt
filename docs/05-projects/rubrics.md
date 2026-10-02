# Rubrics

<p class="block-sub">What the twenty points of every project are made of.</p>

All three projects are graded against the same four criteria, in the same proportions. What changes between them is the standard: the same work that earns full marks in Project 1 earns most of them in the capstone, because by then you have had ten more weeks of practice and far less scaffolding.

Rubrics are published before a project opens, and nothing outside them is graded.

<div class="points-bar">
  <div class="points-seg" style="flex: 8"><b>8</b><span>Method</span></div>
  <div class="points-seg" style="flex: 5"><b>5</b><span>Execution</span></div>
  <div class="points-seg" style="flex: 4"><b>4</b><span>Communication</span></div>
  <div class="points-seg" style="flex: 3"><b>3</b><span>Craft</span></div>
</div>

<div class="points-legend">
  <span class="legend-item">20 points per project · 60 points across the three</span>
</div>

## The principle behind the weights { .section-label }

<div class="principle" markdown>

**The method, not the score.**

A modest result, honestly measured and clearly explained, scores above an impressive one that rests on a leak. Eight of the twenty points are about whether your answer means what you say it means. Only a handful are about the model.

</div>

## Method · 8 points { .section-label }

Does your result mean what you claim it means?

| Band | Points | What it looks like |
|---|:--:|---|
| **Strong** | 7 to 8 | A precise target with every decision inside it written down. A moment of prediction that every feature respects. Cleaning that never learns from the data. A split chosen from how the model will be used, and justified. Choices made on validation, and the test set used once. Results reported with their uncertainty. |
| **Solid** | 5 to 6 | The method is sound, with one weak link: a decision not justified, a slice not checked, an interval missing, or a choice that quietly used the test set. |
| **Shaky** | 3 to 4 | Something important is wrong: a leak, a split that does not fit the question, or a conclusion the measurement cannot support. The work is real, the result is not trustworthy. |
| **Broken** | 0 to 2 | No baseline, no honest split, or a score that cannot be reproduced or defended. |

## Execution · 5 points { .section-label }

Does it run, and are the numbers real?

| Band | Points | What it looks like |
|---|:--:|---|
| **Strong** | 5 | A stranger clones the repository, follows the README, and everything runs from the raw data to the final number. The pipeline rebuilds the results. The numbers in the report are the numbers the code produces. |
| **Solid** | 3 to 4 | Runs with one or two undocumented steps, a hard-coded path, or a seed left unset. |
| **Shaky** | 1 to 2 | Needs files you did not provide, cells run out of order, or results that cannot be reproduced from the repository. |
| **Broken** | 0 | It does not run. |

## Communication · 4 points { .section-label }

Can someone else follow it, and do you say what went wrong?

| Band | Points | What it looks like |
|---|:--:|---|
| **Strong** | 4 | A README a stranger can follow. A problem card and a model card that state the uncomfortable results as plainly as the good ones. Notebooks that read as an argument, with the failures included. |
| **Solid** | 3 | Clear, but thin in one place: limitations glossed over, or a notebook that is code with no narrative. |
| **Shaky** | 1 to 2 | A reader has to reconstruct what you did. Results presented without their caveats. |
| **Broken** | 0 | No README, or claims the work does not support. |

## Craft · 3 points { .section-label }

Would a colleague enjoy working in this repository?

| Band | Points | What it looks like |
|---|:--:|---|
| **Strong** | 3 | Clean layout, small commits with real messages, readable code, no data or secrets committed, and a peer review that genuinely helped another team. |
| **Solid** | 2 | Tidy enough, but with one habit missing: one giant commit, a stray notebook, or a review that says "looks good". |
| **Shaky** | 1 | Hard to navigate, or a history that hides how the work happened. |
| **Broken** | 0 | Data committed, no conventions, no review given. |

## What each project emphasises { .section-label }

The weights do not change. The expectations do.

| | What the rubric looks hardest at |
|---|---|
| **Project 1 · Validated baseline** | Method. The question is given, the models are simple, and almost everything that can go wrong goes wrong in the data. |
| **Project 2 · Model comparison** | Method and communication. Comparing model families fairly needs an equal tuning budget and an honest claim about which differences are real. |
| **Project 3 · Capstone** | All four, with less help. You choose the problem, so framing it well is part of the method, and you defend the whole system live. |

## Built together, defended on your own { .section-label }

One repository, three people, and a grade that is still yours.

<div class="outcomes">
  <div class="outcome"><b>The work is the team's.</b> You plan it together, divide it sensibly, review each other's code, and carry each other through the hard parts. That is the point of working in threes, and it is how the job works.</div>
  <div class="outcome"><b>The grade is individual.</b> The repository sets what the team achieved. What you can explain about it sets what you earn. In the Defend hour I choose who answers, and the question can be about any part of the project, not the part you wrote.</div>
  <div class="outcome"><b>So grades inside a team can differ.</b> Three people who built one project and understand it equally well will land in the same place. Someone who cannot explain what the team submitted will not.</div>
  <div class="outcome"><b>The evidence is public.</b> Your commits show what you built; the defence shows what you understood. Neither alone is enough.</div>
</div>

!!! tip "Carrying a teammate is not cheating, and being carried is not safe"
    Helping someone catch up is exactly what a team is for, and it costs you nothing in the rubric. But the help has to leave them able to explain the work, because that is what they will be asked to do. If a teammate stops contributing altogether, tell me in the week it happens, not after the deadline. A team of two with notice is fine.

!!! tip "Small bonuses for going further"
    Work that clearly goes beyond the brief can earn a small bonus: an extension that is genuinely well done, a tool that helps the whole class, a bug found in the course materials, or help given to other teams that they credit. Bonuses are modest and discretionary, they are never needed to reach full marks, and the total is still capped at 100.

---

**See also:** [all projects](index.md) · [submitting your work](submission-guide.md) · [grading](../00-course/grading.md)
