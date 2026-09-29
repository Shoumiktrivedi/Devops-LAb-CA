# Lab CA Report — Containerized Personal Expense Tracker with Automated CI/CD Pipeline

## A. Abstract
This project is a web-based Personal Expense Tracker that lets a user record income and expenses, search and filter them, and view summaries through charts. It is built with Flask, SQLAlchemy and SQLite on the backend and HTML, CSS, JavaScript and Chart.js on the frontend. The application is packaged with Docker and Docker Compose, tested with PyTest, and integrated with GitHub Actions so that every push is tested and built automatically.

## B. Introduction
Managing personal finances starts with knowing where money is spent. Software projects also need reliable ways to test, package and deliver code. This project combines both: a practical application and a modern DevOps workflow (version control, containers, automated testing and CI/CD).

## C. Problem Statement
Manual tracking in notebooks or spreadsheets is error-prone and gives no quick visual summary. Separately, manually testing and deploying software is slow and inconsistent between machines. The project addresses both problems.

## D. Objectives
1. Develop a REST API for transaction management.
2. Store data persistently with SQLAlchemy and SQLite.
3. Provide a responsive dashboard with charts.
4. Write automated tests with PyTest.
5. Containerize the app using Docker and Docker Compose.
6. Automate testing and building with GitHub Actions.

## E. Proposed System
A single-page dashboard talks to a Flask REST API over JSON. The API validates input, stores data in SQLite and computes dashboard statistics. The whole system runs in one Docker container with a volume for the database. GitHub Actions runs tests and builds the image on every push.

## F. Functional Requirements
- FR1: Add a transaction (type, amount, category, description, date).
- FR2: View all transactions in a table.
- FR3: Edit a transaction.
- FR4: Delete a transaction after confirmation.
- FR5: Filter by type, category and date range.
- FR6: Search by description or category.
- FR7: Show totals, balance, count, recent transactions.
- FR8: Show category-wise and monthly expense charts.
- FR9: Load demo data.

## G. Non-Functional Requirements
- **Usability:** clean, responsive interface for desktop and mobile.
- **Reliability:** input validation and proper error responses.
- **Portability:** runs identically anywhere Docker runs.
- **Maintainability:** separation into routes, services, models; automated tests.
- **Performance:** fast responses for personal-scale data.
- **Security:** no hard-coded secrets, ORM queries prevent SQL injection, output escaped in the UI.

## H. Technology Stack
HTML5, CSS3, JavaScript, Chart.js · Python 3.12, Flask, Flask-CORS · SQLite, SQLAlchemy · PyTest · Docker, Docker Compose · GitHub Actions · Git/GitHub.

## I. System Architecture
Three layers: **presentation** (browser UI), **application** (Flask routes → services), **data** (SQLAlchemy models → SQLite file). The browser calls `/api/*` endpoints using `fetch()`. Flask also serves the static page. In Docker, gunicorn serves Flask on port 5000 and the database file lives in a mounted volume.

## J. Database Design
Table **transactions**

| Column | Type | Notes |
|---|---|---|
| id | Integer | Primary key, auto-increment |
| type | String(10) | `income` or `expense`, indexed |
| amount | Numeric(12,2) | Must be > 0 |
| category | String(50) | Indexed |
| description | String(200) | Optional |
| date | Date | Indexed |
| created_at | DateTime | Set automatically |

## K. API Design
See the API table in the README. The API follows REST conventions: nouns in URLs, HTTP methods for actions, JSON bodies, and status codes 200, 201, 400, 404 and 500.

## L. Docker Architecture
The Dockerfile starts from `python:3.12-slim`, installs requirements (before copying code, to use layer caching), copies the source, runs as a non-root user and starts gunicorn. `docker-compose.yml` defines one service `web`, maps port 5000, sets environment variables, mounts the named volume `expense_data` at `/data` (holding `expenses.db`) and adds a health check. `.dockerignore` keeps unnecessary files out of the image.

## M. CI/CD Workflow
Trigger: push or pull request to `main`. Job 1 installs dependencies and runs PyTest. Job 2 (only if Job 1 passes) validates the Compose file, builds the image and smoke-tests `/api/health`. Job 3 optionally pushes the image to Docker Hub if credentials are configured; otherwise it is skipped.

## N. Testing Strategy
PyTest with Flask's test client, using a fresh temporary SQLite database per test. Coverage: app start, list, create, get by id, update, delete, nine invalid-input cases, filters and search, dashboard calculations, categories, seeding and JSON 404 handling (21 tests). Tests run locally and in CI.

## O. Results
- All 21 automated tests pass.
- The application starts with one command (`docker compose up --build`) and shows a populated dashboard using demo data.
- CRUD, filtering, search and charts function as specified.
- The CI pipeline runs tests and builds the image on each push. *(Add your GitHub Actions and application screenshots here.)*

## P. Advantages
Simple and easy to run; reproducible environment; automated quality checks; clear code structure; visual insights; works offline (Chart.js is bundled).

## Q. Limitations
No user accounts (single user); SQLite is not suited for many concurrent users; single currency (₹); no budgets, exports or recurring entries.

## R. Future Scope
Authentication, multi-user support, PostgreSQL, budget alerts, CSV/PDF export, recurring transactions, mobile app, cloud deployment with continuous delivery.

## S. Conclusion
The project meets its objectives: a working, tested expense tracker that is containerized and automatically validated through CI/CD. It demonstrates practical full-stack development and DevOps practices suitable for real projects.
