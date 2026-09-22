# Project 1 · Raw data to a validated baseline

<p class="block-sub">One city, four questions.</p>

!!! abstract "At a glance"
    **Teams:** three people, one question per team
    **When:** Weeks 1 to 4, presented in the Week 4 Defend hour
    **Worth:** 20 points
    **Data:** New York yellow taxi trips, May to July 2026
    **Models:** linear or logistic regression, and a single decision tree

In class, Block 1 works through one question on Olist, one stage a week. This project asks your team to do the same four stages on data you have never seen, where every decision is yours to make and to defend. Four teams share one dataset, each with a different question, and in Week 4 you present what you found to the others.

---

## The data { .section-label }

Every yellow taxi trip in New York is recorded by the meter and published by the city's [Taxi and Limousine Commission](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page). You get a fixed sample: **200,000 trips from each of May, June and July 2026**, identical for every team, and **raw on purpose**. Deciding what to keep, fix, flag or drop is part of the grade.

| File | What it holds |
|---|---|
| `yellow_tripdata_2026_sample.parquet` | 600,000 trips, one row each, all 21 original columns |
| `taxi_zone_lookup.csv` | The name and borough of each of the 265 zone numbers |
| `taxi_zones.zip` | Zone boundaries, for maps |
| `data_dictionary_trip_records_yellow.pdf` | The official meaning of every column and code |

**Get it:** add the script below to your repository as `data/get_data.py`, then run `python data/get_data.py`. Anyone who clones your repository can do the same, which is what your README needs. `data/raw/` is already excluded from Git by the [repo conventions](../01-toolkit/repo-conventions.md).

??? example "The download script, `data/get_data.py`"
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

    If you have the labs repository, `python data/download.py --taxi` fetches the same files.

**Load it:**

```python
import pandas as pd

trips = pd.read_parquet("data/raw/yellow_tripdata_2026_sample.parquet")
zones = pd.read_csv("data/raw/taxi_zone_lookup.csv")

pickup_zones = zones.rename(columns={"LocationID": "PULocationID", "Borough": "pickup_borough", "Zone": "pickup_zone"})
trips = trips.merge(pickup_zones[["PULocationID", "pickup_borough", "pickup_zone"]], on="PULocationID", how="left")
```

??? info "Columns and codes you will use most"
    | Columns | Meaning |
    |---|---|
    | `tpep_pickup_datetime`, `tpep_dropoff_datetime` | When the meter was engaged and disengaged |
    | `PULocationID`, `DOLocationID` | Pickup and drop-off zone, 1 to 265 |
    | `trip_distance` | Miles, measured by the meter during the trip |
    | `passenger_count` | Entered by the driver |
    | `RatecodeID` | The rate in effect at the end of the trip |
    | `payment_type` | How the trip was paid |
    | `fare_amount` | The time-and-distance fare from the meter |
    | `tip_amount` | Tips, for card payments only |
    | `extra`, `mta_tax`, `tolls_amount`, `improvement_surcharge`, `congestion_surcharge`, `Airport_fee`, `cbd_congestion_fee` | Surcharges and fees |
    | `total_amount` | Everything charged, including the tip |

    | `payment_type` | | `RatecodeID` | |
    |--:|---|--:|---|
    | 0 | Flex fare trip | 1 | Standard rate |
    | 1 | Credit card | 2 | JFK |
    | 2 | Cash | 3 | Newark |
    | 3 | No charge | 4 | Nassau or Westchester |
    | 4 | Dispute | 5 | Negotiated fare |
    | 5 | Unknown | 6 | Group ride |
    | 6 | Voided trip | 99 | Unknown |

!!! note "Five facts to know before you start"
    - **`trip_distance` is measured during the trip, and `RatecodeID` is set at its end.** Neither is automatically available at booking.
    - **Cash tips are never recorded.** A cash trip always shows a tip of zero.
    - **A quarter of the trips are flex fare trips** (payment type 0), with no passenger count and no rate code.
    - **Zones 1, 132 and 138 are the airports** (Newark, JFK, LaGuardia). Zones 264 and 265 are unknown and outside New York.
    - **There are no exact locations**, only zones. The shapefile's coordinates are in feet, not latitude and longitude.

