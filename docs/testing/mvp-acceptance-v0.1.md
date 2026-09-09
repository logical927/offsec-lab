# OffSec Lab v0.1 MVP Acceptance Review

## 1. Review Information

- Review date: 2026-09-09 (Asia/Tokyo)
- Branch: `chore/issue-029-mvp-acceptance`
- Commit reviewed: `1021f37` (`main` and `origin/main` at review start)
- Scope: the approved OffSec Lab v0.1 WBS and merged repository through ISSUE-028
- Review role: technical verification and recommendation only. Product Owner acceptance remains with the User / ChatGPT.

## 2. Acceptance Baseline

The maintained baseline is `docs/OffSec_Lab_v0.1_WBS.xlsx`, supported by the
v0.1 requirements, implemented basic design, ADR-001 through ADR-006, and the
merged repository. The workbook was inspected read-only and was not changed.

The pre-acceptance state is:

- WBS tasks: 75 of 76 Done
- Codex Issues: 28 of 29 Done
- Milestones: 7 of 8 Done
- Current Phase: Phase 12
- Next Task: ISSUE-029
- WBS 12.1, ISSUE-029, and M8: Not Started
- Phase 2, Phase 9, Phase 10, and Phase 11: 100%

The approved v0.1 scope is one complete, local, single-user Mission 01 flow.
Deferred roadmap features are not acceptance failures and were not added to
this review.

## 3. Acceptance Matrix

| Category | Requirement | Evidence | Result | Notes |
| --- | --- | --- | --- | --- |
| A. Project Foundation / Design | Required repository structure and project guidance | `AGENTS.md`; `frontend/`, `backend/`, `challenges/`, `tests/`, `scripts/`, and `docs/`; Git history through `1021f37` | PASS | Root Compose is the infrastructure definition; no empty `infra/` directory is required by current operation. |
| A. Project Foundation / Design | Requirements, implemented architecture, security design, and ADRs | v0.1 requirements; `docs/design/basic_design_v0.1.md`; ADR-001–006; security assessment | PASS | ADR-001 is explicitly superseded by ADR-002. ADR-006 remains an accepted exception. |
| B. Docker Development Environment | Frontend, backend, and PostgreSQL are Compose-managed | Root `docker-compose.yml`; `docker compose config --quiet`; `docker compose up -d --build`; `docker compose ps` | PASS | All three services built and started. Frontend and backend were loopback-published; PostgreSQL had no host-published port. |
| B. Docker Development Environment | Documented startup and shutdown flow | Migrations and seed completed; frontend returned HTTP 200; `/health` and `/ready` passed; `docker compose down` completed | PASS | Shutdown preserved the PostgreSQL volume. |
| C. Backend / Database | Mission, Challenge, Hint, and Progress persistence | Four SQLAlchemy models, four Alembic revisions, repositories, services, and seed module | PASS | Real PostgreSQL suite passed; seed reported that existing progress was preserved. |
| C. Backend / Database | Reproducible schema and Mission 01 seed | `alembic upgrade head`; `python -m app.seed`; real migration/seed tests | PASS | Public Mission 01 response contained five challenges and three hints per challenge. |
| D. Backend APIs | Mission list/detail, answer, progress, completion, and Lab lifecycle APIs | Implemented `/api/v1` route modules; 131-test backend/PostgreSQL run; live frontend-proxied API reads | PASS | Actual routes were reviewed; no endpoint was invented for this review. |
| D. Backend APIs | Server-authoritative answers and structured failures | Challenge service/schemas and API tests; public detail response scan | PASS | `accepted_answers` was absent from the public response. |
| E. Lab Infrastructure | Dedicated internal network and restricted attacker/target | `challenges/m01-recon/compose.lab.yml`, Dockerfiles, static tests, and real Lab integration | PASS | Network is internal and non-attachable; Lab containers have no host ports, host mounts, host network, privilege, or Docker socket. |
| E. Lab Infrastructure | Attacker-to-target reconnaissance | Real integration and Chromium E2E runs | PASS | Ping/DNS, Nmap service discovery, HTTP inspection, and the intended SSH/HTTP surfaces were exercised without publishing target ports. |
| F. Lab Controller | Start → Status → Stop → Reset and error handling | Lab registry, runner, service/API tests, real Lab integration, and E2E | PASS | Registry fixes Mission 1's Compose path/project. Runner uses argument-array subprocess execution, timeouts, locking, and sanitized errors. |
| G. Frontend | Mission selection, details, Lab controls/status/target, answers, hints, completion | 41 Vitest tests, lint, typecheck, production build, and real Chromium E2E | PASS | Incorrect and correct results, sequential progression, three-stage hints, Mission Complete, Reset, Stop, and persisted completion were covered. |
| H. Mission 01 Content | Approved reconnaissance scenario and five challenges | `backend/app/mission01.py`, seed tests, public API shape, and Mission 01 README | PASS | Flow is Host Discovery, Port Scan, Service Enumeration, Version Detection, and HTTP Inspection. Answers are not reproduced here. |
| H. Mission 01 Content | Staged hints and learning explanation | Three persisted hints per challenge and non-empty learning explanation; API, frontend, and E2E tests | PASS | Hints progress from reasoning to technique to a command example. |
| I. Testing | Unit, API, database, Lab integration, frontend, build, E2E, and Reset evidence | Current reruns below and `docs/testing/phase9-test-report.md` | PASS | Current reruns are primary evidence; the dated Phase 9 report supplies historical context and prior repeated runs. |
| I. Testing | Repository and security regression checks | `git diff --check`; static Docker tests; security delta review; tracked-file secret scan | PASS | No test was weakened or skipped to obtain a pass. |

