# Project status audit — Phase 9

Audit date: 2026-09-08. Source precedence: current working-tree implementation and
executed tests, then local Git/merged PR history, then documents and WBS. Tests
and exact commands are recorded in [phase9-test-report.md](phase9-test-report.md).
`Done` describes verified functionality, not a claim that work has been merged to
`main`. ISSUE-022 is committed as `930a0da`, and Phase 9 is committed as
`7cbf8ec`. Both commits are included in open PR #17, which is awaiting merge to
`main`. Remote GitHub Issues/Milestones were not edited.

## Issue evidence

| Issue | Result | Implementation, history and validation evidence |
| --- | --- | --- |
| 001 Project Scaffold | Done, retained | Baseline `0fa94b3`, repository directories, AGENTS, README and Git conventions |
| 002 Docker Development Environment | In Progress, retained | Compose runs backend/DB, but its recorded scope includes frontend and WBS 2.1 requires three services; frontend is a separate Next.js process |
| 003 FastAPI Backend Foundation | Done, retained | `7391efc`; real /health and /ready plus test_health.py |
| 004 PostgreSQL Database Foundation | Done, retained | `7391efc`, database.py/Compose; real PostgreSQL migration/seed/API test |
| 005 Mission / Challenge Data Model | In Progress → Done | `304204c`, `5c4506e`, `d3ca138` plus the ISSUE-022 Hint migration committed in `930a0da`; four models, full migration round trip and constraints validated |
| 006 Mission API | Done, retained | `795827f`, routes/services/repository/schema tests and real DB/browser reads |
| 007 Challenge Answer API | Done, retained | `5c4506e`, answer service/API, normalization/invalid/locked cases and five real answers |
| 008 Progress Management | Done, retained | `d3ca138`, persistent progress and sequential completion; rollback/reanswer tests and real DB/E2E |
| 009 Mission 01 Docker Network | Done, retained | `7318eab`, dedicated internal Compose network; static and runtime isolation assertions |
| 010 Attacker Container | In Progress → Done | `7c9f665`, restricted attacker Dockerfile/Compose; actual ping, DNS, Nmap and curl |
| 011 Mission 01 Target Container | In Progress → Done | `9082d67`/`987b787`, target SSH/HTTP image; actual ports, version, HTTP title and runtime restrictions |
| 012 Lab Controller — Start | Not Started → Done | `36df3d5`, allowlisted service/runner; real Start and repeated Start |
| 013 Lab Controller — Stop / Reset | Not Started → Done | `f61a85d`, real Stop/repeat Stop and container recreation/marker removal |
| 014 Lab Status API | Not Started → Done | `2a1e63c`, state/error unit/API tests plus real target/state transitions |
| 015 Next.js Frontend Foundation | Done, retained | `2a9d2f6`; frontend build/lint/typecheck, routes and real browser |
| 016 Mission List UI | Done, retained | `1b77362`; learning/mission tests, actual selection through View Mission |
| 017 Mission Detail UI | Done, retained | `1b77362`; briefing tests and actual browser content/navigation |
| 018 Lab Control UI | Done, retained | `1b77362`; control tests and real UI Start/Reset/Stop |
| 019 Challenge UI | Done, retained | `1b77362`; wrong/correct/refresh failure unit integration and five browser answers |
| 020 Hint UI | Done, retained | `1b77362` plus existing ISSUE-022 content; three-stage disclosure verified through real API client and browser |
| 021 Mission Complete UI | Done, retained | `1b77362` plus existing ISSUE-022 learning review; backend-confirmed modal, reload and review tests |
| 022 Mission 01 Content | Done, retained | Mission 01 content, seed, hints, migration and report are committed in `930a0da`; migration/seed/five-answer and real reconnaissance/E2E passed |
| 023 Backend Tests | In Progress → Done | Current Phase 9 additions: 18 cases; 131 backend tests including PostgreSQL passed |
| 024 Lab Integration Tests | Not Started → Done | Current Phase 9 real HTTP/Docker/DNS/Nmap/HTTP/reset/cleanup test passed twice |
| 025 Frontend Tests | Not Started → Done | 3 actual-client integration tests added; all 41 frontend cases passed |
| 026 End-to-End Test | Not Started → Done | New minimal Playwright setup; full real-stack Chromium flow passed twice |
| 027 Security Assessment | Not Started, retained | Phase 9 runtime checks are not the formal assessment; comprehensive scan/review remains |
| 028 README / Documentation | Not Started → In Progress | README, ADRs and test reports exist. Security assessment documentation and stale architecture/API/setup examples still need reconciliation |
| 029 MVP Acceptance Review | Not Started, retained | No final acceptance record; dependent on security assessment/documentation |

Totals: **25 Done**, **2 In Progress** (002, 028), **2 Not Started** (027, 029).
The workbook's existing status-to-progress formulas remain authoritative for
display: Done 100%, In Progress 50%, Blocked 25%, Not Started 0%. No percentages
were estimated from issue numbers or substituted for formulas.

