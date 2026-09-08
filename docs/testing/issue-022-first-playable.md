# ISSUE-022 completion report

Validated locally on 2026-09-08.

## Summary and repository audit

Mission **1**, **Reconnaissance Fundamentals**, now has a reproducible scenario,
five sequential challenges, fifteen progressive hints, and a Mission Complete
learning explanation. Its theme is **Web Server Attack Surface Reconnaissance**:
an authorized internal assessment for Northbridge Systems, investigating a newly
deployed status portal only inside the isolated OffSec Lab network.

Before modification, Mission, Challenge (including backend-only accepted answers),
and Progress models and three Alembic migrations existed. Mission list/detail,
Challenge Answer, and Progress APIs already implemented public response schemas,
normalization, sequential unlocking, transaction/mission locking, and completion.
Mission Briefing, Lab Workspace/controls, ChallengePanel, HintPanel, and
MissionComplete already existed. HintPanel received an empty array; no Hint
model, content seed, or learning explanation field/rendering existed. The running
database contained no missions or challenges and was at revision 0001.

The registry already mapped numeric Mission ID 1 to the existing lab; this ID
is preserved. No second Mission 01 or parallel frontend content store was added.
The requirements file exists under its Japanese filename,
`docs/requirements/OffSec Lab v0.1 MVP要件定義書.md`; this and the basic design and
ADRs were read. ADR-006 documents the pre-existing backend-only socket exception.

## Changes

| Files | Purpose |
| --- | --- |
| `backend/app/mission01.py`, `backend/app/seed.py` | Single authoritative content source and transactional, repeatable initialization |
| `backend/app/models/hint.py`, `models/__init__.py`, `models/challenge.py`, `models/mission.py` | Persist three-level hints and nullable learning explanation |
| `backend/alembic/versions/20260908_0004_add_learning_content.py` | Reversible, deterministic schema extension |
| `backend/app/repositories/mission_repository.py` | Eager-load ordered hints, avoiding async lazy-loading during serialization |
| `backend/app/schemas/mission.py`, `backend/app/api/v1/missions.py` | Add public hints and explanation to existing detail contract; keep answers excluded |
| `frontend/lib/api/client.ts` | Add optional public content fields for compatibility with existing consumers/fixtures |
| `frontend/components/lab/ChallengePanel.tsx` | Feed the existing HintPanel the selected challenge's ordered hints; reset disclosure on challenge change |
| `frontend/components/lab/LabWorkspace.tsx`, `MissionComplete.tsx` | Remove empty placeholder hints, show learning review in existing modal, allow reopening it |
| Backend model/API tests and `test_mission01.py` | Schema, seed, constraints, API disclosures, PostgreSQL migration and complete progression coverage |
| Frontend challenge/completion tests | Per-challenge three-hint progression, reset behavior, backend learning review and reopening |
| Root and Mission README, this report | Setup, content behavior, implementation decisions, reproducible validation |

Existing WBS spreadsheet and `outputs/` changes are outside this implementation
and were left untouched. No Docker definition, target file, lab lifecycle logic,
answer normalization, or progress algorithm changed.

## Mission content (maintainer answer key)

| Order | Challenge | Canonical answer |
| --- | --- | --- |
| 1 | Host Discovery | `reachable` |
| 2 | Port Scan | `22,80` |
| 3 | Service Enumeration | `ssh,http` |
| 4 | Version Detection | `OpenSSH 9.2p1` |
| 5 | HTTP Inspection | `Northbridge Systems Status Portal` |

Every challenge has exactly three persisted levels: concept/reasoning, technique,
then a concrete attacker-side command whose output must be interpreted. Levels
1 and 2 contain no canonical answers. The learning review covers reconnaissance,
reachability versus scanning, ports as conventions, service/version evidence,
HTTP inspection, and the authorized assessment workflow. It explains that an
open port or a detected version alone does not establish a vulnerability.

The issue both requests a printed reachability acknowledgement and forbids its
canonical value in public content. The public task therefore describes the
acknowledgement word instead of printing it. The scenario avoids stating the
exact page title. Required later-stage Nmap commands still contain `22,80` as
scan parameters, as specified by the issue; this is instructional context, not
an exposed answer-key field. Answer data is never imported into frontend code.

## Database and seed

Run after building the backend:

```bash
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.seed
```

