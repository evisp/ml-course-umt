# Submitting your work

<p class="block-sub">One repository, pushed before the deadline.</p>

Submission is deliberately simple. There is no upload form and no archive to send: your team's GitHub repository **is** the submission, and its history is part of what gets graded.

## The four rules { .section-label }

<div class="outcomes">
  <div class="outcome"><b>One repository per team</b>, on GitHub, for the whole project.</div>
  <div class="outcome"><b>Every member commits.</b> The history should show three people working, not one person pushing on the last night.</div>
  <div class="outcome"><b>Push before the deadline.</b> The last commit timestamp is your submission time.</div>
  <div class="outcome"><b>Make it readable.</b> Public, or private with the instructor added as a collaborator.</div>
</div>

## The test that decides the Execution points { .section-label }

<div class="principle" markdown>

**A stranger clones your repository, follows the README, and everything runs.**

From the raw data to your final number, with no undocumented steps and nothing that exists only on your laptop.

</div>

Before you submit, do it for real: clone your own repository into a new folder, follow your README as written, and run everything. Most lost Execution points are found in those ten minutes.

## What the repository contains { .section-label }

The full list is in each project brief. Every project expects at least:

| | |
|---|---|
| `README.md` | What this is, how to run it, and where you used AI |
| `PROBLEM.md` | The question, the target and its decisions, the metric, the baseline |
| `MODEL_CARD.md` | What the model does, how well, where it fails |
| `data/` | The script that downloads the data. **Never the data itself** |
| `src/`, `notebooks/` | The code that rebuilds everything, and the story of how you got there |

The [repo conventions](../01-toolkit/repo-conventions.md) page has the layout and a `.gitignore` to start from.

## Deadlines and lateness { .section-label }

Deadlines are in each project brief, announced when the project opens. If something real happens, ask for an extension **before** the deadline rather than explaining afterwards.

## Before you push for the last time { .section-label }

- [ ] A fresh clone runs from the README alone
- [ ] No data files, no secrets, no absolute paths from your machine
- [ ] Seeds set, so the numbers come out the same way twice
- [ ] `PROBLEM.md` and `MODEL_CARD.md` are written and current
- [ ] The README declares any use of AI
- [ ] Your peer review of another team is delivered
- [ ] Every member has commits, and can explain any line of the submission

---

**See also:** [all projects](index.md) · [rubrics](rubrics.md) · [repo conventions](../01-toolkit/repo-conventions.md)