The split is the same for every team, so results can be compared: trips picked up in **May** for training, **June** for validation and every choice, and **July** for one final test.

---

## Your team's task { .section-label }

Each team owns one question, allocated in Week 1. Choose your team's tab. Everything in it is the minimum expected: going further, carefully, is welcome.

=== "A · The fare"

    ### What will this trip cost?

    **Type:** regression · **Predicted at:** booking · **Target:** `fare_amount`

    A booking app wants to show a price before the trip starts. Your model is that price.

    **Define the target.** `fare_amount` is the meter's fare, not what the passenger pays in total. Decide which trips belong in your question: airport flat fares and negotiated fares follow different rules from the meter. Write down each decision and how much data it removes.

    **The moment of prediction.** At booking you know the pickup time, the two zones, and the planned route. Treat `trip_distance` as the planned route's length, and say so in `PROBLEM.md`. You do **not** know the drop-off time, the duration, the tip, the total, or any fee settled at the end.

    **The analysis expected**

    - The fare against the distance: how much of the fare does distance alone explain?
    - The fare per mile by hour of the day and by borough. Where and when is a mile more expensive, and why?
    - Airport trips and very short trips: where do they sit, and do they follow the same pattern?
    - The strangest fares: very high fares for short trips, zero or negative fares. Explain or remove them, in writing.

    **The baseline ladder**

    1. The median fare of May, for every trip
    2. A rule a person could write: a fixed charge plus a fixed price per mile
    3. A decision tree two levels deep

    **Models and evaluation**

    - Linear regression and a decision tree, judged on June
    - MAE and RMSE against the median baseline, with a bootstrap interval on July
    - Errors by slice: borough, airport or not, hour of day, distance band
    - **The decision:** a customer is quoted your prediction plus a buffer. How large must the buffer be for the real fare to come in under the quote on 90% of trips?

    **Watch out for:** the meter also charges for time spent in slow traffic, and at booking you cannot know how long the trip will take. Look for where that hurts your predictions.

    !!! success "A strong project"
        Reads its linear model's coefficients as a price per mile and a starting charge, and compares them with the [official taxi fares](https://www.nyc.gov/site/tlc/passengers/taxi-fare.page). Shows exactly which trips the quote fails for, and why.

=== "B · The duration"

    ### How long will this trip take?

    **Type:** regression · **Predicted at:** pickup · **Target:** minutes from pickup to drop-off

    A passenger has just got into the car and wants to know when they will arrive. Your model is that estimate.

    **Define the target.** Compute the duration from the two timestamps. Decide which durations are real: zero or negative ones, trips of several hours, and trips of a few seconds all exist. Write down each decision and how much data it removes.

    **The moment of prediction.** At pickup you know the time, the two zones, and the planned route: treat `trip_distance` as the planned route's length, and say so. You do **not** know the drop-off time, the fare, the tip, the total, or any fee settled at the end.

    **The analysis expected**

    - Duration against distance: how far does distance alone get you?
    - Average speed by hour of the day and day of the week. When is New York slowest?
    - Speed by pickup zone or borough, and for airport trips
    - The long tail: the trips that took far longer than their distance suggests

    **The baseline ladder**

    1. The median duration of May, for every trip
    2. A rule: the distance divided by a typical speed
    3. A decision tree two levels deep

    **Models and evaluation**

    - Linear regression and a decision tree, judged on June
    - MAE and RMSE against the median baseline, with a bootstrap interval on July
    - Errors by slice: hour of day, borough, distance band, airport or not
    - **The decision:** the app shows an arrival time with a buffer. How large must it be for 90% of passengers to arrive before the time shown?

    **Watch out for:** the fare. The meter charges for time, so `fare_amount` contains the answer you are predicting. So do several other columns settled at the end of the trip.

    !!! success "A strong project"
        Shows, with its residuals, exactly where a straight line fails for travel time, and explains why in terms of the city: the hours and places where traffic behaves differently.