The new migration adds `hints` with unique `(challenge_id, level)`, levels bounded
to 1–3, and `missions.learning_explanation`. Seed creates Mission 1 only when
absent, updates the existing five positions, and preserves IDs, slugs, and
progress. PostgreSQL advisory locking serializes concurrent seed runs. An
unexpected extra challenge position fails the transaction rather than deleting
existing history. Initialization also advances the Mission ID sequence after
using the fixed registry ID. No schema redesign or new dependency was needed.

Migration downgrade/re-upgrade and reseeding restore the learning content while
retaining mission/challenge/progress records. Tests verify a fresh schema and
idempotent updates, including repeated seed calls in the same session.

## Automated validation

From the repository root on Windows:

```powershell
$env:PYTHONPATH='backend'
.\.venv\Scripts\python.exe -m pytest backend/tests tests -q -p no:cacheprovider
```

Result: **121 passed, 1 skipped**. The skipped test is the explicitly opt-in
PostgreSQL integration test; it passed separately below. This run includes the
existing Docker Compose/network/attacker/target security-definition tests.

PostgreSQL integration plus the entire backend suite, using a temporary test
dependency directory in a disposable management container:

```bash
docker compose run --rm --no-deps -w /workspace/backend \
  -e PYTHONPATH=/tmp/issue022-deps:/workspace/backend \
  -e OFFSEC_TEST_POSTGRES=1 backend sh -c \
  'pip install --quiet --target /tmp/issue022-deps pytest==8.4.1 httpx==0.28.1 && python -m pytest tests -q -p no:cacheprovider'
```

Result: **113 passed**. The integration test creates a unique temporary database
schema, upgrades all migrations, runs Alembic model/schema comparison, seeds,
calls the real FastAPI routes/repositories with TestClient, verifies a locked
answer is rejected, rejects incorrect answers without advancing progress,
accepts all five normalized answers sequentially, verifies final completion,
reseeds without losing progress, downgrades/upgrades the new migration, and
finally removes only its temporary schema. It never completes the player's
live Mission. Alembic logging configuration is isolated from pytest logging.

From `frontend`:

```bash
pnpm test
pnpm typecheck
pnpm lint
pnpm build
```

Results: **38 tests passed** across 11 files; typecheck, lint, and production
build passed. Existing backend deprecation warnings are non-failing.
`git diff --check` passed.

## Runtime verification

Executed against the existing target from the attacker container:

```bash
docker exec offsec-m01-attacker ping -c 4 target-m01
docker exec offsec-m01-attacker nmap -p- target-m01
docker exec offsec-m01-attacker nmap -sV -p 22,80 target-m01
docker exec offsec-m01-attacker curl -i http://target-m01
```

Observed target IP `172.19.0.2` (dynamic, not a content dependency):

- ICMP: 4 transmitted, 4 received, 0% loss.
- Full TCP range: only 22/tcp and 80/tcp open; 65,533 closed ports.
- 22/tcp: SSH, `OpenSSH 9.2p1 Debian 2+deb12u10 OffSecLab-M01`.
- 80/tcp: HTTP, `nginx 1.22.1`.
- HTTP: `200 OK`, `Server: nginx/1.22.1`.
- HTML title: `Northbridge Systems Status Portal`.

The local backend was rebuilt and initialized with migrations/seed. Live API
verification returned one Mission 1, five challenges, three hints each, a learning
explanation, and `NOT_STARTED` progress (first challenge AVAILABLE, others LOCKED).
Browser verification at `http://127.0.0.1:3000` confirmed the actual seeded
briefing, workspace, RUNNING target information, and all three successive hint
disclosures. The workspace's rendered hint layout was visually inspected.

## Security review

Runtime inspection confirmed both lab containers have `privileged=false`, empty
host port bindings, and no mounts; the lab network remains `internal=true`.
No target host ports, host networking, Docker socket mount, additional capability,
real credential, secret, or external reconnaissance target was introduced.
The pre-existing management backend socket mount remains governed by ADR-006.
Public response models exclude accepted answers. Lab Start/Stop/Reset and
backend-authoritative answer/progress behavior are reused unchanged.

## Known validation limits

The browser smoke test did not submit all five answers to the live player DB;
that complete flow was exercised through real PostgreSQL/FastAPI integration,
with completion and hint UI behavior covered by React tests. The live progress
remains fresh for the player. Start/Stop/Reset runtime operations were not
re-executed against the already-running lab in this content-only issue; their
existing tests passed and their implementation was unchanged.
