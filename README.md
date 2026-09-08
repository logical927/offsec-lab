# OffSec Lab

OffSec Lab is a local cyber range for learning vulnerability assessment and
penetration-testing fundamentals through hands-on exercises. It combines a web
learning platform with intentionally observable targets that run inside isolated
Docker networks. The project also documents the engineering decisions behind the
platform so it can be reviewed as a software, infrastructure, and security
portfolio.

OffSec Lab v0.1 is a single-user, local-only MVP. Its goal is one complete
vertical slice: select Mission 01, start its Lab, investigate the target from an
attacker container, answer the challenges, review the learning material, and
stop or reset the Lab.

> [!WARNING]
> OffSec Lab intentionally runs services designed for security training. Use it
> only on a local, isolated development machine. Do not publish the target,
> connect Lab networks to production systems, use real credentials, or attack
> anything outside the OffSec Lab resources provided for the exercise.

## v0.1 scope

The implemented MVP contains:

- a Next.js/TypeScript frontend with Dashboard, Learning Path, Mission Briefing,
  Lab Workspace, Progress, staged Hints, and Mission Complete views;
- a FastAPI backend with Mission, Challenge Answer, Progress, and Lab lifecycle
  APIs;
- PostgreSQL models and migrations for Mission, Challenge, Hint, and Progress;
- a server-side Mission registry and Docker Compose Lab Runner for fixed,
  allowlisted lifecycle operations;
- Mission 01, a reconnaissance exercise with five sequential challenges;
- a restricted attacker container with `ping`, `nmap`, and `curl`;
- an SSH/HTTP target reachable only from the Mission 01 Lab network; and
- unit, API, database, Docker integration, frontend, browser E2E, reset, and
  security-assessment evidence.

Authentication, multiple users, multiplayer, XP/levels, skill trees, rankings,
achievements, AI Mentor, a browser terminal, production or cloud deployment,
Kubernetes, and additional vulnerability labs such as SQL injection, XSS, IDOR,
privilege escalation, or Active Directory are not v0.1 features.

## Architecture

```text
Local browser
    |
    | 127.0.0.1:${FRONTEND_PORT:-3000}
    v
Next.js frontend -------- management network -------- FastAPI backend
                                                    |            |
                                                    |            +--> PostgreSQL
                                                    |
                                                    +--> Docker socket (ADR-006)
                                                          |
                                                          v
                                                allowlisted Lab Runner
                                                          |
                                                          v
Attacker container --> offsec-m01-net (internal) --> Target container
                                                      SSH 22 / HTTP 80
```

The Compose-managed frontend, backend, and PostgreSQL database share the
`management` bridge network. The frontend is exposed on host loopback and
forwards same-origin `/api/v1/*` requests to the backend over that network. The
backend is also exposed on loopback for local diagnostics. PostgreSQL publishes
no host port.

Mission 01 runs in a separate Lab Plane. Its attacker and target join only the
dedicated `offsec-m01-net` internal bridge. The target uses `expose` for TCP/22
and TCP/80 but publishes neither port to the host. The intended training path is
attacker to target; the normal Docker external gateway is unavailable to both
Lab containers.

The backend controls Docker through the Docker CLI and a fixed Mission registry.
For the local v0.1 MVP, it mounts the Docker socket under the narrowly scoped
exception in [ADR-006](docs/design/adr/ADR-006-backend-docker-socket-mvp-exception.md).
This grants host-equivalent authority and remains an accepted risk, not an
eliminated risk. Attacker and target containers never receive the socket.

See [Basic design v0.1](docs/design/basic_design_v0.1.md) for components,
communication paths, lifecycle, networks, data ownership, and trust boundaries.

## Prerequisites

The supported development environment is:

- Windows 11 with WSL2 and Ubuntu;
- Docker Desktop with the Linux container engine and Docker Compose plugin; and
- Git.

The primary startup workflow is Docker Compose. A host Python, Node.js, or pnpm
installation is needed only when running the optional host-side development and
test commands.

## Setup and startup

Clone the repository and run the commands below from its root in WSL2. The
backend mount expects the WSL Docker socket at `/var/run/docker.sock`.

```bash
git clone <repository-url>
cd "OffSec Lab"
cp .env.example .env
```

Edit `.env` and replace the placeholder PostgreSQL password with a synthetic,
local-development value. Do not commit `.env`. Set `DOCKER_GID` to the numeric
group owner of the Docker socket:

```bash
stat -c '%g' /var/run/docker.sock
```

Start and build the frontend, backend, and PostgreSQL services:

```bash
docker compose up -d --build
```

Create the database schema and seed Mission 01:

```bash
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.seed
```

Open:

- Frontend: <http://127.0.0.1:3000>
- Backend liveness: <http://127.0.0.1:8000/health>
- Backend readiness: <http://127.0.0.1:8000/ready>

`FRONTEND_PORT` and `BACKEND_PORT` in `.env` can change the host-side port
numbers, but the Compose bindings remain limited to `127.0.0.1`. A ready backend
returns `{"status":"ready","database":"connected"}`. The liveness endpoint can
remain healthy while readiness reports a disconnected database.

