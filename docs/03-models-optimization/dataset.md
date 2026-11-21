# The dataset · what we settled, what you decide

!!! abstract "At a glance"
    **Block:** 2 · Models & Optimization
    **Running example:** two Portuguese hotels, 119,390 bookings, arrivals July 2015 to August 2017
    **Notebook:** [`block-2-data/notebook.ipynb`](https://github.com/evisp/ml-course-labs/blob/main/block-2-data/notebook.ipynb) in the labs repository
    **Data:** `python data/download.py --hotels`
    **Before class:** sections 1 to 3, about ten minutes

## Why this page exists

Block 1 and Project 1 settled the question of whether you can do the data half. You can. You framed a question, built a table you could defend, split it so the model was judged on a future it had not seen, and wrote down what you had decided. Several of you built websites to show it.

This block is about something else. It asks what a model is actually doing when it fits, how it finds its answer, when that search fails, and what stops it memorising instead of learning. Those questions need steady ground underneath them. If every lab re-derived its own cleaning, five weeks of numbers would stop being comparable, and the week-to-week comparisons are the whole point.

So the data half is done once, here, in the open. Nothing is hidden, and the notebook shows every decision being made. But from Week 5 onwards, `hotels.py` hands you the same table every time.

That does not mean every question is closed. Some decisions are settled because the block needs them fixed. Others are left open on purpose, because they are judgement calls and arguing about them is useful. Section 8 says which are which.

## 1. What one row is

One row is **one booking**, made at one moment, for one future stay at one of two hotels: a city hotel in Lisbon and a resort in the Algarve. It records what the guest asked for, how they booked it, and what happened.

The file has 119,390 rows and 32 columns, published alongside a paper so the provenance is citable.

!!! hotel "The columns, in four families"
    **Who is coming** — `adults`, `children`, `babies`, `country`, `is_repeated_guest`, `previous_cancellations`, `previous_bookings_not_canceled`

    **What they asked for** — `hotel`, `arrival_date_*`, `stays_in_weekend_nights`, `stays_in_week_nights`, `meal`, `reserved_room_type`, `required_car_parking_spaces`, `total_of_special_requests`

    **How they booked it** — `lead_time`, `market_segment`, `distribution_channel`, `agent`, `company`, `deposit_type`, `customer_type`, `adr`

    **What happened afterwards** — `is_canceled`, `assigned_room_type`, `booking_changes`, `days_in_waiting_list`, `reservation_status`, `reservation_status_date`

That fourth family is the one to watch, and section 3 is about it.

## 2. The two questions

The block runs two tracks on the same table. Half the room answers one, half the other, and in Week 8 you compare.

| | The question | Target | Rows | What a model must beat |
|---|---|---|---|---|
| **A** | What will this booking pay per night? | `adr`, in euros | 117,396 | predicting the mean: **€29.92** average error |
| **B** | Will this booking be cancelled? | `is_canceled`, 0 or 1 | 118,564 | guessing: **lift 1.00**, at a 38.6% base rate |

Both come out of `hotels.py` ready to use:

```python
import sys; sys.path.insert(0, "..")
import hotels

df = hotels.block_2()           # cleaned, split, with the derived columns
rate = hotels.daily_rate(df)    # track A, with a `target` column
cancel = hotels.cancellation(df)  # track B, with a `target` column
```

They are not two halves of the same lesson. They disagree, usefully. Cancellation has the dramatic leak and the imbalance; the nightly rate has the clearest gap between a straight line and a tree. Neither group will see the whole picture alone, which is why Week 8 puts you back together.

## 3. What exists at the moment of booking

The moment of prediction is the moment the booking is made. Everything after that is the future.

Five columns in the file describe that future, and one of them is the target in a disguise.

!!! danger "`reservation_status` is the answer"
    It takes three values: *Canceled*, *Check-Out*, *No-Show*. A booking with status *Canceled* has `is_canceled = 1`. Always. There is no noise in the relationship at all, because they are the same fact written twice.

    Leave it in and a boosted model scores **PR AUC 1.000, ROC AUC 1.000, accuracy 1.000**. Three perfect scores, no warning, no error.

    The notebook does exactly this, on purpose, before throwing the column away. It is worth seeing a perfect score once so you learn to distrust one.

There is a second one, quieter, and it is the better lesson.

!!! danger "`required_car_parking_spaces` cannot be what it says it is"
    It reads like a request made at booking, and the column name encourages
    you to believe that. But of the **7,416 bookings that record a parking
    space, exactly zero were cancelled** — and the same holds in every split
    after cleaning: 4,696 in training, 857 in validation, 1,840 in test, zero
    cancellations in all three.

    No honest booking-time feature behaves like that. A space is assigned when
    the guest arrives, and a cancelled booking never arrives. The column
    records an outcome, not a request.

    It costs about 0.01 PR AUC to remove, so nothing in this block depends on
    it. What it costs to *keep* is a model that cannot work in production,
    because at the moment you need a prediction the column is always zero.

The giveaway was a count, not a score: a feature that is right 7,416 times out
of 7,416 is not a feature. When a column looks too good, group by it and count
before you celebrate.

`hotels.py` removes six columns from both questions:

| Column | Why it is not available |
|---|---|
| `reservation_status` | is the target, renamed |
| `reservation_status_date` | is when that status was set |
| `assigned_room_type` | decided at check-in, not at booking |
| `booking_changes` | accumulates after the booking is made |
| `days_in_waiting_list` | known only once the wait is over |
| `required_car_parking_spaces` | assigned on arrival — see above |

`adr` is a borderline case worth arguing about. The nightly rate is agreed when the booking is made, so track B is allowed to use it. Track A is predicting it, so it goes.

**Elsewhere:** a `closed_date` on a support ticket, a `final_invoice_amount` on an order, a `churn_reason` on an account.

## 4. What we removed, and what we left

The cleaning is deliberately short. Three rules, 826 rows:

| Rule | Removed | Remaining |
|---|--:|--:|
| nobody in the booking | 180 | 119,210 |
| no nights booked | 645 | 118,565 |
| a negative nightly rate | 1 | 118,564 |

None of these is a judgement call. A booking with no guests in it, or no nights in it, or a price below zero, is a recording error whichever question you are answering. One recording habit is also fixed: `meal` writes self-catering as both `SC` and `Undefined`, so `Undefined` becomes `SC`.

Everything debatable was left in, including things that look wrong:

- **1,959 bookings with a nightly rate of exactly zero.** Complimentary stays, staff rooms, some group allocations. They are real bookings, so track B keeps them. Track A leaves them out, because *what will this pay* is a different question from *will this be free*.
- **One booking at €5,400 a night.** Possibly real, possibly a typo. `daily_rate()` keeps rates between €1 and €1,000 and loses 1,968 rows doing it.
- **Four bookings with `children` missing.** Four. The pipeline's imputer handles them; nothing needs a special case.
- **Two `Undefined` market segments and five `Undefined` channels.** Rare enough to live with.

![The nightly rate, as recorded and inside a sane range](../assets/images/03-models-optimization/b2d-adr-light.png#only-light)
![The nightly rate, as recorded and inside a sane range](../assets/images/03-models-optimization/b2d-adr-dark.png#only-dark)

*Left, every rate in the file on a log scale: a spike at zero, a long thin tail, one booking at €5,400. Right, the same data between €1 and €1,000, which is the shape a model can work with.*

## 5. The split

Train on bookings made before October 2016. Validate on the three months after that. Test once, on everything booked in 2017.

![The three periods, their size and their cancellation rate](../assets/images/03-models-optimization/b2d-splits-light.png#only-light)
![The three periods, their size and their cancellation rate](../assets/images/03-models-optimization/b2d-splits-dark.png#only-dark)

*77,385 bookings train, 14,770 validate, 26,409 test. The cancellation rate is 38.6%, 39.9% and 31.8% — the world moves between the periods, as it did on Olist.*

Two things about this split are worth a minute each.

**It splits on the booking date, not the arrival date.** A booking made in September 2016 for an arrival the following summer belongs in training, because September 2016 is when we would have known about it. That means arrival periods overlap across the splits even though booking periods do not. If you split on arrival instead — which is the obvious thing to do, and wrong — you train on bookings that were made *after* some of the bookings you are predicting.

**The early months are not comparable.** The first arrival in the file is July 2015, so a booking recorded in January 2015 must have been made at least six months ahead. Long-lead bookings cancel far more often, so the left edge of the chart below reads like a catastrophe and is really an artefact of where the file starts.

![Cancellation rate by the month the booking was made](../assets/images/03-models-optimization/b2d-over-time-light.png#only-light)
![Cancellation rate by the month the booking was made](../assets/images/03-models-optimization/b2d-over-time-dark.png#only-dark)

*The shaded region holds only bookings made before the first arrival in the file, so it is all long-lead and not comparable with the rest.*

## 6. What the data says before any model touches it

Three findings worth carrying into Week 5.

**Lead time is the backbone.** How far ahead a booking is made predicts cancellation almost on its own, and it does so monotonically.

![Cancellation rate by how far ahead the booking was made](../assets/images/03-models-optimization/b2d-leadtime-light.png#only-light)
![Cancellation rate by how far ahead the booking was made](../assets/images/03-models-optimization/b2d-leadtime-dark.png#only-dark)

*From 9.7% for bookings made in the last week to 67.7% for those made more than a year ahead. Six buckets, no reversals.*

**One category is almost a perfect predictor, and it runs backwards.** Non-refundable bookings are cancelled **99.4% of the time**, across 14,587 of them.

![Cancellation rate by deposit type and by market segment](../assets/images/03-models-optimization/b2d-segments-light.png#only-light)
![Cancellation rate by deposit type and by market segment](../assets/images/03-models-optimization/b2d-segments-dark.png#only-dark)

*Non-refundable bookings almost always cancel. Guests booked through group channels cancel at 61%, direct bookers at 16%.*

That is not a leak — the deposit type is agreed at booking, so it is honestly available. But it should bother you, because it is the opposite of what a deposit is supposed to do. Something about how this hotel records non-refundable bookings is not what the column name suggests. The data cannot tell you what; you would have to go and ask. Keep it, use it, and put a line in your model card saying you do not know why it behaves this way.

**Three categorical columns are very wide, and one is nearly empty.**

![How much of the data the commonest categories cover](../assets/images/03-models-optimization/b2d-cardinality-light.png#only-light)
![How much of the data the commonest categories cover](../assets/images/03-models-optimization/b2d-cardinality-dark.png#only-dark)

*`country` has 177 values but 23 of them cover 95% of bookings. `agent` has 334 and needs 79. `company` has 348 and needs **two**, because 94% of bookings have no company at all.*

Week 3's encoding decisions are live again, on a dataset that did not exist when you learned them.

## 7. The floor to beat

Every model in this block gets compared to these. They come from the training rows only.

=== "Track A · the nightly rate"

    | | |
    |---|---|
    | **Baseline** | predict the training mean, €97.37, for every booking |
    | **On validation** | R² 0.000, average error **€29.92** |
    | **A plain linear model** | R² 0.378, average error €23.89 |

=== "Track B · cancellation"

    | | |
    |---|---|
    | **Baseline** | the base rate, 38.6% of training bookings cancelled |
    | **On validation** | PR AUC 0.386, **lift 1.00** |
    | **Logistic regression** | PR AUC 0.845, **lift 2.12** |

Report lift next to PR AUC for track B, because the base rate moves between the periods — 38.6% in training, 31.8% in test — and a raw PR AUC from one period cannot be compared with one from another.

## 8. What is yours to decide

Settled for the whole block, so that weeks compare: what one row is, the two targets, which columns exist at booking, the three cleaning rules, the split dates, and the baselines above.

Open, and yours:

- **How to encode the wide columns.** One-hot on 177 countries costs you 177 columns. Group the rare ones? Target-encode, cross-fitted, the way Week 3 did? Drop `company` since it is 94% empty, or keep the fact that it is empty?
- **What to derive.** `hotels.py` gives you `total_nights`, `total_guests`, and numeric month, week and day. A ratio of previous cancellations to previous stays, a weekend-arrival flag, lead-time buckets — those are yours.
- **What to do with the odd rows** that cleaning deliberately left in.
- **Everything from Week 5 onwards.** The model, how it is fitted, how it is held back, and how you choose between candidates.

Write your choices down as you make them. Project 2 asks you to defend them.

## Quick reference

| | |
|---|---|
| Get the data | `python data/download.py --hotels` |
| Start a lab | `import hotels; df = hotels.block_2()` |
| Work faster | `hotels.block_2(sample=20_000)` — 20,000 rows per split |
| Track A | `hotels.daily_rate(df)` — `target` is euros per night |
| Track B | `hotels.cancellation(df)` — `target` is 0 or 1 |
| Just the agreed columns | `hotels.features(df)` |
| The floor | `hotels.baseline(train, valid, task="rate")` or `task="cancellation"` |
| See the cleaning | `hotels.clean_bookings(raw, log=True)` |
| The split | before Oct 2016 trains · Oct–Dec 2016 validates · 2017 tests |

## Where the data comes from

Antonio, N., de Almeida, A. and Nunes, L. (2019). *Hotel booking demand datasets.* **Data in Brief** 22, 41–49. [doi:10.1016/j.dib.2018.11.126](https://doi.org/10.1016/j.dib.2018.11.126) · CC BY 4.0

Two hotels in Portugal, one city and one resort, with arrivals between 1 July 2015 and 31 August 2017. Personally identifying fields were removed by the authors before publication. The course serves it as a parquet file from the `data-v3` release of the labs repository; the content is unchanged from the published CSV.
