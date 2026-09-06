# ADR-001 — WSL2 Host上でBackendを実行する

## Status

**Superseded**

Superseded by: ADR-002 — Containerized Management Plane

## Context

OffSec LabのBackendは、Mission用Docker Labに対して以下の操作を実行する必要がある。

- Start
- Stop
- Reset
- Status取得

BackendをDocker Containerとして実行する場合、Host上のDocker Engineを操作するために、Docker SocketなどへのアクセスをBackend Containerへ与える構成が必要になる可能性がある。

しかしOffSec Labは、意図的に脆弱なTarget Containerを実行するCyber Rangeである。

そのため、Application ContainerにDocker Engineへの強い操作権限を与えることは、HostとのSecurity Boundaryを弱める可能性がある。

また、OffSec Lab v0.1では以下を前提とする。

- ローカル環境のみで利用する
- Windows 11を利用する
- WSL2 Ubuntuを利用する
- Docker Desktopを利用する
- 単一ユーザーで利用する
- Cloud Deploymentは行わない

## Decision

FastAPI BackendはDocker Container内ではなく、**WSL2 Ubuntu Host上で直接実行する**。

BackendはWSL2上からDocker CLIを利用し、Docker Desktop上で動作するMission Labを操作する。

構成は以下とする。

```text
FastAPI Backend
      ↓
LabService
      ↓
LabRunner
      ↓
Docker CLI
      ↓
Docker Desktop
      ↓
Mission Lab
```

## 置き換えに関する注記

本ADRで採用した決定は、ADR-002によって置き換えられました。

Backendの実行方式について再検討した結果、開発環境の再現性、依存関係の分離、およびOffSec Lab全体のアーキテクチャとの一貫性を高めるため、WSL2ホスト上で直接実行する方式から、Docker Compose上でコンテナとして実行する方式へ変更しました。

現在の正式なアーキテクチャ判断については、ADR-002を参照してください。

## Rationale

この方式を採用することで、Backend ContainerへDocker SocketをMountする必要がなくなる。

また、v0.1ではCloud DeploymentやMulti-user環境を必要としないため、WSL2 Host上でBackendを実行する方が構成が単純であり、MVPとして適している。

BackendとDocker操作の関係も理解しやすく、Debugも容易になる。

## Consequences

### Positive

- Docker SocketをApplication Containerへ公開する必要がない
- Docker制御経路が明確になる
- Debugが容易になる
- Docker CLIを直接利用できる
- MVPの実装量を削減できる
- HostとLabのSecurity Boundaryを理解しやすい

### Negative

- Backendを完全にContainer化できない
- WSL2への依存が発生する
- Host上にPython実行環境が必要になる
- 将来Cloud化する場合はLab orchestration方式の再設計が必要になる

## Alternatives Considered

### Backend Container + Docker Socket

採用しない。

Docker SocketへアクセスできるContainerは、Docker Engineを通じてHostへ強い操作権限を持つため。

### Docker-in-Docker

v0.1では採用しない。

Isolation手段として利用可能ではあるが、構成・運用・Debugが複雑になり、MVPとして過剰である。

### Dedicated Lab Worker

将来的な候補とする。

Multi-userやCloud Deploymentが必要になった場合に再検討する。

## Security Considerations

BackendからDocker CLIを実行する場合でも、ユーザー入力から任意のDocker Commandを実行できない設計とする。

以下は禁止する。

```python
os.system(...)
```

```python
subprocess.run(..., shell=True)
```

Mission IDはServer側のRegistryでAllowlist管理し、定義済みMissionのみ起動可能とする。

## Future Considerations

以下の機能を実装する場合は、本Decisionを再評価する。

- Cloud Deployment
- Multi-user
- Concurrent Labs
- Remote Lab Execution
- Kubernetes
- Dedicated Lab Worker

方式を変更する場合は、本ADRを書き換えるのではなく、新しいADRを作成する。