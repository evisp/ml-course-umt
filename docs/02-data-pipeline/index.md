# Block 1 · Data & the Pipeline

<p class="block-sub">A model is the easy part.</p>

Four weeks, and you will barely train a model. That is deliberate. Everything that quietly ruins a machine learning project goes wrong before training starts, and none of it throws an error. A bad split or a leaked feature does not crash your code. It hands you an excellent score and a system that fails the day it meets real data.

So this block builds the part that decides whether a score can be trusted: one pipeline, one stage a week.

<div class="roadmap-track">
  <div class="track-seg seg-1">
    <span class="track-weeks">Week 01</span>
    <b>Frame</b>
  </div>
  <div class="track-seg seg-2">
    <span class="track-weeks">Week 02</span>
    <b>Split</b>
  </div>
  <div class="track-seg seg-3">
    <span class="track-weeks">Week 03</span>
    <b>Build</b>
  </div>
  <div class="track-seg seg-4">
    <span class="track-weeks">Week 04</span>
    <b>Evaluate</b>
  </div>
  <div class="track-seg seg-project">
    <span class="track-weeks">End of block</span>
    <b>Project 1</b>
  </div>
</div>

## The running example { .section-label }

<div class="block-card" markdown>

<div class="block-head">
<span class="block-num">Olist · Brazilian e-commerce</span>
<span class="block-weeks">Used every week</span>
</div>

### Will this order arrive late?

<p class="block-sub">Predicted at the moment the customer clicks buy.</p>

Olist is a Brazilian marketplace that connects small shops to large online stores. In 2018 it released a real, anonymised record of its orders, and that is the data every lecture, figure, and lab in this block uses.

A late order is one of the surest ways to lose a customer. A prediction made at purchase time leaves room to act on it: warn the customer early, prioritise the shipment, choose a different carrier. That makes it a question a real company would pay to have answered, which is the only kind worth practising on.

<div class="chips chips-left">
<span class="chip">About 100,000 orders</span>
<span class="chip">Nine linked tables</span>
<span class="chip">2016 to 2018</span>
<span class="chip">Real mess, nothing planted</span>
</div>

</div>

??? info "How the nine tables connect"
    You will only need two of these in Week 1. Week 2 joins all nine, and one of the relationships below hides a trap you will meet there.

    ```mermaid
    erDiagram
        CUSTOMERS ||--|| ORDERS : "places"
        ORDERS ||--|{ ORDER_ITEMS : "contains"
        ORDERS ||--|{ PAYMENTS : "paid by"
        ORDERS ||--o{ REVIEWS : "receives"
        PRODUCTS ||--o{ ORDER_ITEMS : "appears in"
        SELLERS ||--o{ ORDER_ITEMS : "ships"
        CATEGORY_NAMES ||--o{ PRODUCTS : "translates"
        GEOLOCATION }o--o{ CUSTOMERS : "zip prefix"
        GEOLOCATION }o--o{ SELLERS : "zip prefix"

        ORDERS {
            string order_id PK
            string customer_id FK
            string order_status
            datetime order_purchase_timestamp
            datetime order_delivered_customer_date
            datetime order_estimated_delivery_date
        }
        CUSTOMERS {
            string customer_id PK
            string customer_unique_id
            string customer_state
        }
        ORDER_ITEMS {
            string order_id FK
            string product_id FK
            string seller_id FK
            float price
            float freight_value
        }
    ```

    The data is the [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce), shared under CC BY-NC-SA 4.0.

## Four ways a score can lie { .section-label }

Each week closes one of them. By the end of the block, a score you report has survived all four.

<div class="grid cards" markdown>

-   :material-ruler:{ .lg .middle } **Week 01 · Problem framing & baselines**

    ---

    **The lie: "it beats nothing."** A 95% score means nothing until you know what always guessing the most common answer would have scored.

    **The defence:** a precisely defined target, and a ladder of baselines before any real model.

    [:octicons-arrow-right-24: Week 01](week-01-problem-framing.md)

-   :material-call-split:{ .lg .middle } **Week 02 · Data quality & splitting**

    ---

    **The lie: "the test set was unseen."** Rows from the same customer, or from the future, sitting on both sides of the split.

    **The defence:** cleaning you can repeat, and a split that matches how the model will actually be used.

    [:octicons-arrow-right-24: Week 02](week-02-data-quality.md)

-   :material-pipe-leak:{ .lg .middle } **Week 03 · Feature engineering**

    ---

    **The lie: "the features are fair."** A column recorded after the prediction was made, or a scaler that quietly saw the test set.

    **The defence:** features built only from what is known at prediction time, inside a pipeline that cannot leak.

    [:octicons-arrow-right-24: Week 03](week-03-feature-engineering.md)

-   :material-magnify:{ .lg .middle } **Week 04 · Evaluation & error analysis**

    ---

    **The lie: "the average is fine."** A respectable overall score that is poor for exactly the customers who matter most.

    **The defence:** a metric chosen for the cost of being wrong, and error analysis slice by slice.

    [:octicons-arrow-right-24: Week 04](week-04-evaluation.md)

</div>

## What you build { .section-label }

Every week leaves something concrete in your repository. Together they are most of Project 1.

| Week | By the end of the week, your repo has |
|:--:|---|
| **01** | A problem card stating exactly what you predict, when, and why, plus a baseline ladder |
| **02** | A cleaning step anyone can rerun, and a split with its reasoning written down |
| **03** | A preprocessing pipeline that cannot leak, whatever you put through it |
| **04** | An error analysis broken down by slice, and a short model card |

## Skills you leave with { .section-label }

<div class="chips chips-left">
<span class="chip">Frame a problem</span>
<span class="chip">Split without leaking</span>
<span class="chip">Engineer features</span>
<span class="chip">Evaluate honestly</span>
</div>

## How the labs work { .section-label }

<div class="beats">
  <div class="beat">
    <span class="beat-time">Week 01</span>
    <b>Clone once</b>
    <p>The labs repository holds every notebook and the script that fetches the Olist data.</p>
  </div>
  <div class="beat">
    <span class="beat-time">Before each lab</span>
    <b>Pull</b>
    <p>Run <code>git pull</code> to get that week's notebook. It arrives with gaps for you to fill in class.</p>
  </div>
  <div class="beat">
    <span class="beat-time">After each lab</span>
    <b>Compare</b>
    <p>The complete, narrated solution appears the same evening. Compare it with what you wrote.</p>
  </div>
</div>

!!! tip "Missed a week? You are not locked out"
    Each lab starts from a checkpoint file produced by the previous week's solution. You can pick up the story at any week without having finished the one before it.

## Where it leads { .section-label }

<div class="principle" markdown>

**Project 1: the same four stages, on a different dataset.**

The class works on Olist together. Your team then applies every stage to data you have not seen in class, which is where you find out whether you understood the idea or only followed the notebook.

</div>

[Project 1 brief](../05-projects/project-1-pipeline.md){ .block-project }

---

**Before you start:** make sure the [toolkit](../01-toolkit/index.md) readiness checklist is done. Then go to [Week 01](week-01-problem-framing.md).
