# AGENTS.md

## Project Name

OffSec Lab

## Project Purpose

OffSec Lab is a local cybersecurity training platform designed to teach vulnerability assessment and penetration testing through hands-on exercises.

The platform provides intentionally vulnerable or observable lab environments inside isolated Docker networks.

The project has two primary goals:

1. Build a practical cybersecurity learning environment.
2. Use the development process itself to learn software engineering, infrastructure, networking, Docker, Python, Web development, and security.

The application must prioritize safety, reproducibility, maintainability, and learning value.

---

# Architecture Baseline

## Frontend

- Next.js
- TypeScript

## Backend

- Python
- FastAPI

## Database

- PostgreSQL

## Lab

- Docker
- Docker Compose

## Development Environment

- Windows 11
- WSL2
- Ubuntu
- Docker Desktop

## Lab Control

The FastAPI backend runs on the WSL2 host and controls Docker through the Docker CLI.

Application containers MUST NOT receive direct access to the Docker socket.

---

# Required Documents

Before implementing any issue, read the relevant project documents.

At minimum, read:

```text
docs/requirements/mvp_requirements_v0.1.md
docs/design/basic_design_v0.1.md
```

Also read any relevant ADRs under:

```text
docs/design/adr/
```

When an Issue explicitly references another design document, read that document before implementation.

---

# Development Principles

## Small Changes

Implement only the scope required by the current Issue.

Do not implement unrelated future functionality.

Do not perform large architectural refactoring unless the Issue explicitly requires it.

---

## Vertical Slice Development

Prefer completing a small end-to-end user flow over building large isolated subsystems.

The MVP priority is:

```text
Mission Display
→ Lab Start
→ Target Discovery
→ Challenge Answer
→ Mission Complete
```

---

## Keep the MVP Small

The following are NOT part of v0.1 unless explicitly added by a later requirement:

- Authentication
- Multiple users
- Multiplayer
- Cloud deployment
- Internet hosting
- Browser-based terminal
- AI Mentor
- XP system
- Skill tree
- Ranking
- Active Directory
- Privilege Escalation
- SQL Injection lab
- XSS lab
- IDOR lab

Do not introduce infrastructure for these features prematurely.

---

# Security Rules

Security requirements are mandatory.

## Vulnerable Lab Isolation

Intentionally vulnerable targets MUST NOT be exposed directly to the public Internet.

Target containers should normally exist only inside dedicated Docker lab networks.

Use Docker internal networks where appropriate.

---

## Host Port Exposure

Target containers MUST NOT publish ports to the host unless explicitly required by an approved design decision.

Avoid:

```yaml
ports:
  - "80:80"
```

for vulnerable Target containers.

Attacker containers should access Targets through the Docker lab network.

---

## Docker Socket

Never mount:

```text
/var/run/docker.sock
```

into:

- frontend
- backend containers
- attacker containers
- target containers

unless an explicit architecture decision replaces ADR-002.

---

## Privileged Containers

Do not use:

```yaml
privileged: true
```

without an explicit approved requirement.

Prefer minimum Linux capabilities.

---

## Host Network

Do not use:

```yaml
network_mode: host
```

for Lab containers.

---

## Host Mounts

Do not mount unnecessary host directories into Lab containers.

Never mount:

```text
/
```

or sensitive host paths into Challenge containers.

---

## Secrets

Never commit:

- passwords
- API keys
- access tokens
- private keys
- production credentials

Use:

```text
.env.example
```

for configuration examples.

Ensure:

```text
.env
```

is ignored by Git.

Challenge credentials must always be synthetic.

---

## Command Execution

Never construct shell commands by concatenating user-controlled input.

Avoid:

```python
os.system(...)
```

Avoid:

```python
subprocess.run(..., shell=True)
```

Prefer argument arrays.

Example:

```python
subprocess.run(
    ["docker", "compose", "-f", compose_file, "up", "-d"],
    check=True,
)
```

Mission IDs received from APIs must be resolved through a server-side allowlist or registry.

Users must never be allowed to supply arbitrary Compose paths or arbitrary shell commands.

---

# Backend Rules

Use a layered structure where practical:

```text
API
↓
Service
↓
Repository
↓
Database
```

Lab management should use:

