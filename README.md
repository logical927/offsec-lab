# OffSec Lab

## Overview

OffSec Lab is a local cybersecurity training platform for learning vulnerability assessment and penetration testing through hands-on exercises in isolated lab environments. Developing the platform also supports learning software engineering, infrastructure, networking, and security.

## Project Status

The Docker Compose development environment starts the frontend, backend, and
PostgreSQL services. The frontend provides the Dashboard → Learning Path → Mission Briefing →
Lab Workspace → Challenge → Mission Complete flow, using shared dark-theme
UI primitives and backend-authoritative progress. The
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

See the basic design and accepted ADRs below.

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
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.seed
```

Open the frontend at <http://localhost:3000>. The home route redirects to the
Dashboard. The frontend proxies `/api/v1/*` requests to the backend across the
private Compose management network.

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

The PostgreSQL service is reachable only from the Compose network; it does not publish port 5432 to the host. The frontend and backend are bound to `127.0.0.1` on the host.

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
cp .env.example .env.local
pnpm dev
```

The development server is bound to `127.0.0.1:3000`; `/` redirects
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

Both frontend commands bind to loopback because the frontend now relays Lab
API requests. Do not expose it to the LAN or Internet.

The browser calls same-origin `/api/v1/*`. Next.js rewrites those requests to
the server-only `API_BASE_URL` in `frontend/.env.local` (default:
`http://127.0.0.1:8000`). Set it to your local backend origin, without
`/api/v1` or a trailing slash. Restart development after changes; rebuild
production because rewrites are recorded at build time. No CORS change or
browser-visible secret is needed.

Mission routes use numeric API IDs, for example `/missions/1`. An empty
database displays an empty state until the initialization commands above run;
the frontend never seeds content. Mission 01 now provides five challenges,
three progressive hints each, scenario/learning goals in the description, and
a learning review in Mission Complete. Difficulty is not exposed by the API.

The authoritative content is `backend/app/mission01.py`. The repeatable seed
updates Mission ID 1 and its five challenge positions in place, preserving
existing IDs, slugs, and progress. See [Mission 01](challenges/m01-recon/README.md)
for the content and verification guide.
Mission 01 provides three hints per challenge and reveals them in order.
Missions without hint data display that hints are unavailable.
Existing XP/LEVEL dashes in the application shell remain unpopulated.

Start, Stop, and Reset are synchronous backend operations. The workspace
refreshes status afterwards to retrieve the current target. Reset confirms
discarding lab changes while preserving learning progress. If a request
times out, refresh status before retrying; stopping the browser request does
not cancel Docker work already accepted by the backend. Ordinary reads have
a 30-second timeout, and Lab writes and their proxy have a five-minute limit.
Transitional states are checked every three seconds for at most 20 checks.

After a correct answer, the UI retrieves progress again. It shows Mission
Complete only when that response confirms completion. Returning to Dashboard,
Learning Path, or Progress fetches fresh backend data. Progress is not stored
in localStorage and Lab Reset does not reset it.

See [frontend flow validation](docs/testing/frontend-mvp-flow.md) for test
coverage and the isolated browser fixture procedure.

Phase 9 adds reproducible real-Lab integration and Chromium E2E tests.
See [Phase 9 test report](docs/testing/phase9-test-report.md) for commands,
test results, isolation/cleanup details, and
[project status audit](docs/testing/project-status-audit.md) for WBS reconciliation.
From `frontend/`, install Chromium with `pnpm exec playwright install chromium`,
then run `pnpm test:e2e` with the management DB/backend image available.
E2E uses a temporary PostgreSQL schema, loopback ports 3001/8001 and the real
Mission 01 Lab. Run it separately from Lab integration tests and active play:
both tests start/stop/reset the singleton Lab and remove its resources afterwards.
Saved player learning progress is preserved.

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
