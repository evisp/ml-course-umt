# Grading

One hundred points. Sixty from three team projects, forty from an individual exam.

<div class="points-bar">
  <div class="points-seg seg-team" style="flex: 20">
    <b>20</b>
    <span>Project 1</span>
  </div>
  <div class="points-seg seg-team" style="flex: 20">
    <b>20</b>
    <span>Project 2</span>
  </div>
  <div class="points-seg seg-team" style="flex: 20">
    <b>20</b>
    <span>Capstone</span>
  </div>
  <div class="points-seg seg-exam" style="flex: 40">
    <b>40</b>
    <span>Final exam</span>
  </div>
</div>

<div class="points-legend">
  <span class="legend-item legend-team">60 points · built in teams</span>
  <span class="legend-item legend-exam">40 points · on your own</span>
</div>

The split is the point. Sixty points reward what you can build with other people, which is how the work actually happens once you leave. Forty reward what you understand alone, which no team can carry for you.

## The projects { .section-label }

Each block ends with one. Each is worth twenty points, graded against a rubric published before the project opens.

<div class="outcomes">
  <div class="outcome"><b>Project 1 · Validated baseline.</b> A messy dataset, simple models only, and a pipeline you can defend.</div>
  <div class="outcome"><b>Project 2 · Model comparison.</b> Several model families, an equal tuning budget, and a claim about which differences are real.</div>
  <div class="outcome"><b>Project 3 · Capstone.</b> Your own problem, end to end, presented live.</div>
</div>

Full specifications are on the [projects pages](../05-projects/index.md).

## How a project is graded { .section-label }

| Criterion | Points | What earns them |
|---|:--:|---|
| **Method** | 8 | Correct splitting, no leakage, evaluation that fits the problem |
| **Execution** | 5 | The code runs, the pipeline is reproducible, results are what you claim |
| **Communication** | 4 | A README and report a stranger can follow, limitations named |
| **Craft** | 3 | Repo conventions, commit history, code someone else can read |

!!! tip "Where points are actually lost"
    Almost never on modelling. They go on a leaked feature, a repo that will not clone and run, a conclusion the measured variance does not support, and a README written at midnight. Three of those four are settled before you write a line of model code.

## The final exam { .section-label }

Forty points, individual, closed book except for one page of notes you write yourself.

| Part | Points | What it asks |
|---|:--:|---|
| **A · Concepts** | 15 | Short answers about why, not what. *"Your CV score is 0.91 and your test score is 0.62. Give three plausible causes."* |
| **B · Code reading** | 15 | You are given a pipeline. Find what is wrong with it and explain the consequence. |
| **C · Judgement** | 10 | A scenario. Choose a metric, a split, and a baseline, and defend all three. |

Nothing on the exam asks you to recall a formula. It tests whether you can diagnose, choose, and justify, which is what the projects spend fourteen weeks training.

!!! success "How to prepare"
    Reread your own project logs. Most exam questions resemble something that went wrong in one of your three projects.

## Grades { .section-label }

| Points | Grade |
|---|:--:|
| 95 to 100 | **10** |
| 85 to 94 | **9** |
| 75 to 84 | **8** |
| 65 to 74 | **7** |
| 55 to 64 | **6** |
| 45 to 54 | **5** |
| Below 45 | **4** (fail) |

!!! info "Passing needs both halves"
    You need 45 points overall **and** at least 20 of the 40 exam points. A team cannot carry you to a pass. This is the one place where the individual component is a gate rather than a weight.

---

Team formation, peer review, and deadlines are set out in each project brief when the project opens.

**Next:** [Week 1](../02-data-pipeline/week-01-problem-framing.md)
