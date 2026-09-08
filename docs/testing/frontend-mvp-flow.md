# ISSUE-016–021: frontend MVP flow

## Scope and contracts

The implementation follows `docs/basic-design/ui-ux-basic-design.md`, with
the batch's explicit deferrals taking precedence over example XP values.
It uses the actual backend Pydantic schemas and numeric mission IDs.

| Operation | Endpoint |
| --- | --- |
| Mission selection | GET /api/v1/missions |
| Briefing/challenges | GET /api/v1/missions/{mission_id} |
| Progress and completion | GET /api/v1/progress |
| Target and lab state | GET /api/v1/labs/{mission_id}/status |
| Start | POST /api/v1/labs/{mission_id}/start |
| Stop | POST /api/v1/labs/{mission_id}/stop |
| Reset | POST /api/v1/labs/{mission_id}/reset |
| Answer | POST /api/v1/challenges/{challenge_id}/answers |

The answer body is `{"answer":"learner input"}`, limited to 200 characters
by the existing backend contract. Answer values and matching remain on the
backend. The frontend does not import models, seed data, or accepted answers.

## Implementation choices

- Domain components sit between thin route pages and shared UI primitives.
  The typed client owns HTTP calls; no state framework or dependency was added.
- Next.js relays same-origin API calls to a configured local backend. This
  avoids CORS changes and browser-visible backend configuration. Frontend
  start/dev scripts bind to loopback because the relay can invoke Lab controls.
- Lab action responses use lowercase terminal states. The UI normalizes them,
  then retrieves status to obtain target information. STARTING, STOPPING and
  RESETTING during a submitted operation describe the pending request, not a
  fabricated backend job. STARTING/STOPPING returned by GET status are polled
  every three seconds, at most 20 times, and stop at terminal state/unmount.
- A failed or timed-out write has an uncertain result: controls require a
  status refresh before another Lab action. A disconnected browser does not
  cancel Docker work. Initial reads and polling are aborted on unmount.
- Challenge availability comes from Progress. Correct answers trigger a new
  Progress read, and only a COMPLETED mission in that response opens the
  completion dialog. A failed read offers explicit retry and cannot unlock
  the next challenge or claim mission completion.
- Mission NOT_STARTED maps to AVAILABLE. The current backend has no mission
  prerequisite/lock contract; listed missions remain selectable. MissionRow
  supports a locked presentation for future supplied availability data, tested
  with fixtures. No prerequisites or later missions are invented.
- The current Mission API has no hints, difficulty, separate objectives, or
  skill summary fields. Briefing/Objective use its description; completion
  lists actual challenge titles. HintPanel accepts typed data and reveals only
  the requested sequential prefix. Production supplies an empty list.
- Next Mission requires a later actual listed mission with NOT_STARTED or
  IN_PROGRESS in backend progress. If discovery fails or no candidate exists,
  Back to Learning Path remains available.
- Native modal dialogs provide an inert background and keyboard interaction,
  with initial focus, Escape cancellation and focus restoration. Next Challenge
  moves focus to its updated heading. Status text does not depend on color.
- Progress refreshes on route entry and after correct answers; it is not
  continuously synchronized across browser tabs. The Dashboard independently
  checks listed mission lab statuses and shows confirmed running labs.

## Automated checks

Run from `frontend/`:

```bash
pnpm lint
pnpm typecheck
pnpm test
pnpm build
```

Run `git diff --check` from the repository root.

| Issue | Focused tests |
| --- | --- |
| 016 | learning.test.tsx, mission-row.test.tsx: loading, errors/retry, empty data, first action, resume, navigation, locked row, active lab |
| 017 | mission.test.tsx: briefing mapping, safe errors, security notice, lab navigation |
| 018 | lab.test.tsx: Start/Stop/Reset, duplicate prevention, confirmation, cancel/Escape, focus restoration, failures, bounded polling, terminal cleanup/unmount |
| 019 | challenge.test.tsx: generic answers, duplicates, incorrect/correct feedback, next challenge/focus, resume, progress failure, empty content |
| 020 | hints.test.tsx: arbitrary hint count, sequential disclosure, semantic keyboard controls, missing data, changed identities |
| 021 | completion.test.tsx: completion only after refreshed progress, persisted completion on reload, real next mission |
| Shared | api.test.ts: all paths/methods, request body, sanitized errors, abort and timeout |

Existing AppShell, UI primitive, and required-route tests remain intact.
All component tests mock API calls; no unit test invokes Docker.

Final results (2026-09-08): lint passed with zero warnings; typecheck passed;
36 tests passed across 11 files; production build passed for all required
routes; `git diff --check` passed. No dependencies were added, and no commits
or merges were made. Temporary browser-fixture and preview servers were stopped.

## Browser fixture procedure

The test-only API uses in-memory state and never contacts PostgreSQL or Docker.
Its `fixture-pass` value is a synthetic UI test input, not a Mission 01 answer.
There are no imports from this fixture into the production application.

In one terminal, from `frontend/`:

```bash
node tests/manual-api.mjs
```

In another PowerShell terminal, from `frontend/`:

```powershell
$env:API_BASE_URL = 'http://127.0.0.1:8001'
pnpm dev --port 3001
```

Or from WSL:

```bash
API_BASE_URL=http://127.0.0.1:8001 pnpm dev --port 3001
```

Visit `http://127.0.0.1:3001/dashboard`. Follow Learning Path → Mission →
Lab. Start, open/cancel the Reset dialog using Escape, then confirm Reset.
Submit an incorrect value, then `fixture-pass`, choose Next Challenge and
submit `fixture-pass` again. Confirm Mission Complete, return to Workspace,
stop the lab, and visit Learning Path and Progress. Reopen the workspace to
verify recorded completion. Restart the fixture API to clear its memory.
Stop both test servers when finished.

## Manual verification, 2026-09-08

- Real local backend: mission list returned `[]`; Dashboard displayed the
  intended empty state. No database content or progress was modified.
- Fixture API: full navigation, start/running target, reset/cancellation,
  incorrect/correct answers, two-challenge progression, completion dialog,
  stop, completed path, Progress, and reopening completion passed.
- Reset dialog focused Cancel; Escape restored focus to Reset Lab.
- Desktop Learning Path, Briefing, Workspace, and completion dialog inspected.
- At 390px viewport, Progress and Workspace remained readable; measured body
  content width equaled client width (375px excluding scrollbar). Existing
  compact navigation scrolls horizontally within its own region.
- Invalid nonnumeric mission URL displayed the framework 404 page.

## Security review and limitations

No Docker, backend, database, network, capability, host-port or socket-mount
configuration was changed. ADR-006's existing backend-only socket exception
remains; no browser/frontend socket access was added. No secrets, dangerous
HTML rendering, external scripts, telemetry, or production answer data were
introduced. Upstream error bodies are never shown in the UI.

Real seeded-Mission/Docker end-to-end execution was not verified in this batch:
the running database has no missions. Fixture success validates frontend HTTP
integration and UX, not Docker lifecycle or PostgreSQL persistence. Hint
keyboard tests use native button semantics in jsdom; no full screen-reader
audit was performed. The existing TopBar's XP/LEVEL dashes are unpopulated.

Deferred: real Mission 01 hints, full Mission 01 content, Embedded Terminal,
AI Mentor, XP/Level, and later Learning Path content.
