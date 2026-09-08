# OffSec Lab v0.1 Security Assessment

> Status: **Final — static and dynamic assessment complete**
>
> Assessment date: 2026-09-09 (Asia/Tokyo)
>
> Scope: OffSec Lab v0.1 and Mission 01 (`m01-recon`)

## 1. Purpose

This assessment checks whether the security boundaries around the intentionally
observable Mission 01 target are implemented as designed. The target's intended
SSH and HTTP behavior is not treated as a defect. The acceptance condition is
that no critical isolation failure exists around the Management Plane, Docker
host, Lab Plane, or external networks.

This report combines the static assessment with the user's runtime evidence.
The assessed controls passed, and no unresolved Critical or High finding
remains.

The assessment distinguishes four security concerns:

- **Intentional Mission attack surface:** SSH on TCP/22 and HTTP on TCP/80 are
  required Mission 01 learning surfaces and are not findings by themselves.
- **Lab isolation controls:** the attacker and target are restricted to the
  dedicated internal Lab network without host port publication, host mounts,
  privileged mode, host namespaces, or Docker socket access.
- **Management Plane security:** the backend API is published on loopback, runs
  with a non-root UID, is non-privileged, uses `no-new-privileges`, and limits
  Docker operations through a fixed Mission registry and fixed command paths.
- **ADR-006 Accepted Risk:** the backend Docker socket deliberately retains
  host-equivalent authority for the local single-user v0.1 MVP.

## 2. Scope

Included:

- Host port publication for the Management Plane and Mission 01.
- Mission 01 Docker network membership and external isolation.
- Attacker and target privileges, namespaces, capabilities, and root filesystems.
- Docker socket exposure and ADR-006 mitigations.
- Host bind mounts, named volumes, and `tmpfs` use.
- Direct target exposure and unnecessary Lab egress.
- Git-tracked files and reachable Git history for common secret indicators.

Excluded:

- Hardening or changing the intentionally observable Mission 01 SSH/HTTP services.
- Removing the intended attacker-to-target path.
- Replacing or revising ADR-006 in this issue.
- Dependency vulnerability, image provenance, host hardening, or a full threat model.
- Phase 11 documentation cleanup and post-v0.1 features.

### Final management-stack security state (ISSUE-002 closeout)

After this assessment, ISSUE-002 completed the originally required
three-service development stack by adding the frontend to the root Compose
project. Review of the merged final configuration confirms that this did not
change the ISSUE-027 result or the Lab security boundary:

- the frontend is published only as
  `127.0.0.1:${FRONTEND_PORT:-3000}:3000`;
- the backend remains published only as
  `127.0.0.1:${BACKEND_PORT:-8000}:8000`;
- PostgreSQL still has no host port;
- the frontend runs as the non-root `app` user, is explicitly non-privileged,
  and uses `no-new-privileges`;
- the frontend has no Docker socket, host bind mount, host network, added Linux
  capability, or membership in the Mission 01 Lab network; and
- ADR-006 socket access remains limited to the backend.

The frontend relays `/api/v1/*` over the separate Compose `management` network.
It does not join `offsec-m01-net` and does not create a browser-to-target route.
These observations are a final configuration delta review, not a rerun or
replacement of the ISSUE-027 dynamic assessment.

## 3. Trust Boundaries

```text
Browser on local host
        |
        | 127.0.0.1 only
        v
FastAPI backend ---- Docker socket ---- Docker Engine / host authority
        |              (ADR-006 accepted risk)
        | fixed Mission registry and fixed Compose operations
        v
offsec-m01-net (bridge, internal)
        |
        +---- offsec-m01-attacker ----> target-m01:22,80
        |
        +---- no host-published target port
        +---- no external gateway
```

The backend-to-Docker-socket boundary has host-equivalent authority. Controls
around the API and command construction reduce exposure but do not make the
socket a low-privilege interface.

## 4. Assessment Method

The static assessment used the following evidence:

1. Requirements, basic design, ADR-003, ADR-006, Mission 01 documentation, and
   the Phase 9 report were compared with the current implementation.
