# ADR-002: Management Planeのコンテナ化

## Status

Accepted

---

## Context

OffSec Lab v0.1では、Management Planeとして以下のコンポーネントを構成する予定です。

- Backend API
- Database
- 将来的なWeb UI
- Mission管理
- Hint管理
- ユーザー進捗管理
- XP / Level
- Lab Control
- Challenge判定

ADR-001では、BackendをWSL2ホスト上で直接実行する方式を採用していました。

しかし、Issue 002で開発環境を構築する過程で、BackendとPostgreSQLをDocker Compose上で実行する構成の方が、OffSec Labの開発方針および将来のアーキテクチャに適していると判断しました。

特にOffSec Labでは、今後Challenge用のコンテナや隔離ネットワークを多数扱う予定であり、Management Planeについてもコンテナを前提とした実行モデルに統一することで、環境差異を抑えながら再現性の高い構成を維持できます。

---

## Decision

OffSec LabのManagement Planeは、Docker Composeを使用してコンテナ上で実行します。

少なくともv0.1では、以下をDocker Compose管理下に置きます。

- FastAPI Backend
- PostgreSQL

BackendはWSL2ホスト上で直接実行せず、専用のDockerコンテナとして実行します。

PostgreSQLもDockerコンテナとして実行し、Backendとの通信にはDocker Composeで構成された内部ネットワークを使用します。

基本構成は以下とします。

```text
Windows Host
    │
    │ HTTP
    ▼
Docker Desktop / WSL2
    │
    └─ Management Network
        │
        ├─ backend
        │   └─ FastAPI
        │
        └─ db
            └─ PostgreSQL
```

Backendのみ、ローカル開発用として必要なHost Portを公開します。

v0.1では以下を基本とします。

```text
127.0.0.1:8000
```

PostgreSQLの5432/tcpはHostへ公開せず、Management Network内部からのみ利用します。

---

## Rationale

### 1. 開発環境の再現性

BackendをHost上で直接実行する場合、以下のHost環境差異の影響を受けやすくなります。

- Pythonバージョン
- pipパッケージ
- 仮想環境
- PATH
- OS設定
- ローカル依存ライブラリ

Backendをコンテナ化することで、実行環境をDockerfileとして定義でき、開発者ごとの差異を小さくできます。

---

### 2. 依存関係の分離

FastAPIおよびその依存ライブラリをHostへ直接インストールする必要がなくなります。

Backendの実行環境をコンテナ内に閉じることで、Host環境への影響を減らします。

---

### 3. Challenge Planeとの一貫性

OffSec Labでは今後、意図的に脆弱なChallenge環境をDockerコンテナとして構築する予定です。

そのため、

```text
Management Plane
Challenge Plane
```

の両方についてDockerを基本単位として扱うことで、アーキテクチャ全体の一貫性を保ちやすくなります。

---

### 4. ネットワーク分離

Docker Networkを利用することで、BackendとPostgreSQL間の通信をHostネットワークから分離できます。

PostgreSQLをHostへ直接公開せず、

```text
backend -> db:5432
```

の通信だけを許可する構成を取りやすくなります。

これはOffSec Labのセキュリティ原則である、

- 不要なHost Portを公開しない
- 最小限の通信経路のみ許可する
- 脆弱なChallenge環境と管理系を分離する

という考え方とも一致します。

---

### 5. ポートフォリオとしての再現性

OffSec Labは学習用途だけでなく、セキュリティおよびインフラ設計のポートフォリオとしても使用します。

Docker Composeによって実行環境をコードとして定義することで、

```bash
docker compose build
docker compose up -d
```

を基本とした再現可能な開発環境を提示できます。

---

## Consequences

### Positive

- 開発環境の再現性が向上する
- Host環境への依存が減る
- BackendとDatabaseの依存関係を明確にできる
- Docker Networkによる通信分離が可能になる
- Challenge Planeとのアーキテクチャ上の一貫性が高まる
- CI/CDへ展開しやすい
- 他の開発環境へ移行しやすくなる

