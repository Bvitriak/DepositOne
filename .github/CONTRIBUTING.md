# Contributing to DepositOne

Thanks for taking the time to contribute. This guide explains the project layout,
how to run it locally, and the branching and commit rules.

## Project layout

DepositOne is a full-stack app with two backend services built on different
frameworks, plus a static frontend and a PostgreSQL database with Master-Slave
replication.

- `backend/core` - Core service (FastAPI): business logic and main entities.
- `backend/supporting` - Supporting service (Flask): API gateway, reports, auth,
  notifications.
- `frontend` - HTML, CSS, JavaScript, assets.
- `database` - schema, seed data, replication scripts.

Both services follow the same layered structure:

```
Routes -> Controllers -> Services -> Repositories -> Models
```

Please keep changes inside the correct layer. Data access uses SQL through psycopg
only. Do not introduce an ORM.

## Running locally

1. Copy the environment template and fill in the values:

   ```bash
   cp .env.example .env
   ```

2. Build and start everything:

   ```bash
   docker compose up --build
   ```

3. Open `http://localhost:8080`.

See [README](../README.md) and [docs](../docs) for details.

## Git branching

- **main** - final project state and README.
- **dev** - branch for integrating implemented features.
- **feature/** - branches for individual tasks or components.
  - Format: `feature/<username>/<task-name>`.
  - Created from `dev`; merged back into `dev` after implementation.
- **release/** - release preparation, format `release/v1.0`.

## Commit rules

- One commit = one logical change.
- Write commit messages in English.
- Format: `<type>: <short description>`.

### Change type

- [ ] feat - new functionality
- [ ] fix - bug fix
- [ ] docs - documentation
- [ ] style - formatting
- [ ] refactor - refactoring
- [ ] perf - query optimization
- [ ] seed - test / initial data
- [ ] test - tests

Examples:

```
feat: add user authentication
fix: resolve login error
docs: update README
feat(db): create users table
seed(db): add initial test data
perf(db): add index to improve query speed
```

## Pull requests

- Base your branch on `dev` and open the PR against `dev`.
- Fill in the pull request template.
- Make sure the project builds locally before requesting a review.

## Issues

- Bug - `bug_report` template.
- New feature - `feature_request` template.