=== "C · The crawl"

    ### Will this trip crawl?

    **Type:** classification · **Predicted at:** pickup · **Target:** average speed under 6 miles per hour

    A dispatcher wants to warn passengers whose trip is likely to crawl through traffic. Your model decides who gets the warning.

    **Define the target.** Average speed is distance divided by duration, and a trip is positive if it is under 6 mph. Decide which trips can be labelled at all: zero distances and tiny durations make the speed meaningless. Write down each decision, and the positive rate after each one.

    **The moment of prediction.** At pickup you know the time, the two zones, and the planned route. Your target is built from the distance *and the duration*, both measured during the trip. The duration, the drop-off time, and anything settled at the end are forbidden. The planned distance is allowed, and your `PROBLEM.md` must say why.

    **The analysis expected**

    - The positive rate overall, and by hour of the day and day of the week
    - The positive rate by pickup zone. Draw it as a map with the zone shapefile.
    - Which trips crawl: short or long, within Manhattan or across boroughs, to or from airports?
    - Whether the positive rate is stable from May to June to July

    **The baseline ladder**

    1. Always predict "does not crawl"
    2. A rule a dispatcher could use, such as busy hours in the busiest zones
    3. A decision tree two levels deep

    **Models and evaluation**

    - Logistic regression and a decision tree, judged on June
    - Precision, recall, PR AUC and lift. Never accuracy alone.
    - A threshold chosen from costs you state: what does a missed crawl cost, and what does a needless warning cost?
    - A reliability check, results by slice, and July scored once with a bootstrap interval

    **Watch out for:** the target is made from two measurements of the future. Check every feature against your moment of prediction.

    !!! success "A strong project"
        Has a map that explains itself, a threshold whose costs are argued rather than assumed, and a model card that says plainly which trips the warning misses.

=== "D · The tip"

    ### Will this passenger tip well?

    **Type:** classification · **Predicted at:** payment · **Target:** a card tip of 25% of the fare or more

    A driver-support app wants to understand which trips end with a generous tip. Your model predicts it at the moment of payment.

    **Define the target.** A trip is positive if `tip_amount` is at least 25% of `fare_amount`. Decide who is in the question: cash tips are never recorded, so what does that do to your population? Decide what to do with zero fares, disputes and voided trips. Write down each decision, and the positive rate after each one.

    **The moment of prediction.** At the payment screen the trip is over: the fare, the duration, the distance, the zones and the times are all known. The tip is not, and neither is `total_amount`, which includes it.

    **The analysis expected**

    - The tip as a percentage of the fare. What shape is it, and what do its peaks tell you about how people tip?
    - The tip rate by payment type, and a clear demonstration of why cash trips cannot be in your data
    - The positive rate by fare, trip length, hour, day, airport or not, and number of passengers
    - Whether any of these differences are large enough to matter

    **The baseline ladder**

    1. Always predict the most common answer
    2. A rule, based on your analysis
    3. A decision tree two levels deep

    **Models and evaluation**

    - Logistic regression and a decision tree, judged on June
    - Precision, recall, PR AUC and lift. Never accuracy alone.
    - A threshold chosen from costs you state, a reliability check, results by slice, and July scored once with a bootstrap interval

    **Watch out for:** human generosity is hard to predict from a trip record. This question may have a lower ceiling than the others, and discovering how low, with evidence, is a real result.

    !!! warning "The most demanding question"
        This team gets extra guidance in class. A modest score, honestly measured and clearly explained, can earn full marks.

    !!! success "A strong project"
        Proves the cash leak, measures the ceiling of what trip data can say about tipping, and explains it in a model card that promises nothing it cannot deliver.

---

## Week by week { .section-label }

Each week's project step follows that week's class. By the end of the week your repository has:

