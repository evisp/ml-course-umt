# Project 1 · Raw data to a validated baseline

<p class="block-sub">One city, four questions.</p>

!!! abstract "At a glance"
    **Teams:** three people, one question per team
    **When:** Weeks 1 to 4, presented in the Week 4 Defend hour
    **Worth:** 20 points
    **Data:** New York yellow taxi trips, May to July 2026
    **Models:** linear or logistic regression, and a single decision tree

In class, Block 1 works through one question on Olist, one stage a week. This project asks your team to do the same four stages on data you have never seen, where every decision is yours to make and to defend.

Four teams share one dataset, and each owns a different question about it. In Week 4 you present what you found to the teams who spent a month on the same data, asking something else.

---

## The data { .section-label }

Every yellow taxi trip in New York is recorded by the meter and published by the city's [Taxi and Limousine Commission](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page). You get a fixed sample: **200,000 trips from each of May, June and July 2026**, 600,000 in total, identical for every team.

!!! warning "The sample is raw, on purpose"
    Nothing has been cleaned or removed. Deciding what to keep, fix, flag or drop is part of the project, and part of the grade.

| File | What it holds |
|---|---|
| `yellow_tripdata_2026_sample.parquet` | The 600,000 trips, one row per trip, all 21 original columns |
| `taxi_zone_lookup.csv` | The name and borough of each of the 265 zone numbers |
| `taxi_zones.zip` | Zone boundaries, for drawing maps |
| `data_dictionary_trip_records_yellow.pdf` | The official meaning of every column and code |

### Get it

Add this script to your repository as `data/get_data.py`. Anyone who clones your repository then gets the data with one command, which is exactly what your README needs.

```python
"""Download the Project 1 data into data/raw/. Run from the repository root:
    python data/get_data.py
"""
import urllib.request
import zipfile
from pathlib import Path

BASE = "https://github.com/evisp/ml-course-labs/releases/download/data-v2/"
FILES = [
    "yellow_tripdata_2026_sample.parquet",
    "taxi_zone_lookup.csv",
    "taxi_zones.zip",
    "data_dictionary_trip_records_yellow.pdf",
]

raw = Path(__file__).resolve().parent / "raw"
raw.mkdir(parents=True, exist_ok=True)

for name in FILES:
    if not (raw / name).exists():
        print(f"downloading {name}")
        urllib.request.urlretrieve(BASE + name, raw / name)

with zipfile.ZipFile(raw / "taxi_zones.zip") as zf:
    zf.extractall(raw)

print("ready:", sorted(p.name for p in raw.iterdir()))
```

`data/raw/` is already excluded by the `.gitignore` from the [repo conventions](../01-toolkit/repo-conventions.md), so the data never ends up in your commits. Parquet files need `pyarrow`, which is in the course requirements.

If you have the labs repository, `python data/download.py --taxi` fetches the same files into `data/raw/taxi/`.

### Load it

```python
import pandas as pd

trips = pd.read_parquet("data/raw/yellow_tripdata_2026_sample.parquet")
zones = pd.read_csv("data/raw/taxi_zone_lookup.csv")

pickup_zones = zones.rename(columns={"LocationID": "PULocationID", "Borough": "pickup_borough", "Zone": "pickup_zone"})
trips = trips.merge(pickup_zones[["PULocationID", "pickup_borough", "pickup_zone"]], on="PULocationID", how="left")
```

### What you need to know

The [data dictionary](https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_yellow.pdf) is the authority. These are the columns and codes you will use most.

| Columns | Meaning |
|---|---|
| `tpep_pickup_datetime`, `tpep_dropoff_datetime` | When the meter was engaged and disengaged |
| `PULocationID`, `DOLocationID` | Pickup and drop-off zone, a number from 1 to 265 |
| `trip_distance` | Miles, **as measured by the meter during the trip** |
| `passenger_count` | Number of passengers, entered by the driver |
| `RatecodeID` | The rate **in effect at the end of the trip** |
| `payment_type` | How the trip was paid |
| `fare_amount` | The time-and-distance fare from the meter |
| `tip_amount` | Tips, **for card payments only** |
| `extra`, `mta_tax`, `tolls_amount`, `improvement_surcharge`, `congestion_surcharge`, `Airport_fee`, `cbd_congestion_fee` | Surcharges and fees. `cbd_congestion_fee` is the congestion pricing charge in force since January 2025 |
| `total_amount` | Everything charged, **including the tip** |

