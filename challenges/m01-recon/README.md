# Mission 01 — Reconnaissance

This directory contains the isolated Docker Compose environment for Mission 01.

## Network boundary

`compose.lab.yml` defines the dedicated `offsec-m01-net` bridge network. The
network is internal, so containers attached only to it cannot use Docker's
external gateway. The attacker service joins this network; the future target
service must join the same network without publishing host ports.

The vulnerable target must not publish host ports. The intended access path is:

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

## Validate the definition

From the repository root:

```bash
docker compose -f challenges/m01-recon/compose.lab.yml config --quiet
```

The automated tests verify that the resulting `lab` network uses the bridge
driver, has `internal` set to `true`, and has no published host ports or unsafe
container settings.
