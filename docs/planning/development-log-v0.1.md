# OffSec Lab v0.1 Development Log

## Purpose

This log explains how the v0.1 vertical slice was built and what was learned.
It is based on the Git history, accepted ADRs, implementation, Phase 9 test
report, ISSUE-027 security assessment, and the maintained WBS. Dates below are
repository commit dates, not reconstructed estimates.

## 1. Project foundation — 2026-09-06

**Context.** The project began as a learning-focused local cyber range with
safety, reproducibility, and explainability as primary constraints.

**Problem / decision.** The repository needed guardrails before intentionally
observable services were added. The baseline established the directory layout,
AGENTS.md rules, Git practices, documentation locations, and the frozen v0.1
scope.

**Reason.** Security rules and acceptance criteria are easier to preserve when
they exist before implementation choices accumulate.

**Resolution.** Commit `0fa94b3` established the project baseline. Commit
`5fe74b3` added the Office temporary-file ignore needed for the WBS workflow.

**Result.** The repository had an explicit architecture baseline, security
prohibitions, testing expectations, and issue-sized development process.

**Learning.** Project governance is implementation infrastructure. It prevents
scope and safety decisions from being rediscovered in every issue.

## 2. Requirements and design — 2026-09-06 onward

**Context.** The MVP required one playable reconnaissance mission, not a broad
catalog of security features.

**Problem / decision.** The team had to separate the application that manages
learning state from the intentionally observable Lab. The requirements and basic
design defined a browser-to-frontend-to-backend-to-database path and a distinct
attacker-to-target Lab path.

**Reason.** A narrow vertical slice made it possible to validate learning flow,
Docker lifecycle, persistence, and isolation end to end.

**Resolution.** The requirements fixed the Mission 01 flow and deferred
authentication, multiple users, browser terminal, XP, AI Mentor, additional
vulnerability Labs, and deployment. ADR-002 superseded the initial WSL-hosted
backend choice, ADR-003 selected an internal Lab network, ADR-004 selected
PostgreSQL, and ADR-005 retained an external terminal.

**Result.** Subsequent issues could implement against explicit functional and
security boundaries.

**Learning.** Keeping non-goals visible is as important as describing features.
It prevents a learning MVP from turning into an unreviewable platform rewrite.

## 3. Backend and database foundation — 2026-09-06

**Context.** Mission data, progress, and answer validation needed an
authoritative server and reproducible persistence layer.

**Problem / decision.** The application needed liveness/readiness separation,
database configuration without committed credentials, and a structure that
remained understandable.

**Reason.** Thin APIs, services for business rules, and repositories for data
access isolate concerns and support focused tests.

**Resolution.** Commit `7391efc` added the FastAPI and PostgreSQL foundation,
environment configuration, `/health`, `/ready`, and initial tests. Alembic
migrations became the only supported schema bootstrap path.

**Result.** The backend could start, distinguish process health from database
readiness, and connect to a Compose-managed PostgreSQL service.

**Learning.** Readiness is not the same as liveness. Reporting them separately
produces better diagnostics and avoids claiming the application is usable when
its required database is unavailable.

## 4. Mission, Challenge, Hint, and Progress model — 2026-09-06 to 2026-09-08

**Context.** Mission 01 needed ordered tasks, private accepted answers,
progressive hints, and saved sequential progress.

**Problem / decision.** Content needed to be reusable and seedable without
placing answers in frontend code or destroying existing progress.

**Reason.** Backend ownership prevents answer disclosure and ensures the UI
cannot claim completion without a persisted authoritative result.

**Resolution.** Commit `304204c` added Mission and Challenge models. Commit
`d3ca138` added Progress and sequential transitions. Commit `930a0da` completed
Hint persistence, the learning explanation, repeatable Mission 01 seed logic,
and the final five-challenge content.

**Result.** A fresh database can be migrated and seeded reproducibly. Existing
Mission/challenge identities and progress survive reseeding.

**Learning.** Seed data is production behavior for a local learning platform.
Idempotency and identity preservation matter even when there is only one user.

## 5. Mission and answer APIs — 2026-09-06

**Context.** The frontend needed public mission content and a safe answer
submission contract.

**Problem / decision.** Responses had to provide ordered content and progress
without exposing accepted answers.

**Reason.** Frontend-only validation would reveal answers and make progress
untrustworthy.

**Resolution.** Commit `795827f` added Mission list/detail APIs. Commit
`5c4506e` added normalized backend answer validation. Commit `d3ca138` added the
Progress API and transactionally safe sequential unlock/completion behavior.

**Result.** The backend rejects locked or unknown challenges, preserves progress
on wrong/repeated answers, and returns structured application errors.