| `payment_type` | | `RatecodeID` | |
|--:|---|--:|---|
| 0 | Flex fare trip | 1 | Standard rate |
| 1 | Credit card | 2 | JFK |
| 2 | Cash | 3 | Newark |
| 3 | No charge | 4 | Nassau or Westchester |
| 4 | Dispute | 5 | Negotiated fare |
| 5 | Unknown | 6 | Group ride |
| 6 | Voided trip | 99 | Unknown |

!!! note "Read these before you start"
    - **Cash tips are never recorded.** A cash trip always shows a tip of zero, whatever the passenger gave.
    - **A quarter of the trips are flex fare trips** (payment type 0), and those have no passenger count and no rate code.
    - **Zones 1, 132 and 138 are the three airports**: Newark, JFK and LaGuardia. Zones 264 and 265 mean "unknown" and "outside New York".
    - **There are no exact locations**, only zones, to protect passengers' privacy.
    - **The shapefile uses New York State Plane coordinates, in feet**, not latitude and longitude. Maps work fine. Distances computed from it are in feet.

The data comes from NYC Open Data, published by the New York City Taxi and Limousine Commission.

---

## Your question { .section-label }

Each team owns one question, allocated in Week 1.

| Team | Question | Type | Predicted at |
|:--:|---|---|---|
| **A** | **What will this trip cost?** The fare. | Regression | Booking |
| **B** | **How long will this trip take?** The duration in minutes. | Regression | Pickup |
| **C** | **Will this trip crawl?** An average speed under 6 miles per hour. | Classification | Pickup |
| **D** | **Will this passenger tip well?** A card tip of 25% or more of the fare. | Classification | Payment |

Each question is defined here in one line. Turning that line into a precise target, with every decision it hides, is your Week 1 work.

Question D is the most demanding of the four, and the D team gets extra guidance in class.

## The split { .section-label }

The split is the same for every team, so that results can be compared:

| Part | Trips picked up in | Used for |
|---|---|---|
| **Train** | May 2026 | Learning and exploring |
| **Validation** | June 2026 | Every choice you make |
| **Test** | July 2026 | One final score, once |

Your `PROBLEM.md` must still explain why a split by time is the right one for your question.

---

## What to do, week by week { .section-label }

Each week's project step follows that week's class. By the end of the week, your repository has:

| Week | Stage | In your repository |
|:--:|---|---|
| **[01](../02-data-pipeline/week-01-problem-framing.md)** | Frame | `PROBLEM.md`: your one-sentence question, the moment of prediction, every decision in your target with its effect on the data, and a baseline ladder |
| **[02](../02-data-pipeline/week-02-data-quality.md)** | Split | A cleaning function that rebuilds the clean data from the raw files; a findings table with a fix, flag or drop decision for each problem; at least four charts of the training month |
| **[03](../02-data-pipeline/week-03-feature-engineering.md)** | Build | A pipeline that cannot leak; each feature judged on validation; the features that lost, reported too |
| **[04](../02-data-pipeline/week-04-evaluation.md)** | Evaluate | Results by slice, a test score with a bootstrap interval, `MODEL_CARD.md`, a peer review of another team, and the presentation |

## Decisions you must make and defend { .section-label }

These run through every question, and they are where most of the method marks are.

- **The flex fare trips.** A quarter of the data, with missing fields. Keep them, drop them, or treat them separately?
- **Trips that cannot be real.** Zero distances, durations of zero or less, negative amounts, voided trips, unknown zones.
- **Non-standard fares.** Airport flat rates and negotiated fares follow different rules. In your data, or out?
- **The moment of prediction.** The distance is measured during the trip, and the rate code is set at its end. What does "predicted at booking" or "at pickup" allow you to use, and what does it forbid? Write the answer down, and follow it.
- **Every column settled after your moment.** The tip, the total amount, and many of the fees are only known when the trip ends. Any of them can leak.

## Models and evaluation { .section-label }

**Models:** linear regression or logistic regression, and a single decision tree. More powerful models arrive in Block 2. For now, the work is in the data and the method.

**Baselines:** a ladder, as in Week 1. For regression, the first rung predicts the median of the training month for every trip.

**Classification teams (C and D):**

- precision, recall and lift, never accuracy alone
- a threshold chosen from costs you state and justify
- a reliability check before anyone reads a score as a probability
- results by slice

**Regression teams (A and B):**

- mean absolute error and root mean squared error, against the median baseline
- a bootstrap interval around the test error
- errors broken down by slice, such as borough, airport trips, and hour of the day
- **a decision in regression form:** a customer is quoted your prediction plus a buffer. How large must the buffer be for the real fare, or the real trip time, to come in under the quote for 90% of trips? Choose it on validation, and check it on test.

