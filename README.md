# OffSec Lab

## Overview

OffSec Lab is a local cybersecurity training platform for learning vulnerability assessment and penetration testing through hands-on exercises in isolated lab environments. Developing the platform also supports learning software engineering, infrastructure, networking, and security.

## Project Status

Issue 002 — Development Environment. The repository provides the minimal FastAPI and PostgreSQL management-plane development stack. Frontend, lab control, and challenge environments are not implemented yet.

The v0.1 MVP is planned for a single local user and one reconnaissance mission.

## Architecture

The documented v0.1 architecture uses:

- Frontend: Next.js and TypeScript.
- Backend: Python and FastAPI. Issue 002 runs it in the development Compose stack.
- Database: PostgreSQL.
- Labs: Docker and Docker Compose, with dedicated internal lab networks.
- Lab control: the host backend invokes the Docker CLI through a Lab Runner using predefined mission configurations.
- Lab access: an external WSL2 terminal.

These components will be implemented in later issues. See the basic design and accepted ADRs below.

ADR-001 still specifies a WSL2-hosted backend for future Docker lab control. Issue 002's containerized development backend does not control Docker and receives no Docker socket. The execution model must be reconciled before lab-control work begins.

## Requirements

The planned development environment is Windows 11, WSL2 with Ubuntu, and Docker Desktop. Git is used for version control. Runtime versions and installation instructions: TBD.

## Setup

Copy `.env.example` to `.env` and replace the development-only PostgreSQL password before starting the stack. Local `.env` files must remain outside Git.

```bash
cp .env.example .env
docker compose up --build -d
```

Verify that FastAPI can query PostgreSQL:

```bash
curl http://localhost:8000/health
```

A healthy stack returns `{"status":"ok","database":"connected"}`. Stop it with:

```bash
docker compose down
```

The PostgreSQL service is reachable only from the Compose network; it does not publish port 5432 to the host. The backend API is bound to `127.0.0.1` on the host.

## Development

Read [AGENTS.md](AGENTS.md), the MVP requirements, basic design, and relevant ADRs before implementing an issue.

- `frontend/`: future frontend implementation.
- `backend/`: future backend implementation.
- `challenges/`: future isolated mission labs.
- `scripts/`: future development and lab helper scripts.
- `tests/`: future tests.
- `docs/`: planning, requirements, design, security, and testing documentation.

Run the backend API tests from `backend/` after installing `requirements-dev.txt`:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest
```

## Security Notice

OffSec Lab will contain intentionally vulnerable lab environments. Vulnerable targets must not be exposed directly to the Internet. Use the platform only in the isolated local environment defined by the project design.

Application and lab containers must not receive Docker socket mounts. Lab containers must not use privileged mode, host networking, or unnecessary host filesystem mounts. Never commit real credentials or secrets; challenge credentials must be synthetic.

## Documentation

- [Project proposal](docs/企画書.md)
- [MVP requirements v0.1](<docs/OffSec Lab v0.1 MVP要件定義書.md>)
- [Basic design v0.1](docs/design/basic_design_v0.1.md)
- [Architecture decision records](docs/design/adr/)
- [Work breakdown structure](docs/OffSec_Lab_v0.1_WBS.xlsx)
- [Planning](docs/planning/), [security](docs/security/), and [testing](docs/testing/) directories for future documentation.

The proposal and requirements remain at their existing paths under `docs/`. The requirements path referenced in AGENTS.md, `docs/requirements/mvp_requirements_v0.1.md`, is not present; use the existing MVP requirements linked above.