**Learning.** Public schemas should be designed independently from persistence
models. A private field is not protected merely because the current UI ignores
it.

## 6. Isolated Lab network — 2026-09-06

**Context.** Mission 01 required real network discovery while preventing normal
external connectivity and host exposure.

**Problem / decision.** Attacker and target needed mutual reachability without a
published target port or shared management network.

**Reason.** An internal, mission-specific bridge provides the intended training
path and a small boundary that can be tested statically and dynamically.

**Resolution.** Commit `7318eab` added `offsec-m01-net` with `internal: true`
and `attachable: false`. The Mission Compose project owns the network separately
from the management Compose project.

**Result.** Lab services communicate through Docker DNS and dynamic IPs while
the target has no direct host mapping or normal external gateway.

**Learning.** Network isolation should be part of the Compose definition, not a
manual workstation convention.

## 7. Attacker and target containers — 2026-09-06 to 2026-09-07

**Context.** The learner needed familiar reconnaissance tools and an observable
SSH/HTTP target.

**Problem / decision.** The containers had to support ICMP and low-port services
without becoming privileged general-purpose environments.

**Reason.** Minimum capabilities preserve the exercise while limiting the
impact of mistakes inside the Lab.

**Resolution.** Commit `7c9f665` added the non-root attacker with `ping`,
`nmap`, and `curl`; all capabilities are dropped except `NET_RAW`. Commit
`9082d67` added the non-root SSH/HTTP target; all capabilities are dropped except
`NET_BIND_SERVICE`. Both use read-only root filesystems, bounded tmpfs, resource
limits, and `no-new-privileges`. Commit `3c18751` fixed shell-script line endings
for Linux container execution.

**Result.** The attacker can discover the target and enumerate its intended
services. Neither Lab container has host mounts, Docker socket access, host
networking, or published ports.

**Learning.** Cross-platform repositories must treat executable line endings as
part of container reproducibility. Least privilege often requires a small,
documented capability exception rather than root.

## 8. Lab Controller — 2026-09-07

**Context.** The browser flow required Start, Stop, Reset, and Status operations
against the real Mission project.

**Problem / decision.** A containerized backend cannot control the host Docker
engine without a control channel. Arbitrary caller-supplied Docker commands or
Compose paths were unacceptable.

**Reason.** The smallest local-only v0.1 path was a backend socket mount combined
with a strict allowlist, while explicitly acknowledging its security cost.

**Resolution.** Commit `36df3d5` added the Mission registry, argument-array
Docker runner, timeouts, and Start operation. Commit `f61a85d` added idempotent
Stop and destructive Lab-only Reset. Commit `2a1e63c` added Docker-derived
Status and target addressing. ADR-006 documented the backend socket as
host-equivalent accepted risk.

**Result.** Numeric Mission ID 1 maps to one fixed Compose file/project. Client
input cannot select paths, images, containers, flags, or shell commands.

**Learning.** Mitigations around a powerful interface do not reduce its
fundamental authority. The socket risk must remain visible until a narrower
host controller or proxy replaces it.

## 9. Frontend foundation and flow — 2026-09-08

**Context.** Backend and Lab capabilities needed a usable learning interface.

**Problem / decision.** The frontend had to represent asynchronous Docker work,
authoritative progress, errors, hints, and reset confirmation without inventing
state.

**Reason.** A thin typed client and domain components provided enough structure
without adding a state-management dependency.

**Resolution.** Commit `f914f4b` recorded the UI/UX basic design. Commit
`2a9d2f6` added the Next.js foundation. Commit `1b77362` implemented Dashboard,
Learning Path, briefing, workspace, Lab controls, challenges, hints, progress,
and completion UI. Same-origin rewrites relay API calls to the local backend.

**Result.** The browser can complete the intended management flow. Lab and
learning state remain backend-authoritative, and no accepted answer is bundled
into the frontend.

**Learning.** A UI should expose uncertainty after a timed-out write instead of
assuming failure or success. Refreshing authoritative status prevents duplicate
or contradictory lifecycle actions.

## 10. First playable Mission 01 — 2026-09-08

**Context.** Infrastructure alone did not satisfy the MVP; it needed a coherent
teaching sequence and review.

**Problem / decision.** Hints had to help progressively without turning public
documentation into an answer key.

**Reason.** Reasoning, technique, and command-example stages support different
levels of learner independence.

**Resolution.** Commit `930a0da` finalized the Northbridge Systems
reconnaissance scenario, five ordered challenges, three hints per challenge,
and a Mission Complete learning explanation.

**Result.** The learner progresses from reachability through port, service,
version, and HTTP inspection and can review why each observation matters.

