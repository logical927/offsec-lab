# Mission 01 — Reconnaissance

This directory contains the isolated Docker Compose environment for Mission 01.

## Network boundary

`compose.lab.yml` defines the dedicated `offsec-m01-net` bridge network. The
network is internal, so containers attached only to it cannot use Docker's
external gateway. Future attacker and target services must join the `lab`
network.

The vulnerable target must not publish host ports. The intended access path is:

```text
attacker-m01 -> offsec-m01-net -> target-m01
```

The attacker and target containers are intentionally deferred to ISSUE-010 and
ISSUE-011. Until those services are added, the Compose file is a declarative
network definition and `docker compose up` has no workload to start.

## Validate the definition

From the repository root:

```bash
docker compose -f challenges/m01-recon/compose.lab.yml config --quiet
```

The automated network test adds a test-only probe service when rendering and
starting the stack. It verifies that the resulting `lab` network uses the
bridge driver, has `internal` set to `true`, and has no published host ports.
