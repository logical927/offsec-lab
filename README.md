# OffSec Lab

## Overview

OffSec Lab is a local cybersecurity training platform for learning vulnerability assessment and penetration testing through hands-on exercises in isolated lab environments. Developing the platform also supports learning software engineering, infrastructure, networking, and security.

## Project Status

The frontend foundation provides a Next.js App Router shell, shared design
tokens and UI primitives, and placeholder routes for the v0.1 user flow. The
backend provides Mission, Challenge Answer, and Progress APIs backed by
PostgreSQL. Mission 01 has an internal Docker network, a restricted attacker
container, and an observable SSH/HTTP target for reconnaissance. The backend
Lab Controller can start, stop, and reset Mission 01 through its allowlisted API.

The v0.1 MVP is planned for a single local user and one reconnaissance mission.

## Architecture

The documented v0.1 architecture uses:

- Frontend: Next.js and TypeScript.
- Backend: Python and FastAPI. Issue 002 runs it in the development Compose stack.
- Database: PostgreSQL.
- Labs: Docker and Docker Compose, with dedicated internal lab networks.
- Lab control: the containerized backend invokes Docker Compose through a Lab Runner using predefined mission configurations.
- Lab access: an external WSL2 terminal.

These components will be implemented in later issues. See the basic design and accepted ADRs below.

ADR-002 supersedes ADR-001 and establishes the containerized management plane.
ADR-006 documents a security-sensitive local MVP exception that mounts the
Docker socket only into the backend. Challenge containers never receive it.

## Requirements

The planned development environment is Windows 11, WSL2 with Ubuntu, and Docker Desktop. Git is used for version control. Runtime versions and installation instructions: TBD.

## Setup

Copy `.env.example` to `.env` and replace the development-only PostgreSQL password before starting the stack. Local `.env` files must remain outside Git.

In WSL2, set `DOCKER_GID` in `.env` to the numeric group owner reported by
`stat -c '%g' /var/run/docker.sock`. This lets the non-root backend process use
the socket without making it world-writable.

```bash
cp .env.example .env
docker compose up --build -d
```

Verify FastAPI liveness:

```bash
curl http://localhost:8000/health
```

This returns `{"status":"ok"}` whenever the FastAPI process is running and does not
depend on PostgreSQL. Verify application readiness, including PostgreSQL connectivity:

```bash
curl http://localhost:8000/ready
```

A ready stack returns `{"status":"ready","database":"connected"}`. If PostgreSQL
is unavailable, `/health` remains HTTP 200 while `/ready` returns HTTP 503 with
`{"status":"not_ready","database":"disconnected"}`. Stop the stack with:

```bash
docker compose down
```

Start Mission 01 through the application:

```bash
curl -X POST http://localhost:8000/api/v1/labs/1/start
```

The response reports `status: "running"` and whether the complete healthy lab
was already running. Only registered Mission IDs are accepted. The operation
has a 120-second execution timeout.

Temporarily stop Mission 01 without removing its containers:

```bash
curl -X POST http://localhost:8000/api/v1/labs/1/stop
```

The response reports `status: "stopped"` and whether the lab was already
stopped. Repeated stop requests are safe. Recreate Mission 01 from its clean
Compose definition and wait for it to become healthy:

```bash
curl -X POST http://localhost:8000/api/v1/labs/1/reset
```

Reset removes only the registered `offsec-m01` Compose project's containers,
network, and volumes, then force-recreates and starts that project. It does not
reset saved learning progress.

Inspect the current Mission 01 lab state:

```bash
curl http://localhost:8000/api/v1/labs/1/status
```

The status is one of `STOPPED`, `STARTING`, `RUNNING`, `STOPPING`, or `ERROR`.
When the lab is running, the response also includes the Target container's
hostname and internal lab-network IP address. Docker command failures are
reported as `ERROR` without exposing command output or host details.

Apply database migrations from the backend container after the stack starts:

```bash
docker compose exec backend alembic upgrade head
```

Alembic reads the same `POSTGRES_*` environment variables as the application;
the configuration does not contain database credentials.

The PostgreSQL service is reachable only from the Compose network; it does not publish port 5432 to the host. The backend API is bound to `127.0.0.1` on the host.

## Development

Read [AGENTS.md](AGENTS.md), the MVP requirements, basic design, and relevant ADRs before implementing an issue.

- `frontend/`: Next.js and TypeScript frontend.
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

Install and run the frontend from `frontend/` with Node.js and pnpm:

```bash
cd frontend
pnpm install
pnpm dev
```

The development server is available at `http://localhost:3000`; `/` redirects
to `/dashboard`. Run each frontend validation command from `frontend/`:

```bash
pnpm lint
pnpm typecheck
pnpm test
pnpm build
```

Preview a completed production build locally with:

```bash
pnpm start
```

Run migrations locally from `backend/` with the same `POSTGRES_*` variables set:

```bash
alembic upgrade head
alembic downgrade base
alembic upgrade head
```

Validate the Mission 01 network definition from the repository root:

```bash
docker compose -f challenges/m01-recon/compose.lab.yml config --quiet
```

Mission 01 uses the dedicated internal bridge network `offsec-m01-net`. The
attacker service is attached to it; the future target must use the same network
without publishing host ports.

## Security Notice

OffSec Lab will contain intentionally vulnerable lab environments. Vulnerable targets must not be exposed directly to the Internet. Use the platform only in the isolated local environment defined by the project design.

Lab containers must not receive Docker socket mounts or use privileged mode,
host networking, or unnecessary host filesystem mounts. The backend-only socket
exception is documented in ADR-006 and grants host-equivalent Docker authority;
keep the API bound to localhost. Never commit real credentials or secrets;
challenge credentials must be synthetic.

## Documentation

- [Project proposal](docs/企画書.md)
- [MVP requirements v0.1](<docs/requirements/OffSec Lab v0.1 MVP要件定義書.md>)
- [Basic design v0.1](docs/design/basic_design_v0.1.md)
- [Architecture decision records](docs/design/adr/)
- [Work breakdown structure](docs/OffSec_Lab_v0.1_WBS.xlsx)
- [Planning](docs/planning/), [security](docs/security/), and [testing](docs/testing/) directories for future documentation.

The requirements path referenced in AGENTS.md,
`docs/requirements/mvp_requirements_v0.1.md`, is not present; use the existing
MVP requirements linked above.