---

## What to hand in { .section-label }

One GitHub repository per team, following the [repo conventions](../01-toolkit/repo-conventions.md), with four notebooks that tell the story in order:

| Notebook | What it shows |
|---|---|
| `notebooks/01-frame.ipynb` | The question, the target and its decisions, the baseline ladder |
| `notebooks/02-clean-and-split.ipynb` | The audit, the cleaning decisions, the split, and the charts of the training month |
| `notebooks/03-features.ipynb` | The features, the pipeline, and what each addition did on validation |
| `notebooks/04-evaluate.ipynb` | The chosen model on validation, the slices, the decision, and the one look at test |

Alongside them:

```text
data/get_data.py          downloads the data
src/                      the cleaning function and the pipeline, imported by the notebooks
PROBLEM.md                written in Week 1, updated if a decision changes
MODEL_CARD.md             written in Week 4
README.md                 how to run everything, from a fresh clone
requirements.txt
```

**The test for your repository:** a stranger clones it, follows the README, and every notebook runs from top to bottom, from the raw data to the final score.

**The presentation:** fifteen minutes in the Week 4 Defend hour. Your question, one decision you are proud of, one thing that did not work, and what your model card says about where the model fails. Any member of the team may be asked to answer any question.

**Submission:** push to GitHub before the deadline. The last commit time counts. Make the repository public, or add the instructor as a collaborator.

## Peer review { .section-label }

Before the deadline, each team reviews another team's repository:

<div class="outcomes">
  <div class="outcome"><b>A reviews B, B reviews C, C reviews D, and D reviews A.</b> Every team reviews a question it did not work on, so reviewing means reasoning about someone else's problem from scratch.</div>
  <div class="outcome"><b>Clone it, and follow the README exactly.</b> Does everything run? Where did you have to improvise?</div>
  <div class="outcome"><b>Write a short review:</b> what ran, what did not, and at least one real question about their method. A review that says "looks good" is worth nothing. A review that finds a leak is worth a lot.</div>
</div>

The review you give counts towards your Craft points.

## Working as a team { .section-label }

The project grade is a team grade: all three of you receive it. At the end, each member privately rates the contribution of the other two, and a member rated clearly below the rest can receive a reduced share. If a teammate stops contributing, tell the instructor in the week it happens, not after the deadline.

## AI and integrity { .section-label }

AI assistants are allowed, on two conditions:

- **Declare it.** Your README has a section saying where you used AI, and for what.
- **Understand it.** Every member must be able to explain every line in the repository. In the Defend hour, the instructor chooses who answers.

Copying another team's code, or presenting work nobody in the team can explain, is handled under university regulations.

---

## How it is graded { .section-label }

Twenty points, in four parts.

| Criterion | Points | Full marks look like |
|---|:--:|---|
| **Method** | 8 | A precise target with its decisions written down. A moment of prediction that is respected by every feature. Cleaning that never learns from the data. A split that fits the question. Features judged on validation, and test used once. |
| **Execution** | 5 | The repository runs from a fresh clone. The pipeline rebuilds everything from the raw data. The numbers reported are the numbers the code produces. |
| **Communication** | 4 | A README a stranger can follow, a problem card and a model card that state the uncomfortable results as plainly as the good ones, and notebooks that read as a story. |
| **Craft** | 3 | A clean repository layout, a commit history that shows the work as it happened, readable code, and a useful peer review given to another team. |

!!! tip "What earns the points"
    The method, not the score. A modest result, honestly measured and clearly explained, can earn full marks. An impressive score that rests on a leak cannot.

## Before you submit { .section-label }

- [ ] A fresh clone runs from the README, from `python data/get_data.py` to the last notebook
- [ ] `PROBLEM.md` states the target, the moment of prediction, the metric, and the baseline
- [ ] No feature uses information from after your moment of prediction
- [ ] Every learned step is fitted on May only, inside a pipeline
- [ ] July was scored once, at the end
- [ ] The test score has a bootstrap interval, next to the baseline
- [ ] Results are reported by slice, with the number of trips in each
- [ ] `MODEL_CARD.md` says where the model fails
- [ ] The README declares any use of AI
- [ ] The peer review is written and delivered

---

**See also:** [all projects](index.md) · [grading](../00-course/grading.md) · [repo conventions](../01-toolkit/repo-conventions.md)
