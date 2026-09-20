# Security Policy

## Supported versions

The project is developed on the `dev` branch and released from `main`. Security
fixes are applied to the latest state of these branches.

## Reporting a vulnerability

If you found a vulnerability, **do not create a public issue**. Contact the project
author (Bogdan Vitriak) privately and include:

- a description of the problem and its potential impact;
- steps to reproduce;
- version / commit.

We will try to respond within a reasonable time and coordinate disclosure after a
fix.

## Secrets and configuration

- Never commit the `.env` file or any real secrets. `.env` is ignored by
  [.gitignore](../.gitignore); use [.env.example](../.env.example) as a template.
- `JWT_SECRET`, `POSTGRES_PASSWORD` and `REPLICATION_PASSWORD` must be set to
  strong values in every environment.
- Passwords are stored only as bcrypt hashes; plain passwords are never persisted.