```text
API
↓
LabService
↓
LabRunner
↓
Docker CLI
```

Keep FastAPI route handlers thin.

Business logic belongs in Services.

Database access belongs in Repositories.

Docker command execution belongs in the Lab Runner.

---

# Frontend Rules

The frontend is responsible for presentation and user interaction.

Do not place authoritative security or validation logic only in the frontend.

Challenge answers must never be included in Mission API responses.

The backend is authoritative for:

- Challenge answer validation
- Progress updates
- Lab lifecycle
- Mission completion

---

# Database Rules

Use migrations for schema changes.

Do not manually depend on an undocumented local database state.

Seed data should be reproducible.

MVP entities include:

```text
Mission
Challenge
Hint
Progress
```

Avoid unnecessary schema complexity.

---

# Challenge Structure

Challenges should be isolated under:

```text
challenges/
```

Example:

```text
challenges/
└── m01-recon/
    ├── compose.lab.yml
    ├── attacker/
    │   └── Dockerfile
    ├── target/
    │   ├── Dockerfile
    │   └── files/
    └── README.md
```

A new Mission should ideally be added without large changes to the core platform.

---

# Mission Registry

Only predefined Mission configurations may be started.

Conceptually:

```python
LAB_REGISTRY = {
    "m01": {
        "compose_file": "challenges/m01-recon/compose.lab.yml",
        "project_name": "offsec-m01",
    }
}
```

Reject unknown Mission IDs.

---

# Testing Rules

Every functional change should include appropriate tests.

Run relevant tests before completing an Issue.

Testing layers:

```text
Unit
API
Integration
E2E
Security
```

At minimum:

- new business logic requires Unit Tests
- new API endpoints require API Tests
- Docker Lab changes require Integration validation
- security-sensitive Docker changes require security verification

Do not delete or weaken existing tests merely to make a change pass.

---

# Error Handling

Do not expose:

- Python stack traces
- raw shell commands
- environment secrets
- sensitive host paths

to the frontend.

Return structured application errors.

Example:

```json
{
  "error": {
    "code": "LAB_START_FAILED",
    "message": "Failed to start the lab."
  }
}
```

Detailed errors may be written to local development logs.

---

# Logging

Useful events should be logged.

Examples:

```text
LAB_START
LAB_STOP
LAB_RESET
LAB_ERROR
CHALLENGE_COMPLETED
MISSION_COMPLETED
```

Do not log secrets.

---

# Coding Quality

Code should prioritize:

1. Correctness
2. Security
3. Readability
4. Simplicity
5. Testability
6. Maintainability

Avoid unnecessary abstractions.

Avoid speculative generalization.

Do not add dependencies without a concrete reason.

---

# Documentation Rules

When implementation changes architecture, behavior, setup, or security assumptions, update the relevant documentation.

Potential documents:

```text
README.md

docs/requirements/
docs/design/
docs/security/
docs/testing/
docs/design/adr/
```

Do not silently change architecture without documentation.

---

# Architecture Decision Records

Major architecture changes require an ADR.

Examples:

- replacing PostgreSQL
- changing Docker isolation
- introducing Docker Socket access
- introducing Kubernetes
- adding Cloud deployment
- replacing external terminal access
- changing Lab execution model

Create a new ADR rather than rewriting historical ADR decisions.

---

# Git Rules

Use focused commits.

Recommended commit prefixes:

```text
feat:
fix:
docs:
test:
refactor:
chore:
```

Do not mix unrelated work into a single commit.

Suggested branch format:

```text
feature/issue-001-project-scaffold
```

---

# Issue Completion Requirements

Before marking an Issue complete:

1. Confirm all Acceptance Criteria.
2. Run relevant tests.
3. Review security implications.
4. Confirm no unrelated files were changed.
5. Update documentation if necessary.
6. Summarize implementation.
7. Report tests executed and results.
8. Report any remaining limitations.

---

# Learning Requirement

OffSec Lab is also a learning project.

Prefer clear and explainable implementations over clever or overly abstract implementations.

When making a non-obvious implementation choice, document why it was selected.

The final project should be understandable enough that the Product Owner can explain:

- what the component does
- why it exists
- how it works
- its security implications
- how it is tested