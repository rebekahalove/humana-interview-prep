# Shared PostgreSQL dependency

This application uses the standalone PostgreSQL 16 and pgvector service in the sibling
`../shared-postgresql` project. The database server's lifecycle, administrator credential,
persistent volume, network, and cross-project provisioning script are owned there rather than in
this repository.

## Application resources

| Resource | Value |
| --- | --- |
| Host endpoint | `localhost:5434` |
| Application role | `humana_interview_prep` |
| Development database | `humana_interview_prep` |
| Test database | `humana_interview_prep_test` |
| Container | `postgresql-for-all-projects` |
| Shared network | `postgresql-for-all-projects-network` |

The ignored local `.env` contains the complete application and test connection URLs. It must not
contain the shared server's administrator password.

The names above are reserved for Humana Interview Prep and must not be shared with another
application. Provision them by following the
[customization record and checklist](template-customization.md).

## Start and connect

Start an existing shared container from this repository:

```bash
make db-up
```

Host-run application processes use `localhost:5434`. A Dockerized application can join the
external `postgresql-for-all-projects-network` network and use
`postgresql-for-all-projects:5432` instead.

## Provisioning and lifecycle

Provisioning another project's role and databases, stopping the shared server, or changing its
published port must be done from `../shared-postgresql`. Those operations affect every project
that uses the service.

The shared `postgresql-for-all-projects-data` volume contains every project's databases. Never
remove it as part of this application's cleanup or test workflow.
