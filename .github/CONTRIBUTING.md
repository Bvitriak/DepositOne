# Contributing to DepositOne

## Git branching

- **main** - main information about the project.
- **dev** - branch for integrating all implemented features.
- **feature/** - branches for individual tasks / components.
  - Format: `feature/<username>/<task-name>`.
  - Created from `dev`; merged back into `dev` after implementation.
- **release/** - releases, format `release/v1.0`.

## Commit rules

- One commit = one logical change.
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

## Issue

- Bug - `bug_report` template.
- New feature - `feature_request` template.