## 4. Automated Test Summary

### Rerun during ISSUE-029

| Validation | Result |
| --- | --- |
| `docker compose config --quiet` | PASS |
| `docker compose -f challenges/m01-recon/compose.lab.yml config --quiet` | PASS |
| `docker compose up -d --build` | PASS; frontend, backend, and PostgreSQL started |
| Live frontend, `/health`, `/ready`, database, and frontend-to-backend API checks | PASS |
| Backend tests with real PostgreSQL | 131 passed, 1 existing Starlette/AnyIO deprecation warning |
| Broader backend/static suite excluding opt-in integrations | 139 passed, 1 skipped, 1 deselected, 1 existing warning |
| Frontend Vitest | 41 passed across 12 files |
| Frontend lint | PASS |
| Frontend typecheck | PASS |
| Frontend production build | PASS during the Compose image build |
| Real Lab integration | 1 passed in 24.47 seconds |
| Real Chromium E2E | 1 passed in 34.0 seconds |
| `git diff --check` before record creation | PASS |

The broader local suite's one skip is the explicitly opt-in real PostgreSQL
case, which passed in the separate 131-test run. Its one deselection is the
explicitly opt-in real Lab test, which passed separately. These are not missing
acceptance coverage.

### Reused historical evidence

`docs/testing/phase9-test-report.md` remains valid historical evidence for the
Phase 9 environment, test design, earlier repeated runs, and cleanup behavior.
Current ISSUE-029 reruns cover every material production change merged after the
Phase 9 baseline, including the frontend Compose closeout. Historical results
were not substituted for a failing or unavailable current check.

## 5. E2E Result

PASS. The current real Chromium test completed the supported player lifecycle:

```text
Compose platform startup
→ Frontend access
→ Mission 01 selection and briefing
→ Lab Start and RUNNING status
→ Real attacker-to-target reconnaissance
→ Incorrect and correct challenge interaction
→ Three-stage hints
→ Five completed challenges and Mission Complete
→ Lab Reset with target recreation
→ Progress preservation
→ Lab Stop and resource cleanup
→ Compose platform shutdown
```

The browser test used the real FastAPI application, real migrations and seed,
a unique PostgreSQL schema, real Docker Lab resources, and no production route
mock. The separate real Lab integration independently verified reconnaissance,
Reset marker removal, target container replacement, Stop idempotence, and
cleanup.