## WBS reconciliation

The repository's `docs/OffSec_Lab_v0.1_WBS.xlsx` is the maintained workbook.
The older workbook under `outputs/01a07f7c-4747-73f2-99f1-39626d12c54a/` was not
used to overwrite it. A byte-identical pre-edit snapshot was saved before authoring;
after the user closed Excel its hash still matched that snapshot.

| WBS IDs | Before → After | Evidence |
| --- | --- | --- |
| 2.3 | Not Started → Done | Next.js source/build and browser test |
| 3.3, 3.6 | Not Started → Done | Persisted hints and repeatable seeded content |
| 3.5 | In Progress → Done | Full PostgreSQL migration round trip and schema check |
| 5.2–5.5 | In Progress → Done | Actual attacker, SSH and HTTP validation |
| 5.6–5.8 | Not Started → Done | Actual reachability/port/service/version tests |
| 6.1–6.5 | Not Started → Done | Real lifecycle/status tests plus error/timeout/API cases |
| 9.2 | In Progress → Done | Complete backend API coverage review and success |
| 9.3–9.6 | Not Started → Done | Real Lab, frontend, E2E and reset success |
| 11.4 | Not Started → Done | Phase 9 test report now records all major test results |

WBS 9.1 was already Done and remains Done. Phase 7 and Phase 8 were already
100% and were not overwritten with older prompt status. WBS 2.1 stays In Progress
because the recorded three-service Compose criterion is unmet. WBS 11.1/11.2
stay In Progress; 11.3/11.5 and Phase 10/12 remain Not Started.

Phase 0/1 statuses remain Done: baseline governance and consolidated requirements,
basic design and ADR documents support their acceptance criteria. Several WBS
deliverable paths are planned split documents that do not exist separately; the
consolidated design is the available evidence. No task scope or acceptance
criterion was rewritten to match implementation. In particular, obsolete
architecture/API examples remain a documented ISSUE-028 gap.

## Milestones and Summary

| Item | Before → After |
| --- | --- |
| M3 Platform Foundation | In Progress → Done: frontend/backend/DB and mission/answer foundation run; this exit criterion does not require all three in Compose |
| M4 First Lab Running | In Progress → Done: actual Start → Nmap → Stop/Reset |
| M6 Testing Complete | In Progress → Done: all Phase 9 tests recorded |
| M1, M2, M5 | Done retained; no redundant status edits |
| M7, M8 | Not Started retained |
| WBS Done count | 41 → 63 of 76 |
| WBS In Progress count | 9 → 3 |
| Overall Progress | 59.8684% → 84.8684% (existing average of task progress) |
| Issue Done count | 15 → 25 of 29 |
| Milestones Done | 3 → 6 of 8 |
| Phase 2 completion | 60% → 80% |
| Phase 3 completion | 50% → 100% |
| Phase 5 completion | 12.5% → 100% |
| Phase 6 completion | 0% → 100% |
| Phase 9 completion | 16.6667% → 100% |
| Phase 11 completion | 0% → 20% (test report only) |

Summary completion formulas count Done tasks, whereas Overall Progress averages
the task progress formulas. These are intentionally different existing measures.
The workbook has no separate phase-status or milestone-percent columns; none were
invented. Added Current Phase and Next Task labels/formulas only in existing blank
Summary F15:G16 cells. They derive Phase 10 / ISSUE-027 from M6 and the issue table.
M6's obsolete next-task note now identifies ISSUE-027 Security Assessment.

## Workbook preservation and verification

Artifact Tool authored the values and recalculated all dependent formulas.
The workbook contains OOXML conditional-formatting extensions; a broad library
round trip can discard them. To respect the requested structural preservation,
only the 41 approved cell payloads and recalculated caches were transferred into
the original OOXML package. This also refreshed the existing chart's numeric
caches from its unchanged Summary references.

Verified: all original ZIP parts remain, non-cell worksheet XML is byte-identical,
all other package parts except affected chart value caches are byte-identical,
and all non-approved cell values/formulas remain unchanged. Original formula text,
styles, tables, dimensions, panes, filters, names, validation, drawings and
conditional-formatting extensions remain intact. Read-back checks compare all
edited cells and formula caches; Artifact Tool formula-error scan found none.
The Summary preview was reviewed before/after. Excel application recalculation
was not independently automated; saved formula caches were recalculated and
cross-checked against task/status counts.

## Remaining verification limits

- Remote GitHub status could not be verified; the audit does not claim to close
  remote issues or milestones.
- ISSUE-022 is committed as `930a0da`, and Phase 9 is committed as `7cbf8ec`.
  Both are included in open PR #17 and are not yet merged to `main`.
- ISSUE-002/WBS 2.1 cannot be declared Done under their current recorded scope.
- Next planned Phase 9 successor is ISSUE-027. Completing the entire v0.1 project
  also requires resolving the ISSUE-002 scope gap, ISSUE-028 and ISSUE-029.
