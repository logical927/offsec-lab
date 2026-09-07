# ADR-006 — Backend Docker Socket Access for the Local MVP

## Status

Accepted for v0.1

## Context

ADR-002 containerized the management plane, while the basic design expected a
WSL2-hosted backend to invoke Docker CLI without mounting the Docker socket.
The deployed backend therefore cannot implement Lab Start: a Docker client in a
container needs an Engine endpoint, and no separate host-side controller exists.

ISSUE-012 requires the containerized FastAPI backend to start the predefined
Mission 01 Compose project. Adding a separate daemon or socket proxy would add a
new service and substantially more lifecycle and deployment complexity for the
single-user, local-only MVP.

## Decision

For v0.1 only, the backend container receives:

- the Docker CLI and Compose plugin;
- a read-only mount of this repository at `/workspace`, used only for registered
  Compose files and their build contexts; and
- `/var/run/docker.sock`, with access granted through the socket's numeric group.

The Lab API accepts only a numeric Mission ID. Mission 1 maps in backend code to
`challenges/m01-recon/compose.lab.yml` and project `offsec-m01`. The runner uses
argument-array subprocess execution, a fixed operation set, and a timeout. It
does not accept a path, image, container, Docker arguments, or shell command from
the caller.

The backend remains non-root and non-privileged, uses `no-new-privileges`, and is
published only on `127.0.0.1`. The socket is not mounted into attacker or target
containers. Mission 01's internal network and lack of host port mappings remain
unchanged.

This decision is a narrow exception to the no-application-socket rule in the
basic design and ADR-002. It does not authorize socket access for the frontend,
database, attacker, target, or future challenge containers.

## Security Implications

Docker socket access is effectively host-level administrative authority. A
backend compromise could potentially control Docker and, through it, the host.
The read-only repository mount does not reduce that Docker authority.

Risk is bounded for the MVP by:

- local-only API exposure;
- a predefined Mission registry;
- no generic Docker endpoint;
- no `shell=True` or caller-controlled command arguments;
- a non-root, non-privileged backend process;
- no Docker socket in the Lab Plane; and
- fixed execution timeouts and sanitized client errors.

These controls reduce exposure but do not make Docker socket access a low-trust
boundary. The backend must remain local-only and should not process untrusted
remote traffic.

## Alternatives Considered

### Run FastAPI directly on WSL2

This avoids a socket mount but reverses ADR-002 and splits the supported
management-plane runtime. It was rejected for ISSUE-012.

### Dedicated host controller or restricted Docker socket proxy

This can create a stronger boundary, but introduces another service, protocol,
authentication/lifecycle concerns, and Compose/build API coverage. It is a
recommended post-MVP replacement, not the smallest v0.1 change.

## Follow-up

Before any LAN or Internet exposure, multi-user support, or broader Docker
operations, replace direct socket access with a narrowly privileged host-side
controller and create a new ADR and threat model.