**Learning.** Good training content separates evidence collection from the
answer format. Showing a command is useful; publishing the observation it should
produce removes the exercise.

## 11. Phase 9 testing — 2026-09-08

**Context.** Component tests existed, but MVP confidence required real database,
Docker, browser, reset, and cleanup evidence.

**Problem / decision.** Mission 01 is a singleton Lab, so integration and E2E
tests could interfere with each other or with an active learner session.

**Reason.** Explicit opt-in, bounded polling, unique database schemas, and scoped
cleanup allow realistic tests without broad Docker or data deletion.

**Resolution.** Commits `7cbf8ec` and `dbd4fcb` completed ISSUE-023 through
ISSUE-026 and reconciled their reports. The suite covered backend unit/API
behavior, real PostgreSQL migrations and seed, real Lab discovery and lifecycle,
frontend integration, Chromium E2E, independent Reset verification, and cleanup.

**Result.** Phase 9 recorded PASS for all four testing issues. Exact counts,
commands, environment, and limitations remain in
[phase9-test-report.md](../testing/phase9-test-report.md).

**Learning.** A passing unit suite cannot establish that Docker networking,
container health, browser rewrites, and persisted progress work together.
End-to-end evidence must also own and clean up its external state.

## 12. Security assessment — 2026-09-09

**Context.** The Lab intentionally exposes SSH/HTTP internally, so the assessment
had to distinguish training surface from platform isolation defects.

**Problem / decision.** Static configuration alone could not prove the runtime
network, mounts, ports, capabilities, and egress state.

**Reason.** Combining source review, rendered Compose, tests, Git secret scans,
and runtime inspection provides evidence across both intended definition and
observed execution.

**Resolution.** Commits `f9a7651` and `712cb4e` completed ISSUE-027. SEC-001
through SEC-007 passed; findings were zero at Critical, High, Medium, Low, and
Informational severity. ADR-006 remained an accepted risk.

**Result.** M7 Security Review Complete was marked Done. Residual limitations,
including the unauthenticated local API, host/Docker dependencies, pattern-based
secret scanning, dependency provenance, and host hardening, remain documented.

**Learning.** A security PASS is scoped evidence, not a statement of universal
safety. Accepted risks and unassessed areas belong next to the result.

## 13. ISSUE-002 Compose gap correction — 2026-09-09

**Context.** Development had progressed with the frontend started separately
while backend and PostgreSQL were managed by the root Compose project.

**Problem / decision.** During final WBS acceptance verification, WBS 2.1 was
re-read and compared with the implementation. Its acceptance criterion required
Frontend, Backend, and Database to start through Compose. The recorded status did
not prove that requirement was satisfied.

**Reason.** The startup gap affected reproducibility and a stated MVP acceptance
criterion, even though the application flow itself already worked.

**Resolution.** Commit `2061732`, merged in `c3e9d95`, added the frontend build
and runtime image to the root Compose stack. It preserved loopback-only frontend
and backend publication, no PostgreSQL host port, non-root frontend execution,
and no frontend Docker socket or Lab-network access.

**Result.** `docker compose up -d --build` now starts all three required
management services, and WBS 2.1 / ISSUE-002 are Done.

**Learning.** Acceptance criteria must be re-read against the delivered system.
WBS status alone is not evidence. A closeout review can catch a small but real
requirements gap before final acceptance without overstating the incident.

## 14. Documentation finalization — 2026-09-09

**Context.** Implementation, testing, and security assessment were complete,
but several documents still mixed prospective design with current behavior.

**Problem / decision.** A third party needed one accurate path through setup,
architecture, Mission play, evidence, accepted risk, and deferred scope.

**Reason.** Documentation is part of the MVP acceptance criteria and must match
the repository rather than repeat historical assumptions.

**Resolution.** ISSUE-028 reconciled the README, implemented architecture,
security assessment delta, Phase 9 report, Mission 01 description, development
history, and WBS dashboard. The final dashboard advances to Phase 12 / ISSUE-029
without completing M8.

**Result.** The repository is prepared for the separate MVP Acceptance Review.
No production code, Lab behavior, vulnerability content, or v0.2 feature was
changed.

**Learning.** Historical reports should retain their test-time context while
clearly noting later changes. Current operational documentation should describe
the final implementation directly.

## Remaining accepted limits before ISSUE-029

- v0.1 remains local-only, single-user, and unauthenticated.
- Backend Docker socket access retains host-equivalent authority under ADR-006.
- The security assessment does not cover dependency vulnerability management,
  image provenance, or full host hardening.
- Only Mission 01 exists.
- M8 remains Not Started until ISSUE-029 verifies every MVP acceptance criterion.