Stop the management stack without deleting PostgreSQL data:

```bash
docker compose down
```

To remove the local PostgreSQL volume as an explicit destructive cleanup, use
`docker compose down --volumes`. This erases saved application data and is not
part of normal shutdown.

## Mission 01: how to play

1. Open the frontend and choose **Learning Path**.
2. Select **Mission 01 — Reconnaissance Fundamentals** and read the briefing.
3. Open the Lab Workspace and choose **Start Lab**. Wait for `RUNNING` and note
   the dynamically assigned target IP.
4. In a separate WSL2 terminal, enter the attacker container:

   ```bash
   docker exec -it offsec-m01-attacker bash
   ```

5. Investigate only the displayed target or the `target-m01` Docker DNS name.
   Use the tools and staged hints provided by the mission. Interpret your own
   observations; this README intentionally omits challenge answers.
6. Submit each answer in the Lab Workspace. The backend validates answers and
   unlocks the five challenges in order.
7. Reveal Hint 1, Hint 2, and Hint 3 as needed. Hints progress from reasoning to
   technique to a command example.
8. After all challenges are complete, review the Mission Complete learning
   explanation.
9. Choose **Stop Lab** to stop the containers. Choose **Reset Lab** when you want
   the Lab containers, network, and Lab volumes recreated from the known
   definition. Reset preserves saved learning progress.

The browser has no embedded terminal in v0.1. Lab commands run in the external
WSL2 terminal attached to the attacker container.

## Development and validation

Repository layout:

- `frontend/` — Next.js application, UI components, Vitest, and Playwright E2E;
- `backend/` — FastAPI application, services, repositories, migrations, and tests;
- `challenges/m01-recon/` — Mission 01 attacker, target, and isolated Compose file;
- `tests/` — static Docker-definition and real Lab integration tests;
- `scripts/` — E2E backend support; and
- `docs/` — requirements, design, ADRs, testing, security, WBS, and development log.

For frontend-only development, copy `frontend/.env.example` to
`frontend/.env.local`, set `API_BASE_URL` to the local backend origin, and use
the scripts in `frontend/package.json`. The Compose workflow above remains the
primary full-stack startup method.

The final Phase 9 report records the exact environment, commands, scope, and
results for:

- backend unit and API tests, including the real PostgreSQL suite;
- Mission 01 Docker integration and reconnaissance;
- frontend component and API-client integration tests;
- a real Chromium end-to-end Mission 01 flow; and
- independent Lab reset validation.

See [Phase 9 test report](docs/testing/phase9-test-report.md) rather than relying
on a duplicated or potentially stale count in this README.

## Security architecture

The v0.1 security boundary is intentionally local and narrow:

- **Host ports:** frontend and backend bind to loopback; PostgreSQL and Lab
  targets publish no host ports.
- **Networks:** the management network is separate from the internal Mission 01
  Lab network. Attacker and target join only the Lab network.
- **Privileges:** frontend, backend, attacker, and target run as non-root users.
  Compose sets the relevant services non-privileged and uses
  `no-new-privileges`; Lab containers have read-only root filesystems and only
  the minimum documented capabilities.
- **Docker socket:** only the backend receives it under ADR-006. It is forbidden
  for frontend, database, attacker, target, and future challenge containers.
- **Filesystem:** Lab containers receive no host bind mounts. Their writable
  `/tmp` locations are bounded `tmpfs` mounts. The backend repository bind is
  read-only; PostgreSQL uses its named data volume.
- **Secrets:** `.env` files are ignored, `.env.example` contains placeholders,
  and Mission credentials/data are synthetic.
- **Internet:** the target is not directly host- or Internet-exposed. The
  internal Lab network provides no normal external gateway.

The [v0.1 Security Assessment](docs/security/security-assessment-v0.1.md)
records SEC-001 through SEC-007 as PASS with zero findings at every severity.
It also records the Docker socket authority, local unauthenticated API, host
configuration dependencies, pattern-based secret scanning, and unassessed
dependency/host-hardening concerns as accepted or residual risks.

## Documentation

- [Project proposal](docs/企画書.md)
- [MVP requirements v0.1](<docs/requirements/OffSec Lab v0.1 MVP要件定義書.md>)
- [Basic design v0.1](docs/design/basic_design_v0.1.md)
- [Architecture decision records](docs/design/adr/)
- [Mission 01 design and validation](challenges/m01-recon/README.md)
- [Phase 9 test report](docs/testing/phase9-test-report.md)
- [Security assessment v0.1](docs/security/security-assessment-v0.1.md)
- [Development log v0.1](docs/planning/development-log-v0.1.md)
- [Work breakdown structure](docs/OffSec_Lab_v0.1_WBS.xlsx)

## Deferred work

The following require later requirements and, where architecture or trust
boundaries change, new ADRs: additional learning paths and missions; SQL
injection, XSS, IDOR, privilege-escalation, or Active Directory labs; XP/levels,
skill trees, rankings, and achievements; AI Mentor; browser terminal; login and
multi-user operation; multiplayer; cloud or Internet deployment; and
Kubernetes. They are intentionally absent from v0.1.