| Week | Stage | In your repository |
|:--:|---|---|
| **[01](../02-data-pipeline/week-01-problem-framing.md)** | Frame | `PROBLEM.md`: the question in one sentence, the moment of prediction, the target's decisions, and the baseline ladder |
| **[02](../02-data-pipeline/week-02-data-quality.md)** | Split | A cleaning function that rebuilds the data from the raw files, a findings table with a fix, flag or drop decision for each problem, and the analysis from your tab |
| **[03](../02-data-pipeline/week-03-feature-engineering.md)** | Build | A pipeline that cannot leak, each feature judged on June, and the features that lost reported too |
| **[04](../02-data-pipeline/week-04-evaluation.md)** | Evaluate | The evaluation from your tab, July scored once, `MODEL_CARD.md`, a peer review, and the presentation |

**Every team** must also decide, and defend, what happens to the flex fare trips, the trips that cannot be real (zero distances, impossible durations, negative amounts, voided trips, unknown zones), and the non-standard fares.

---

## What to hand in { .section-label }

One GitHub repository per team, following the [repo conventions](../01-toolkit/repo-conventions.md):

| File | What it shows |
|---|---|
| `notebooks/01-frame.ipynb` | The question, the target and its decisions, the baseline ladder |
| `notebooks/02-clean-and-split.ipynb` | The audit, the cleaning decisions, the split, and the analysis |
| `notebooks/03-features.ipynb` | The features, the pipeline, and what each addition did on June |
| `notebooks/04-evaluate.ipynb` | The chosen model, the slices, the decision, and the one look at July |
| `data/get_data.py`, `src/` | The download, and the cleaning function and pipeline the notebooks import |
| `PROBLEM.md`, `MODEL_CARD.md`, `README.md` | The problem card, the model card, and how to run everything from a fresh clone |

**The presentation:** fifteen minutes in the Week 4 Defend hour. Your question, one decision you are proud of, one thing that did not work, and where your model fails. Any member may be asked to answer any question.

**Submission:** push before the deadline, and the last commit time counts. Make the repository public, or add the instructor as a collaborator.

**Peer review:** A reviews B, B reviews C, C reviews D, D reviews A. Clone the repository, follow the README exactly, and write what ran, what did not, and at least one real question about their method. The review you give counts towards your Craft points.

**Teams and AI:** the project grade is a team grade, adjusted by a private contribution rating at the end. If a teammate stops contributing, tell the instructor that week. AI assistants are allowed if you **declare** where you used them in your README, and every member can **explain** every line. Work nobody in the team can explain is handled under university regulations.

---

## How it is graded { .section-label }

| Criterion | Points | Full marks look like |
|---|:--:|---|
| **Method** | 8 | A precise target with its decisions written down, a moment of prediction respected by every feature, cleaning that never learns from the data, features judged on June, and July used once |
| **Execution** | 5 | The repository runs from a fresh clone, rebuilds everything from the raw data, and reports the numbers the code produces |
| **Communication** | 4 | A README a stranger can follow, and problem and model cards that state the uncomfortable results as plainly as the good ones |
| **Craft** | 3 | A clean layout, a commit history that shows the work as it happened, readable code, and a useful peer review |

!!! tip "What earns the points"
    The method, not the score. A modest result, honestly measured and clearly explained, can earn full marks. An impressive score that rests on a leak cannot.

??? question "Before you submit: the checklist"
    - [ ] A fresh clone runs from the README, from `python data/get_data.py` to the last notebook
    - [ ] `PROBLEM.md` states the target, the moment of prediction, the metric, and the baseline
    - [ ] No feature uses information from after your moment of prediction
    - [ ] Every learned step is fitted on May only, inside a pipeline
    - [ ] July was scored once, at the end, with a bootstrap interval next to the baseline
    - [ ] Results are reported by slice, with the number of trips in each
    - [ ] `MODEL_CARD.md` says where the model fails
    - [ ] The README declares any use of AI
    - [ ] The peer review is written and delivered

---

**See also:** [all projects](index.md) · [grading](../00-course/grading.md) · [repo conventions](../01-toolkit/repo-conventions.md)
