<!--
WEEK PAGE TEMPLATE AND STYLE RULES
Copy this file to docs/<block>/week-NN-<slug>.md and replace every <...>.
Delete this comment block in the copy.

THE PATTERN: every concept section is IDEA -> EXAMPLE -> TRANSFER
  1. The idea, in plain words. It must be true on any dataset, not just Olist.
  2. !!! olist "In our example"    the running example, with real numbers
  3. Elsewhere line (optional)     one sentence from another domain
  4. !!! project "In your project" the question to ask of your own data
  Not every section needs 3 and 4. Use them where they help transfer.

STRUCTURE
  - Section headings name the idea, never the dataset
    ("Define the target precisely", not "What counts as late?")
  - The At a glance box always names the running example and links the block index
  - The closing sequence never changes: Lab, Project step, Common mistakes,
    Check yourself, Quick reference, Summary, Resources

CONTENT
  - A general claim must hold outside Olist. Olist numbers live only in olist boxes
  - Every number is real, copied from the executed solution notebook
  - Every figure caption states the takeaway, not the axes
  - About 60% idea, 40% example. If an example box outgrows the idea above it,
    the extra belongs in the notebook
  - Check yourself: mix Olist questions with at least one transfer question
    set in a different domain

VOICE
  - Second person, plain words, short sentences, concrete verbs
  - Explain why before how
  - No em dashes, no filler, no hype

CALLOUTS: one meaning per shape
  !!! olist "In our example"     running example
  !!! project "In your project"  apply to your own data
  !!! note "Key insight"         the one thing to remember from a section
  !!! warning "..."              a common trap
  !!! danger "..."               something that silently ruins results
  ??? question "..."             check yourself, answer collapsed
  !!! example "Lab · ..."        the lab box

DIVISION OF LABOUR
  Page     = portable ideas, Olist as illustration
  Notebook = Olist in full detail
  Project  = transfer to the team's own data

FIGURES
  scripts/figures/weekNN_figures.py --labs <path to ml-course-labs>
  Import checkpoints.py from the labs repo so figures match the notebooks.
  Save light and dark variants into docs/assets/images/<block>/
-->

# Week NN · <Title>

!!! abstract "At a glance"
    **Block:** <N · Block name>
    **Running example:** Olist orders. *Will this order arrive late?* New to it? Start with the [Block N overview](index.md).
    **Lab:** [`week-NN/lab.ipynb`](https://github.com/evisp/ml-course-labs/blob/main/week-NN/lab.ipynb) in the labs repository
    **Before class:** read sections <x, y, z>, about fifteen minutes

## Why this matters

> <One sentence that names the failure this week prevents.>

<Two short paragraphs: what goes wrong without this, and what this week does about it.>

## Learning outcomes

By the end of this week you can:

- [ ] <Verb-led outcome, true on any dataset>
- [ ] <...>
- [ ] <...>

## Before class

!!! question "Bring an answer"
    <A question students can answer from their own experience, before any reading.>

---

## 1. <The idea, named as an action>

<The general idea. What it is, why it goes wrong, and the checklist or pattern that
applies to any dataset. This part carries the lesson.>

!!! olist "In our example"
    <Olist, with real numbers from the solution notebook. A table, a snippet, or a figure.>

    ![<Alt text>](../assets/images/<block>/wNN-<name>-light.png#only-light)
    ![<Alt text>](../assets/images/<block>/wNN-<name>-dark.png#only-dark)

    *<Caption stating the takeaway.>*

*Elsewhere:* <one sentence showing the same idea in a different domain.>
{ .elsewhere }

!!! note "Key insight"
    <Only if the section has one thing that must stick.>

!!! project "In your project"
    <The question to ask of your own data. Concrete enough to act on today.>

## 2. <Next idea>

<...>

---

## Lab

!!! example "Lab · `week-NN/lab.ipynb`"
    In the [labs repository](https://github.com/evisp/ml-course-labs).

    1. `git pull`, open `week-NN/lab.ipynb`, and save your own copy as `my-lab.ipynb`
    2. <step>
    3. <step>

    **Check cells** tell you as you go whether each part is right. The complete solution appears the same evening.

## Project step

!!! project "For your Project N dataset"
    - <What lands in the team's repository this week>
    - <...>
    - Commit it before moving on

## Common mistakes

!!! warning "What goes wrong in week NN"
    - **<Mistake>.** <Why it happens, and what it costs.>
    - **<Mistake>.** <...>

## Check yourself

??? question "<Question set on Olist>"
    <Answer.>

??? question "<Transfer question set in a different domain>"
    <Answer.>

## Quick reference

| Idea | In one line |
|---|---|
| <idea> | <line> |

```python
# the few lines of code worth remembering from this week
```

## Summary

<One paragraph recapping the ideas, not the Olist steps.>

**Next week** <the question this week leaves open>.

**Next:** [Week NN · <Title>](<next-week-file>.md)

## Resources

- [<Title>](<url>). <Why it is worth reading.>

!!! quote
    <A closing line worth remembering.>