2. Both Compose models were rendered and validated with `docker compose config`.
3. Mission 01 and Lab Runner/API security-related tests were executed.
4. Dockerfiles, the fixed Mission registry, and argument-array subprocess runner
   were reviewed directly.
5. Current Git-tracked content was scanned for private-key headers and common
   provider token formats. Generic password/secret/token assignments were
   reviewed as candidates. Reachable Git history was searched with the same
   high-confidence patterns and generic assignment indicators.
6. User-provided runtime inspection results were compared with the static
   expectations for ports, networks, privileges, namespaces, mounts, the
   backend socket exception, and Lab Internet egress.
7. After the final PASS determination, the WBS workbook was updated only for
   WBS 10.1–10.7, ISSUE-027, M7, and the directly affected Summary fields.

## 5. Assessment Results

| ID | Check | Expected | Observed / Static Evidence | Dynamic Evidence | Result | Severity / Note |
| --- | --- | --- | --- | --- | --- | --- |
| SEC-001 | Host Port Exposure | No attacker/target host `PortBindings`; target 22/80 internal only; Management API on `127.0.0.1` | Rendered Lab Compose has zero published ports. Target uses only `expose: 22,80` ([compose.lab.yml](../../challenges/m01-recon/compose.lab.yml)). Management Compose publishes backend as `127.0.0.1:${BACKEND_PORT:-8000}:8000`; database publishes no port ([docker-compose.yml](../../docker-compose.yml)). Static: **PASS**. | `docker port target-m01` returned no output. Runtime inspection showed `PortBindings={}` and `Ports={"22/tcp":null,"80/tcp":null}`. | **PASS** | TCP/22 and TCP/80 are internal Mission services, not host-published ports. |
| SEC-002 | Docker Network Isolation | `offsec-m01-net`; bridge; internal; non-attachable; attacker/target only on this network; no host network | Source and rendered Compose show one `lab` network named `offsec-m01-net`, `driver: bridge`, `internal: true`, `attachable: false`; both services join only `lab`. No `network_mode: host` is present. Static: **PASS**. | Runtime: `Internal=true`, `Driver=bridge`, `Attachable=false`. Target `172.19.0.3` and attacker `172.19.0.2` belonged only to `offsec-m01-net`; both had an empty gateway. Attacker-to-target ping had 0% packet loss, and Nmap found 22/tcp SSH and 80/tcp HTTP open. | **PASS** | Intended attacker-to-target training path works inside the isolated network. |
| SEC-003 | Container Privilege | Non-privileged; private PID/IPC; `no-new-privileges`; read-only root; drop all capabilities; add only attacker `NET_RAW` and target `NET_BIND_SERVICE` | Compose sets `read_only: true`, `cap_drop: ALL`, the two documented capability exceptions, and `no-new-privileges:true`. It sets neither host PID nor host IPC mode. Dockerfiles end with `USER trainee` and `USER target`. The isolation tests passed. Static: **PASS**. | Both containers reported `Privileged=false`, `ReadonlyRootfs=true`, `CapDrop=["ALL"]`, `SecurityOpt=["no-new-privileges:true"]`, empty `PidMode`, and `IpcMode="private"`. Target added only `CAP_NET_BIND_SERVICE`; attacker added only `CAP_NET_RAW`. | **PASS** | No host PID/IPC sharing or unnecessary capability was observed. |
| SEC-004 | Docker Socket Exposure | No socket in attacker/target. Backend exception only, with local-only API, non-root, non-privileged, `no-new-privileges`, and fixed operations | Mission Compose has no volumes. Backend alone mounts `/var/run/docker.sock`; host publication is loopback, `privileged: false`, `no-new-privileges:true`, and image uses `USER app`. `LAB_REGISTRY` contains only Mission 1 and a fixed Compose path/project. The runner uses `asyncio.create_subprocess_exec` with an argument array and fixed operation methods. Static: **PASS**, subject to ADR-006 accepted risk. | Target and attacker reported `Binds=null` and `Mounts=[]`. Backend reported the read-only repository bind and read-write Docker socket bind, `Privileged=false`, `no-new-privileges:true`, host binding `127.0.0.1:8000`, and identity `uid=100(app)`, `gid=101(app)` with supplementary group 0. The root-owned group-0 socket was mode 0660. | **PASS** | Runtime matches ADR-006. Socket authority remains an **Accepted Risk**, not a separate finding. |
| SEC-005 | Host Filesystem / Volume | No attacker/target bind mount or named volume; `/tmp` may be `tmpfs`; backend repository mount is read-only under ADR-006 | Mission Compose has no `volumes`; each service has only a bounded `/tmp` `tmpfs` with `noexec,nosuid,nodev`. Backend mounts the repository at `/workspace:ro`; PostgreSQL alone uses its intended data volume. Static: **PASS**. | Both Lab containers reported `Binds=null`. Target `/tmp` was `rw,noexec,nosuid,nodev,size=32m`; attacker `/tmp` was `rw,noexec,nosuid,nodev,size=64m`. | **PASS** | The `/tmp` filesystems are tmpfs, not host directory exposure. |
| SEC-006 | Internet Exposure | No external-to-target path; no target port publication; Mission network internal; unnecessary Lab egress fails | Host publication is absent and the dedicated network is internal. ADR-003 states that internal Lab containers have no Docker external gateway. Static: **PASS** for the checked-in architecture. | Both attacker and target failed bounded requests to `https://example.com` with `curl: (6) Could not resolve host`. Runtime network evidence also showed `Internal=true` and an empty gateway. | **PASS** | No normal external egress or intended direct Internet/LAN ingress path was observed. |
| SEC-007 | Secret Scan | No real passwords, API keys, tokens, private keys, or cloud credentials in tracked content/history | No private-key header or high-confidence GitHub/AWS/Slack/Google/Stripe token pattern was found in current tracked content or reachable history. The generic scan found application password-field references and `.env.example`; review confirmed environment-variable plumbing and the placeholder `replace_with_a_local_development_password`, not a real secret. Only `.env.example` is tracked; `.env` and `.env.*` are ignored except for the example. | N/A | **PASS** | Coverage is pattern-based; no dedicated entropy/service-backed scanner was available. |

