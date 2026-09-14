# Machine Learning — UMT

Course materials for the third-year Bachelor Machine Learning course at
University Metropolitan Tirana. Built with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/).

**Live site:** https://evisp.github.io/ml-course-umt/

## Local development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
mkdocs serve
```

Open <http://127.0.0.1:8000>. Pages reload on save.

## Structure

| Path | Contents |
|---|---|
| `docs/00-course/` | Syllabus, schedule, assessment |
| `docs/01-toolkit/` | Setup and prerequisite material |
| `docs/02-data-pipeline/` | Block 1 — weeks 1–4 |
| `docs/03-models-optimization/` | Block 2 — weeks 5–9 |
| `docs/04-representation-systems/` | Block 3 — weeks 10–14 |
| `docs/05-projects/` | Project specs and rubrics |
| `docs/06-reference/` | Topic-based reference material |
| `templates/week-template.md` | Skeleton every week page follows |

## Writing conventions

- Every week page follows `templates/week-template.md`.
- Images go in `docs/assets/images/<section>/` — never hotlinked.
- Callouts use Material admonitions: `!!! note`, `!!! warning`, `!!! example`, `??? tip` (collapsible).
- Math uses MathJax: `\( inline \)` and `\[ display \]`.

## Deployment

Pushing to `main` triggers `.github/workflows/deploy.yml`, which builds and
publishes to the `gh-pages` branch.