## 6. Security Assessment Summary

ISSUE-027 remains the primary security baseline. The committed assessment was
checked against the current Compose files, Dockerfiles, Lab registry/runner,
tests, and current runtime results.

| Check | Result |
| --- | --- |
| SEC-001 Host Port Exposure | PASS |
| SEC-002 Docker Network Isolation | PASS |
| SEC-003 Container Privilege | PASS |
| SEC-004 Docker Socket Exposure | PASS, subject to ADR-006 Accepted Risk |
| SEC-005 Host Filesystem / Volume | PASS |
| SEC-006 Internet Isolation | PASS |
| SEC-007 Secret Scan | PASS within its documented pattern-based scope |

Committed ISSUE-027 finding counts remain Critical 0, High 0, Medium 0, Low 0,
and Informational 0.

Changes after the ISSUE-027 assessment were reviewed from `712cb4e` through
`1021f37`. The ISSUE-002 closeout added the frontend to the root Compose stack.
The final state preserves frontend and backend loopback binding, no PostgreSQL
host port, a non-root/non-privileged frontend with `no-new-privileges`, no
frontend Docker socket or host mount, no host network, and no frontend Lab
network membership. Current static tests, real Lab integration, and real E2E
passed. No security-relevant regression was identified, so ISSUE-027 remains
applicable with this documented delta.

## 7. Accepted Risks

ADR-006 remains accurate and unresolved. The backend's direct Docker socket
access provides host-equivalent authority. The local-only API, loopback binding,
fixed Mission registry, fixed Docker operations, argument-array subprocesses,
timeouts, sanitized errors, non-root/non-privileged backend, and read-only
repository mount reduce exposure but do not eliminate that authority.

This risk is accepted only for the local, single-user v0.1 architecture. The
socket is not granted to the frontend, database, attacker, or target. LAN or
Internet exposure, multi-user operation, or broader Docker control requires a
new architecture decision and safer control boundary.

## 8. Documentation Review

PASS. README, implemented architecture, UI/UX design, security assessment,
Phase 9 test report, development log, Mission 01 README, ADRs, and WBS were
reviewed for current behavior, scope, risks, links, and status.

The operational documents consistently describe the Compose-managed
three-service platform, same-origin frontend API path, external terminal,
five-challenge Mission 01, internal Lab network, lifecycle, tests, deferred
scope, and ADR-006. The UI/UX document explicitly labels its future Mission,
XP, Level, and wireframe examples as design reference rather than implemented
v0.1 functionality. Dated Phase 9 audit wording remains identifiable as
historical evidence and does not override the current WBS or final operational
documents. No contradiction that blocks v0.1 acceptance was found.

## 9. Known Limitations

- v0.1 is local-only, single-user, and intentionally unauthenticated.
- ADR-006 backend Docker socket access retains host-equivalent authority.
- Only Mission 01 is implemented.
- Lab commands require an external WSL2 terminal; there is no browser terminal.
- Docker Desktop, WSL2, host firewall behavior, and local configuration remain
  trusted environment dependencies.
- Secret scanning is pattern-based and can miss novel or low-entropy secrets.
- Dependency vulnerability management, image provenance, comprehensive host
  hardening, and denial-of-service assessment were outside ISSUE-027's scope.

## 10. Deferred Scope

Deferred work includes additional Missions and Learning Paths; SQL injection,
XSS, IDOR, privilege-escalation, and Active Directory Labs; authentication and
multi-user support; multiplayer; rankings and achievements; XP/levels and skill
trees; AI Mentor; browser terminal; production or Internet hosting; cloud
deployment; and Kubernetes. Their absence is not a v0.1 failure.

## 11. Blockers

None

## 12. Technical Recommendation

READY FOR PRODUCT OWNER ACCEPTANCE

This recommendation does not mark ISSUE-029, WBS 12.1, or M8 complete and does
not constitute Product Owner acceptance.
