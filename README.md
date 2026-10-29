# Humana Interview Prep

A local-first, document-grounded workspace for preparing for Humana interviews. Upload job
descriptions, company research, benefits material, personal preparation notes, and other PDF,
DOCX, or Markdown sources, then ask questions about one selected document. Answers retain source
citations so preparation stays anchored to the supplied material.

The backend uses FastAPI, PostgreSQL full-text search, and pgvector. The frontend uses React and
TypeScript.

## Features

- Structure-aware extraction and configurable token chunking
- Hybrid vector and keyword retrieval with reciprocal-rank fusion
- Source metadata and citations retained through answer generation
- Replaceable embedding and answer providers with deterministic test doubles
- Offline evaluation trials for parsing, chunking, retrieval, embeddings, and generation
- Safe file handling, explicit insufficient-evidence answers, and prompt-injection boundaries
- Unit, API integration, PostgreSQL/pgvector integration, frontend, and browser tests

## Project identity

This repository was created from `full-stack-rag-template` and uses isolated local resources:

- application role and development database: `humana_interview_prep`;
- test database: `humana_interview_prep_test`;
- OpenTelemetry service: `humana-interview-prep-api`;
- OpenTelemetry tracer: `humana-interview-prep`.

The synthetic evaluation fixtures remain a general regression baseline. Add a reviewed,
project-specific interview-preparation dataset before using evaluation results to choose a
production model or retrieval configuration.

## Quick start

Prerequisites are Python 3.12+, `uv`, Node.js 20+, npm, a PostgreSQL service with pgvector, and
(when tracing is enabled) an OTLP-compatible trace backend such as Jaeger. The reference local
topology uses the reusable sibling services described in the development guide.

```bash
cp .env.example .env
# Add credentials for the embedding and chat providers selected in .env.
make db-up
cd backend && uv sync --dev && uv run alembic upgrade head
```

The database service lives outside this repository in the sibling `shared-postgresql` project.
Provision the dedicated `humana_interview_prep` role plus the `humana_interview_prep` and
`humana_interview_prep_test` databases there before running migrations. Host-run applications
connect through `localhost:5434`; containers can join the
`postgresql-for-all-projects-network` Docker network.

For normal development, start the shared containers, apply migrations, and launch both web
services with:

```bash
make dev-start
```

Use `make dev-restart` to restart both web services, `make dev-status` to inspect everything, and
`make dev-stop` to stop only this application's web services. Shared PostgreSQL and Jaeger remain
running because other projects may be using them. Open `http://localhost:5173` after startup.

To verify the evaluation harness with its small example, then run the general starter benchmark:

```bash
make evaluate-smoke
make evaluate
```

Evaluation inputs are configurable without editing the Makefile:

```bash
make evaluate \
  DATASET=evaluation/datasets/starter-general.json \
  TRIALS=evaluation/trials/retrieval.json
```

Reports are written under `.evaluation/` with names derived from the selected dataset and trial
suite. See the evaluation guide for the benchmark layout, model trials, scoring, and safeguards.

For the complete setup, test commands, design, and API contract, see:

- [Development guide](docs/development.md)
- [Customization record and checklist](docs/template-customization.md)
- [Configuration reference](docs/configuration.md)
- [Shared PostgreSQL instance](docs/shared-postgresql.md)
- [Architecture](docs/architecture.md)
- [API reference](docs/api.md)
- [Retrieval design](docs/retrieval.md)
- [Provider selection](docs/providers.md)
- [Evaluation and tuning](docs/evaluation.md)

The application has no user authentication and is intended for trusted local development. Do not
upload confidential or regulated material until an appropriate identity, authorization,
retention, and storage design has been implemented.
