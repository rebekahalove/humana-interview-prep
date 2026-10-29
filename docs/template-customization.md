# Humana Interview Prep customization record

This repository was derived from `full-stack-rag-template`. This record captures the selected
identity, completed customization, and setup that still requires local credentials or shared
infrastructure access.

## 1. Choose the project identity

The project uses these values:

| Purpose | Template value | Humana Interview Prep value |
| --- | --- | --- |
| Repository and folder | `full-stack-rag-template` | `humana-interview-prep` |
| Backend display name | `Full-stack RAG Template API` | `Humana Interview Prep API` |
| Frontend display name | `RAG Workbench` | `Humana Interview Prep` |
| Short UI mark | `R` | `H` |
| PostgreSQL role | `rag_template` | `humana_interview_prep` |
| Development database | `rag_template` | `humana_interview_prep` |
| Test database | `rag_template_test` | `humana_interview_prep_test` |
| OpenTelemetry service | `full-stack-rag-template-api` | `humana-interview-prep-api` |
| OpenTelemetry tracer | `full-stack-rag-template` | `humana-interview-prep` |

The Python and npm package names have also been renamed for consistent artifact naming.

## 2. Create local configuration

The committed `.env.example` and ignored local `.env` contain the selected application, database,
frontend, telemetry, and model values. The selected baseline is OpenAI
`text-embedding-3-small` with `gpt-4.1-mini`. Add `OPENAI_API_KEY` to `.env` before real ingestion
or question answering.

To rebuild the local file from the committed baseline if needed:

```bash
cp .env.example .env
```

The customized fields are:

- `APP_NAME`, `APP_DESCRIPTION`, and `APP_VERSION`;
- `DATABASE_URL` and `TEST_DATABASE_URL`, including the role, password, and database names;
- `VITE_APP_NAME`, `VITE_APP_MARK`, `VITE_APP_TAGLINE`, and `VITE_APP_DESCRIPTION`;
- `OTEL_SERVICE_NAME` and `OTEL_TRACER_NAME`;
- the model selections for the chosen embedding and chat providers. Provider credentials remain
  local-only and are not recorded in version control.

Never put shared PostgreSQL administrator credentials in this repository. Provider keys and local
application passwords belong only in `.env` or a deployment secret manager.

## 3. Install project dependencies

Install the toolchains and locked dependencies before running migrations or tests. The template
requires Python 3.12+, `uv`, Node.js 20+, and npm.

From the repository root, run:

```bash
cd backend && uv sync --dev
cd ../frontend && npm ci
cd ..
```

This installs pytest, pytest-asyncio, Ruff, and the backend runtime from `backend/uv.lock`, plus
the frontend dependencies from `frontend/package-lock.json`. If browser coverage is needed, also
install Playwright once with:

```bash
make e2e-setup
```

Use the lockfiles for repeatable setup; do not install pytest or application dependencies ad hoc
outside the project environment.

## 4. Provision isolated database resources

The launcher expects the reusable `postgresql-for-all-projects` container maintained by the
sibling `shared-postgresql` project. Provision the `humana_interview_prep` login role plus the
`humana_interview_prep` development database and `humana_interview_prep_test` test database from
that infrastructure project. The ignored `.env` contains the application password that must be
used for the role.

After updating `.env`, apply the complete schema:

```bash
make db-up
make migrate
```

The test database name must contain `test`; the integration harness deliberately rejects other
names before running migrations or cleanup.

## 5. Customize the product boundary

The initial product boundary is trusted local development. Review these limitations before
treating the application as production-ready:

- authentication, authorization, tenancy, and rate limiting are intentionally absent;
- uploaded files use local storage rather than managed object storage;
- processing runs in the API process rather than a durable job queue;
- exact document-scoped vector retrieval favors mixed embedding dimensions over a global ANN
  index;
- OCR, malware scanning, retention policies, and backup policies are application decisions;
- allowed document types, upload limits, prompts, and insufficient-evidence behavior are
  configuration rather than universal requirements.

Document every decision that changes these boundaries in the derived repository.

## 6. Replace or extend evaluation data

Keep `evaluation/datasets/example.json` and `evaluation/trials/example.json` as a fast harness
smoke test. The synthetic starter benchmark is useful for regression testing general document RAG,
but it is not a substitute for representative domain data.

Create a reviewed dataset and focused trials for the derived use case, then run:

```bash
make evaluate-smoke
make evaluate DATASET=evaluation/datasets/your-project.json \
  TRIALS=evaluation/trials/your-project.json
```

Do not place credentials, confidential source documents, or generated reports in version control.

## 7. Verify before the first project commit

Run the reusable checks:

```bash
make test-unit
make test-integration
make test-frontend
```

Then search for template identifiers that should not survive in a derived product:

```bash
rg -n 'full-stack-rag-template|rag_template|RAG Workbench' \
  .env.example README.md backend docs frontend tests
```

Occurrences in historical migration identifiers or documentation examples may be intentional;
review rather than blindly replacing them.

## 8. Publish and protect the repository

Protect `main`, require pull requests and status checks, and require at least one reviewer who is
not the account that authored the change.
