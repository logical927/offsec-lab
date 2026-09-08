# Phase 9 Test Report

Validated locally on 2026-09-08 (Asia/Tokyo). **Final result: PASS** for
ISSUE-023, ISSUE-024, ISSUE-025, and ISSUE-026. This is a testing milestone,
not the Phase 10 security assessment or final MVP acceptance.

## Environment

- Windows 11, Docker Desktop Linux Engine 29.7.2.
- Containerized FastAPI 0.116.1 / Python 3.12, PostgreSQL 17 Alpine.
- Next.js 16.3.4, React 19.2.8, TypeScript 5.9.3, Node 24.19.0,
  pnpm 11.19.0, Vitest 5.0.0, React Testing Library 16.3.3.
- pytest 8.4.1, httpx 0.28.1, Playwright 1.63.0,
  Chromium 153.0.8010.12. E2E uses one worker and no retries.
- Live management API: loopback port 8000. E2E API: loopback port 8001;
  E2E frontend: loopback port 3001. No DB or target host ports added.

## Repository and starting baseline

Started on `main` at `1215116` (merged frontend MVP PR #16). Created
`feat/issues-023-026-phase9-testing` from that HEAD while retaining all existing
uncommitted files. The working tree already contained ISSUE-022 models, migration,
seed/content, frontend learning/hints changes, its tests/report, README changes,
a modified WBS, an unrelated UI design file deletion/replacement, and `outputs/`.
These were not discarded or attributed to Phase 9. No merge, push, or PR created.

Read the actual Japanese-named MVP requirements, basic design, ADR-001 through
ADR-006, Mission 01 README and prior testing reports. The requirements filename
specified in AGENTS.md does not exist. ADR-002/006 supersede the original
WSL-hosted control-plane model. Existing backend socket access is not new work.

Inventory covered API routes, models, repositories, services, Lab Runner/registry,
Compose/Dockerfiles, API client, mission/workspace/hints/completion components,
pytest/Vitest/package configuration, all existing test files, Git history/merged
commits and all five workbook sheets. No separate repository issue specifications
or CHANGELOG were found; the workbook contains the ISSUE-001–029 roadmap.
GitHub CLI and a connected GitHub tool were unavailable, so remote issue and
milestone status was not independently verified or changed. Local merged PR
history was reviewed; issue numbers are not inferred from GitHub PR numbers.

Starting regression: **121 passed, 1 skipped** across backend and static Docker
definition tests; **38 frontend tests passed**. The skipped case was the existing
explicitly opt-in PostgreSQL test and was subsequently executed successfully.

## ISSUE-023 Backend Tests

### Existing coverage → missing coverage → additions

| Area | Existing coverage | Phase 9 addition |
| --- | --- | --- |
| Health/readiness | Liveness, healthy/unavailable/missing DB settings | No duplicate tests |
| Mission | List/detail public schema, ordered challenges, unknown/invalid IDs, active filters | No duplicate tests |
| Challenge | Correct/wrong, locked/unknown/non-answerable, validation, normalization, answer disclosure/log checks | No duplicate tests |
| Progress | Sequential unlock, completion, persisted migration/seed/API flow, rollback and logging | Two cases: correct and wrong repeated answers preserve completed progress, row identity and single completion event semantics |
| Lab | Start/stop/reset/status, idempotency, domain/CLI errors, sanitized errors, timeout, argument arrays, partial/transitional runtime states | Sixteen cases: zero, negative, nonnumeric and shell-like IDs across all four operations never reach the service/Docker |

Added **18 cases** to `test_progress_service.py` and `test_lab_api.py`.
The real PostgreSQL test already exercises all five seeded challenges and the
actual routes/repositories in a unique schema, including migration round trips.
It remains intact and is explicitly executed below.

Result: **130 passed, 1 skipped** locally for backend only;
**131 passed, 0 failed, 0 skipped** with PostgreSQL enabled. The broader local
backend/static suite has **139 passed, 1 skipped, 1 deselected** when excluding
the opt-in real Lab test. The PostgreSQL skip is not counted as a pass.

## ISSUE-024 Lab Integration

`tests/test_lab_integration.py` uses real HTTP requests to the management backend
and real Docker CLI calls. `OFFSEC_TEST_LAB=1` is an explicit opt-in to owning
Mission 01's singleton Lab. An explicitly requested run fails if Docker or the
API is unavailable. It must not overlap E2E or a learner's Lab session.

Scenario: confirm readiness, establish STOPPED, Start API, bounded RUNNING polling,
repeat Start, inspect both containers and the internal network, resolve target
DNS/IP from attacker, enumerate SSH/HTTP/version with Nmap, retrieve the target
HTTP title, create a `/tmp` marker, Reset API, verify RUNNING, changed container ID
and marker disappearance, verify unchanged learning progress, Stop and repeat
Stop, then remove only the registered Lab project's containers/network/volumes.

Fixture teardown runs on success/failure, tries API Stop, then Compose `down`
in a nested `finally`, and asserts no Lab containers or network remain.
Polling uses deadlines; subprocess and HTTP operations have bounded timeouts.

Result: **1 passed, 0 failed, 0 skipped**. Initial run 25.63s; final regression
23.96s. Backend Start/Stop/Reset and Docker isolation were exercised unchanged.

## ISSUE-025 Frontend Tests

Existing suites cover mission list/selection/detail, controls/status/errors,
answers/progress refresh, progressive hints, completion and API errors/timeouts.
Most component suites mock the API object, while client tests mock fetch.

Added `workspace-api.test.tsx` with **3 integration cases** that mock only fetch
and run the actual API client: briefing navigation; Start/hints/wrong and correct
answers/backend-confirmed completion/Reset/Stop; and HTTP answer failure with
sanitized errors and disabled resubmission. Paths, methods and answer payloads
match the backend. No real backend is needed for Vitest.

Result: **41 passed across 12 files**, no failures/skips. Lint, typecheck and
production build passed. Vitest includes only `tests/**/*.test.{ts,tsx}` so it
does not attempt to execute Playwright tests.

## ISSUE-026 E2E / Reset

`pnpm test:e2e` starts a disposable management backend using the existing Compose
service and source tree. `scripts/e2e_backend.py` creates a unique PostgreSQL
schema, applies the real migrations, seeds Mission 01, and runs the actual
FastAPI application. No route/dependency mock or production bypass is used.
Player progress remains in the original schema. The E2E backend drops only its
unique schema on shutdown, and the runner requires the cleanup acknowledgement.

Playwright starts the real Next.js application on loopback port 3001 and follows:

1. Learning Path → View Mission → Mission Briefing → Lab Workspace.
2. Confirm fresh 0/5 progress, Start Lab and wait for RUNNING.
3. Real attacker DNS, ping, Nmap SSH/HTTP/service/version and curl observations.
4. Reveal all three hints, submit an incorrect answer without advancing progress.
5. Submit five documented fixed Mission 01 observations through the UI and check
   each increment, sequential challenge navigation and Mission Complete.
6. Create a target `/tmp` marker and verify it exists; confirm Reset through the
   UI; verify successful response, RUNNING, new target ID and absent marker.
7. Verify Reset preserves completed progress, Stop through the UI, confirm
   STOPPED/no target, reload and confirm completion remains saved.
8. Assert no browser `pageerror`; always Stop in `finally`. The runner removes
   the E2E backend, confirms schema cleanup and removes/validates Lab resources.

Answers are documented fixed observations, never queried from private answer
fields. Reconnaissance assertions check those observations against the real lab.

Result: **1 passed, 0 failed, 0 skipped**. Initial run 44.3s total; final regression
41.9s total. Reset is verified independently in both real Lab and browser suites.

## Reproduction and validation commands

Start the existing management stack with configured `.env`, Docker socket group
and built lab images as described in README. No additional user/real credentials
are introduced. Run the following groups **sequentially** for the singleton Lab.

From repository root on Windows (or use the matching virtualenv Python on Linux):

```powershell
$env:PYTHONPATH='backend'
.\.venv\Scripts\python.exe -m pytest backend/tests tests -q -m 'not integration' -p no:cacheprovider
$env:OFFSEC_TEST_LAB='1'
.\.venv\Scripts\python.exe -m pytest tests/test_lab_integration.py -q -p no:cacheprovider
Remove-Item Env:OFFSEC_TEST_LAB
```

Real PostgreSQL plus the complete backend suite, from the repository root:

```bash
docker compose run --rm --no-deps -w /workspace/backend \
  -e PYTHONPATH=/tmp/phase9-deps:/workspace/backend \
  -e OFFSEC_TEST_POSTGRES=1 backend sh -c \
  'pip install --quiet --target /tmp/phase9-deps pytest==8.4.1 httpx==0.28.1 && python -m pytest tests -q -p no:cacheprovider'
```

From `frontend/`:

```bash
pnpm install --frozen-lockfile
pnpm exec playwright install chromium
pnpm test
pnpm lint
pnpm typecheck
pnpm build
pnpm test:e2e
```

Build and E2E should be run sequentially. The E2E launcher owns its backend name
and fails if that name is already occupied. Stop any existing Next.js dev server
in this checkout before E2E, because Next.js uses a checkout-local dev lock.
The real Lab is stopped and removed after tests; start it again to resume play.

In this managed Windows session Docker/Python required elevated execution.
Package installation used the existing `../.pnpm-store` and
`NODE_USE_SYSTEM_CA=1` for the OS-trusted certificate chain. TLS verification was
not disabled. Environment-specific certificate/store settings are not committed.

Final validation also includes `git diff --check`, workbook cell/formula audit,
and verification that no temporary backend, schema or Lab resources remain.

## Bugs Found

No production defect was identified, and Phase 9 makes no production-code or
Docker architecture changes. During test authoring an overly broad Hint button
selector matched all three levels; it was narrowed to the existing accessible
button label. No assertion was removed or failing case skipped to obtain a pass.

Non-failing diagnostics: existing Starlette/AnyIO deprecation warning, pip cache
notice in the disposable container, Next.js color-environment warnings, and one
aborted proxy read during the second browser run. All asserted user flows and
browser runtime-error checks passed.

## Project status and workbook reconciliation

See [project-status-audit.md](project-status-audit.md) for ISSUE-001–029 evidence,
retained uncertainties and precise before/after changes. Updated the existing
`docs/OffSec_Lab_v0.1_WBS.xlsx`, retaining the user's Phase 8 completion data.
All five sheets, original formulas, formatting, panes, filters, tables, names,
chart structure and conditional formatting extensions are preserved.

## Security review and remaining risks

- Lab host port bindings are empty; both containers remain confined to the
  dedicated internal network, non-privileged, read-only and without host mounts.
- No socket mount, capability, host network or target exposure was added.
- Test backend reuses the existing ADR-006 backend-only socket authority and is
  published only on loopback; its extra port exists only during E2E.
- Temporary markers use the target's existing `/tmp` tmpfs. Mission content and
  player DB records are not destroyed. Cleanup is scoped to test/registered Lab
  resources; no Docker prune or broad cleanup is used.
- No real secret was introduced or printed. This review is not a repository-wide
  secret scan or proof of every external-network boundary.
- Phase 10 must assess the existing host-equivalent backend socket authority,
  ports/networks/secrets and external exposure comprehensively.
- Docker/host termination that prevents all cleanup code can leave test resources;
  inspect the named E2E backend and `phase9_e2e_*` schema after such an interruption.
  Ordinary test failure/success cleanup is implemented and verified on completed runs.
- ISSUE-002 remains incomplete under its recorded three-service Compose scope;
  the frontend currently runs separately. Documentation has remaining historical
  architecture/API examples to reconcile under ISSUE-028.

## Acceptance Criteria

| Issue | Result | Evidence |
| --- | --- | --- |
| ISSUE-023 | PASS | Existing and additional unit/API tests; real PostgreSQL suite |
| ISSUE-024 | PASS | Real API/lab/recon/reset/cleanup and runtime isolation assertions |
| ISSUE-025 | PASS | 41 frontend tests, including actual client integration and errors |
| ISSUE-026 | PASS | Real Chromium → Next.js → FastAPI → PostgreSQL → Docker flow |

Next planned testing-successor issue: **ISSUE-027 — Security Assessment**.