---

### Negative

- Docker DesktopおよびWSL2への依存が増える
- Docker Engineが利用できない場合、Backendも起動できない
- DockerfileやDocker Composeの理解が必要になる
- コンテナログやネットワークを含む追加のトラブルシューティング知識が必要になる
- Host上で直接実行する方式よりも、初期構築の要素が増える

Issue 002のRuntime Validationでは、実際にDocker DesktopのLinux Engineが利用できず、BackendおよびPostgreSQLの起動検証が一時的に停止しました。

このことからも、コンテナ化による再現性の向上と引き換えに、Docker Runtime自体が新たな依存コンポーネントになることを認識する必要があります。

---

## Security Considerations

Management Planeでは、以下を原則とします。

- PostgreSQLをHostへ直接公開しない
- Backendの公開Portを必要最小限にする
- ローカル開発時のBackend公開先は原則 `127.0.0.1` とする
- Docker Socketを不用意にBackendへmountしない
- `privileged: true` を使用しない
- SecretをDockerfile、Composeファイル、ソースコードへ直接記述しない
- `.env` はGit管理対象外とする
- 実在する認証情報を使用しない
- Challenge Planeとは将来的にNetworkを分離する

特に以下のDocker Socketは、Lab Control機能を実装するまでManagement Planeへ提供しません。

```text
/var/run/docker.sock
```

Docker Socketの利用が必要になった場合は、権限境界およびHostへの影響をThreat Modelで評価した上で、別途Architecture Decisionを行います。

---

## Alternatives Considered

### Option A: WSL2ホスト上でBackendを直接実行する

#### Advantages

- 構成が単純
- Backendのデバッグが容易
- Docker Engine停止時でもBackend単体を動作させやすい

#### Disadvantages

- Python環境がHostへ依存する
- 開発者間で環境差異が発生しやすい
- Dependency管理がHost側へ漏れる
- Docker中心となるOffSec Lab全体の構成と実行モデルが分かれる

この方式はADR-001で採用しましたが、本ADRによって置き換えます。

---

### Option B: BackendとPostgreSQLをDocker Composeで実行する

#### Advantages

- 実行環境の再現性が高い
- 依存関係をコンテナ内へ隔離できる
- Docker Networkを利用できる
- Challenge Planeとの整合性が高い
- CI/CDとの親和性が高い

#### Disadvantages

- Docker Runtimeへの依存が発生する
- コンテナ特有のトラブルシューティングが必要

### Decision

Option Bを採用します。

---

### Option C: Kubernetesを利用する

#### Advantages

- 高度なコンテナオーケストレーション
- Network Policy等を活用できる
- 将来的な大規模環境へ拡張しやすい

#### Disadvantages

- v0.1の規模に対して過剰
- 学習・運用コストが高い
- MVP完成を遅らせる
- ローカルCyber Rangeとして不要な複雑性を持ち込む

MVPでは採用しません。

---

## Implementation

Issue 002で以下を実装しました。

- Docker ComposeによるManagement Plane
- FastAPI Backend Container
- PostgreSQL Container
- Docker内部Management Network
- PostgreSQL healthcheck
- Backendの非root実行
- `GET /health`
- BackendからPostgreSQLへの接続確認
- PostgreSQL Host Port非公開
- Backendのlocalhost限定公開

Runtime Validationでは以下を確認しました。

- Docker Image Build成功
- Backend Container起動成功
- PostgreSQL Container起動成功
- PostgreSQL healthcheck成功
- `GET /health` がHTTP 200を返却
- BackendからPostgreSQLへ接続成功
- PostgreSQLのHost Port非公開
- Compose停止成功

---

## Supersedes

ADR-001

ADR-001で採用していた「BackendをWSL2ホスト上で直接実行する」という決定を、本ADRによって置き換えます。

---

## Related

- Issue 001 — Repository Foundation
- Issue 002 — Development Environment
- OffSec Lab v0.1 MVP要件定義書
```