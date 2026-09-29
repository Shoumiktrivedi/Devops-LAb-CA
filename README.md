# Personal Expense Tracker — Containerized with Automated CI/CD

**Track. Analyze. Manage.**

A full-stack web app to record income and expenses, filter and search them, and see spending charts. Built with Flask + SQLite, packaged with Docker, and tested and built automatically by GitHub Actions.

## Problem statement
Many students and young professionals track spending in notebooks or scattered notes, which makes it hard to see where money goes. This project provides a simple, self-hosted tracker with summaries and charts, and demonstrates a modern DevOps workflow (containers + CI/CD) around it.

## Objectives
- Build a REST API with full CRUD and validation
- Store data with SQLAlchemy + SQLite
- Show summaries and charts in a responsive dashboard
- Automate testing with PyTest
- Containerize with Docker and Docker Compose
- Automate test and build on every push using GitHub Actions

## Features
Dashboard (income, expenses, balance, count, recent transactions, category doughnut chart, monthly bar chart) · Add / edit / delete transactions (with confirmation) · Filter by type, category and date range · Search by description or category · Default categories · Demo data loader · Responsive UI · Toast notifications · Client and server validation.

## Technology stack
| Layer | Tools |
|---|---|
| Frontend | HTML5, CSS3, vanilla JavaScript, Chart.js (bundled locally, works offline) |
| Backend | Python 3.12, Flask, Flask-CORS |
| Database | SQLite via SQLAlchemy (Flask-SQLAlchemy) |
| Testing | PyTest + Flask test client |
| DevOps | Docker, Docker Compose, GitHub Actions, Git/GitHub |

## System architecture
```
Browser (HTML/CSS/JS + Chart.js)
        │  fetch() JSON over HTTP
        ▼
Flask app (gunicorn)  ──  routes.py (HTTP)  →  services.py (validation, logic)  →  models.py (SQLAlchemy)
        │
        ▼
SQLite file  (/data/expenses.db  ← Docker volume "expense_data")
```

## Project structure
```
expense-tracker/
├── app/
│   ├── __init__.py      # app factory, config, DB creation
│   ├── database.py      # SQLAlchemy instance
│   ├── models.py        # Transaction model
│   ├── routes.py        # Blueprints: UI page + REST API
│   ├── services.py      # validation, queries, dashboard maths, demo data
│   ├── templates/index.html
│   └── static/{css/style.css, js/app.js, js/vendor/chart.umd.js}
├── tests/test_api.py
├── instance/            # local SQLite DB lives here (not in Git)
├── .github/workflows/ci-cd.yml
├── Dockerfile · docker-compose.yml · .dockerignore · .gitignore
├── requirements.txt · run.py · seed.py
└── docs/{REPORT.md, VIVA.md, screenshots/}
```

## Installation without Docker
```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python seed.py                    # optional demo data
python run.py
```
Open http://127.0.0.1:5000

## Running with Docker
```bash
docker compose up --build
```
Open http://localhost:5000. Demo data loads automatically on first start (`SEED_ON_START=true`). Data persists in the `expense_data` volume.
```bash
docker compose down            # stop (data kept)
docker compose down -v         # stop AND delete data
SEED_ON_START=false docker compose up --build   # start empty (Windows PowerShell: $env:SEED_ON_START="false"; docker compose up --build)
```

## Configuration (environment variables)
| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `sqlite:///instance/expenses.db` | Database location |
| `SECRET_KEY` | dev placeholder | Flask secret (set your own outside class demos) |
| `SEED_ON_START` | `false` (`true` in compose) | Load demo data when DB is empty |
| `HOST`, `PORT`, `FLASK_DEBUG` | `127.0.0.1`, `5000`, `0` | Used by `python run.py` |

## API documentation
| Method | Endpoint | Description | Success |
|---|---|---|---|
| GET | `/api/transactions` | List. Query: `type`, `category`, `start_date`, `end_date`, `search` | 200 |
| POST | `/api/transactions` | Create | 201 |
| GET | `/api/transactions/<id>` | Get one | 200 / 404 |
| PUT | `/api/transactions/<id>` | Update | 200 / 400 / 404 |
| DELETE | `/api/transactions/<id>` | Delete | 200 / 404 |
| GET | `/api/dashboard` | Totals, balance, chart data, recent 5 | 200 |
| GET | `/api/categories` | Category lists | 200 |
| POST | `/api/seed` | Add demo data if DB empty (`?reset=true` replaces all) | 201 / 200 |
| GET | `/api/health` | Health check | 200 |

Request body (POST/PUT):
```json
{"type": "expense", "amount": 250.5, "category": "Food", "description": "Lunch", "date": "2025-01-15"}
```
`type`, `amount`, `category`, `date` are required; `description` is optional (max 200 chars). Amount must be > 0 and category must belong to the chosen type.
Validation error (400): `{"error": "Validation failed", "details": {"amount": "Amount must be greater than zero"}}`

## Testing
```bash
pip install -r requirements.txt
pytest -v
```
21 tests cover startup, CRUD, validation (9 invalid cases), filters/search, dashboard totals, categories and seeding. Each test uses its own temporary database.

## CI/CD explanation
`.github/workflows/ci-cd.yml` runs on every push and pull request to `main`:
1. **test** — checkout, set up Python 3.12, install dependencies, run `pytest`. Failing tests fail the pipeline.
2. **docker** (after tests pass) — validate `docker-compose.yml`, build the image, start the container and call `/api/health`.
3. **publish** (optional, push to `main` only) — pushes to Docker Hub *only if* the repo secrets `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` exist; otherwise it is skipped and the pipeline still passes.

## GitHub setup
```bash
git init
git add .
git commit -m "Initial project setup"
git branch -M main
git remote add origin https://github.com/<your-username>/expense-tracker.git
git push -u origin main
```
Create the empty repository on github.com first (no README/.gitignore). Then open the **Actions** tab to watch the pipeline.

Suggested commit history (commit after each stage instead of once):
`Initial project setup` → `Implemented expense CRUD APIs` → `Added dashboard and charts` → `Added Docker containerization` → `Added automated tests` → `Added GitHub Actions CI/CD`

## Screenshots
Add your own after running the app (do not commit fake images):
- `docs/screenshots/dashboard.png`
- `docs/screenshots/transactions.png`
- `docs/screenshots/add-transaction.png`
- `docs/screenshots/github-actions.png`

## Future enhancements
User login, budgets and alerts, recurring transactions, CSV/PDF export, PostgreSQL, deployment to a cloud host.

## Team members
| Name | Roll No. | Role |
|---|---|---|
| _your name_ | _roll no._ | _e.g. Backend & Docker_ |

## Conclusion
The project delivers a working expense tracker and shows the complete path from code to tested, containerized, automatically built software.

See `docs/REPORT.md` for report content and `docs/VIVA.md` for viva Q&A.