### Final PASS summary

- SEC-001 through SEC-006 passed both static assessment and the supplied runtime
  verification.
- SEC-007 passed the tracked-content and reachable-history secret scan; no
  additional dynamic check was required.
- Final result: **SEC-001 through SEC-007 PASS**.

## 6. Findings

No Critical, High, Medium, or Low finding was identified in ISSUE-027.

| Severity | Count |
| --- | ---: |
| Critical | 0 |
| High | 0 |
| Medium | 0 |
| Low | 0 |
| Informational | 0 |

## 7. Accepted Risks

### AR-001 — Backend Docker socket access (ADR-006)

The backend mounts `/var/run/docker.sock` read-write. Docker socket access
provides host-equivalent administrative authority: compromise of the backend
can permit control of Docker and, through Docker, the host.

Runtime evidence confirms that the backend uses non-root `uid=100(app)` and
`gid=101(app)`. Supplementary group 0 grants access to the root-owned,
group-0-owned socket, whose mode is 0660 (`srw-rw----`). The backend is
non-privileged, uses `no-new-privileges`, publishes the API only on
`127.0.0.1:8000`, and mounts the repository read-only at `/workspace`. The fixed
Mission registry, fixed Compose path/project, argument-array execution, bounded
operations, and timeouts further reduce exposure. These controls do **not**
neutralize or remove the Docker socket's host-equivalent authority.

ADR-006 accepts this risk only for the local, single-user v0.1 MVP. Before LAN or
Internet publication, multi-user support, or broader Docker operations, replace
direct socket access with a narrowly privileged host-side controller or a
restricted socket proxy, and record the new design and threat model in an ADR.

The socket is not authorized for the frontend, database, attacker, target, or
future challenge containers.

## 8. Residual Risks

- Static Compose review cannot prove that running containers were created from
  the current files or were not manually modified.
