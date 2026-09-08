# Mission 01 — Reconnaissance

This directory contains the isolated Docker Compose environment for Mission 01.

## Network boundary

`compose.lab.yml` defines the dedicated `offsec-m01-net` bridge network. The
network is internal, so containers attached only to it cannot use Docker's
external gateway. The implemented attacker and target services both join only
this network, and the target publishes no host ports.

The target does not publish host ports. The intended access path is:

```text
attacker-m01 -> offsec-m01-net -> target-m01
```

## Attacker container

The attacker image contains `ping`, `nmap`, `curl`, and supporting network
utilities. It runs as the unprivileged `trainee` user with a read-only root
filesystem. Compose drops all Linux capabilities and adds back only `NET_RAW`
for network discovery. It also applies CPU, memory, and PID limits.

Build and start it from the repository root:

```bash
docker compose -f challenges/m01-recon/compose.lab.yml up --build -d attacker
docker exec -it offsec-m01-attacker bash
```

Stop the Mission 01 stack with:

```bash
docker compose -f challenges/m01-recon/compose.lab.yml down
```

## Target container

The target provides SSH on 22/tcp and HTTP on 80/tcp for service enumeration.
SSH authentication is disabled; the service exists only for protocol and
version detection. The HTTP response exposes an intentional server header,
page title, and synthetic status content for reconnaissance exercises.

The target runs as an unprivileged user with a read-only root filesystem. Its
ephemeral SSH host key is generated under `/tmp` at startup and is never stored
in the image or repository. Compose publishes no target port to the host.

Start both Mission 01 containers with:

```bash
docker compose -f challenges/m01-recon/compose.lab.yml up --build -d
```

From the attacker container, inspect the target with:

```bash
nmap -sV target-m01
curl -i http://target-m01/
```

## Validate the definition

From the repository root:

```bash
docker compose -f challenges/m01-recon/compose.lab.yml config --quiet
```

The automated tests verify that the resulting `lab` network uses the bridge
driver, has `internal` set to `true`, and has no published host ports or unsafe
container settings.

## First playable learning content (ISSUE-022)

Mission ID **1**, **Reconnaissance Fundamentals**, teaches an authorized internal
assessment of Northbridge Systems' newly deployed status portal. The theme is
Web Server Attack Surface Reconnaissance. All commands run from the existing
attacker environment against `target-m01` on the isolated lab network.

Initialize the application after building its backend:

```bash
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.seed
```

`backend/app/mission01.py` is the single authoritative source for scenario,
tasks, answers, hints, and learning explanation. `app.seed` updates Mission 1
and challenge positions 1–5 without replacing existing IDs/slugs or resetting
progress. Unexpected extra challenge positions cause a transactional failure
for review, rather than deletion of learning history. Fresh initialization
creates one mission, five challenges, and fifteen persisted hints.

The progression is Host Discovery → Port Scan → Service Enumeration → Version
Detection → HTTP Inspection. Each challenge has exactly three hints: reasoning,
technique, and a concrete command to interpret. Mission Complete provides a
learning review, also accessible through Review Learning after dismissal.

Answer formats are a reachability acknowledgement, ascending comma-separated
ports, comma-separated services in port order 22 then 80, SSH product/upstream
version without packaging metadata, and the HTML title text. Normalization
uses existing Unicode NFKC, case folding, trimming, and whitespace collapsing;
comma-separated submissions must omit spaces. Incorrect answers do not advance
progress, and locked challenges cannot be answered. No command telemetry is
collected: submissions assess reported observations, not command execution.

Mission detail adds ordered `challenges[].hints` (`id`, `level`, `content`) and
`learning_explanation`. Explicit response schemas exclude `accepted_answers`.
The frontend imports no seed or answer data. Command examples necessarily
include observed ports as parameters for subsequent enumeration; they are not
an answer-key field. To honor the issue's answer-disclosure constraint, the
Host Discovery task describes its acknowledgement word instead of printing
the canonical answer. The scenario also avoids giving the exact HTML title.

The new Alembic revision `20260908_0004` adds the Hint table (unique challenge
and level; levels 1–3) and nullable Mission learning explanation. Downgrading
to `20260906_0003` removes only these new content fields/table; upgrading and
seeding restores them. Progress and existing mission/challenge identities remain.

For the completion audit and validation results, see
[ISSUE-022 validation](../../docs/testing/issue-022-first-playable.md).