- The local API has no authentication by v0.1 design. Loopback binding and the
  single-user assumption are therefore security prerequisites.
- Docker's internal-network behavior and host firewall/Engine configuration are
  dependencies outside the repository definition.
- Pattern-based secret scanning can miss novel formats or low-entropy secrets.
- Image dependency vulnerabilities, build-source integrity, Docker Desktop/WSL2
  host hardening, and denial-of-service against the local host were not assessed.

## 9. Dynamic Verification

| ID | Runtime evidence | Result |
| --- | --- | --- |
| SEC-001 | Target `PortBindings={}`; container ports 22/tcp and 80/tcp were unbound; `docker port target-m01` produced no output. | PASS |
| SEC-002 | Internal bridge, non-attachable; only `offsec-m01-net`; empty gateways; attacker-to-target ping and SSH/HTTP discovery succeeded. | PASS |
| SEC-003 | Both Lab containers were non-privileged and read-only, used private IPC and non-host PID modes, dropped all capabilities, restored only their documented capability, and used `no-new-privileges`. | PASS |
| SEC-004 | No Lab bind or mount; backend exception matched ADR-006, including non-root UID, supplementary group 0, socket mode 0660, loopback API, non-privileged mode, and `no-new-privileges`. | PASS with ADR-006 Accepted Risk |
| SEC-005 | No Lab bind mount; only bounded `/tmp` tmpfs filesystems with `noexec,nosuid,nodev`. | PASS |
| SEC-006 | Attacker and target could not resolve/reach `example.com`; internal network and empty gateways were confirmed. | PASS |
| SEC-007 | No dynamic check required; static tracked-file and reachable-history scan passed. | PASS |

## 10. Conclusion

For the assessed OffSec Lab v0.1 local single-user MVP architecture, SEC-001
through SEC-007 passed. No unresolved Critical or High security finding exists,
and no Medium or Low finding was identified in ISSUE-027. Mission 01's intended
SSH/HTTP attack surface remains available only through the intended Lab path and
is not treated as a vulnerability of the surrounding platform boundary.

The backend Docker socket remains the host-equivalent ADR-006 Accepted Risk.
Its mitigations reduce exposure but do not make direct socket access safe for
LAN exposure, Internet exposure, multi-user operation, or expanded Docker
control. Those changes require architecture review and a safer boundary such as
a host-side controller or restricted proxy.

Within this stated scope, OffSec Lab v0.1 satisfies the ISSUE-027 security
acceptance criteria. This conclusion is not a claim that the application, host,
dependencies, or future architectures are universally or absolutely secure.

The merged ISSUE-002 frontend service preserves the assessed local-only model:
frontend and backend host exposure is loopback-limited, PostgreSQL remains
internal to the management network, and no Docker or Lab privilege was granted
to the frontend. ADR-006 remains an accepted host-equivalent backend risk and
must not be described as fixed or eliminated.

## Validation Record

- `docker compose -f challenges/m01-recon/compose.lab.yml config --quiet` — PASS.
- `docker compose config --quiet` — PASS. The session emitted a non-fatal access
  warning for the user's Docker client configuration file.
- Security-related pytest selection — **57 passed**, with one existing
  Starlette/AnyIO deprecation warning:
  `tests/test_m01_network.py`, `tests/test_m01_attacker.py`,
  `tests/test_m01_target.py`, `backend/tests/test_lab_runner.py`, and
  `backend/tests/test_lab_api.py`.
- Static rendered-Compose evidence — PASS for zero Lab published ports/volumes,
  dedicated Lab membership, internal bridge settings, loopback backend binding,
  non-privileged backend definition, and `no-new-privileges`.
- Secret scan — PASS within the method and limitations described above.
- User-provided Docker runtime inspection — PASS for SEC-001 through SEC-006;
  observed values are recorded in Sections 5, 7, and 9.
- WBS finalization — WBS 10.1–10.7, ISSUE-027, and M7 marked Done; Summary
  advanced to Phase 11 / ISSUE-028.
