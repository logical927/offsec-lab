# ADR-005 — v0.1ではExternal Terminalを使用する

## Status

**Accepted**

## Context

TryHackMe等のCyber Rangeでは、Browser内Terminalを利用できるUXが提供されることがある。

OffSec LabでもBrowser Terminalを導入すれば、以下を1画面で利用できる。

```text
Browser
├── Mission
├── Hint
├── Challenge
└── Terminal
```

しかしBrowser Terminalを安全に実装するためには、少なくとも以下の機能・設計が必要になる。

- WebSocket
- PTY
- Terminal Session Management
- Process Lifecycle Management
- Command Streaming
- Container Session Mapping
- Authentication Boundary
- Timeout
- Error Recovery
- Resource Control

v0.1の目的はTerminal Emulatorを開発することではない。

最優先事項は以下のLearning Flowを完成させることである。

```text
Mission
   ↓
Lab Start
   ↓
Security Tool
   ↓
Challenge
   ↓
Mission Complete
```

## Decision

OffSec Lab v0.1ではBrowser Terminalを実装しない。

ユーザーはWSL2 TerminalからAttacker Containerへ接続する。

標準Entry Pointとして以下のScriptを提供する。

```bash
./scripts/enter-lab.sh m01
```

Script内部では、定義済みMission IDからAttacker Containerを特定し、接続する。

概念例：

```bash
docker exec -it offsec-m01-attacker bash
```

## Rationale

External Terminal方式を採用することで、Terminal関連の複雑な実装をMVPから除外できる。

その結果、開発リソースを以下へ集中できる。

- Mission Engine
- Challenge System
- Lab Controller
- Docker Isolation
- Learning Content

また、ユーザーが実際のLinux Terminalを使用するため、以下の学習にもつながる。

- Shell操作
- Linux CLI
- Security Tool操作
- Command History
- Terminal Environment

## Consequences

### Positive

- MVPの実装量を大幅に削減できる
- Security Surfaceを小さくできる
- WebSocket実装が不要
- PTY実装が不要
- Session Managementが不要
- 実際のLinux Terminal操作を経験できる
- Security Toolの利用体験が実環境に近くなる
- Mission Engine開発へ集中できる

### Negative

- BrowserとTerminalを行き来する必要がある
- TryHackMeほど統合されたUXではない
- Docker / WSL2 Terminalの基本操作が必要
- ユーザー体験として多少手順が増える

## User Flow

v0.1では以下の操作Flowとする。

```text
Browser
   │
   ├── Mission確認
   ├── Challenge確認
   └── Target IP確認
         │
         ▼
WSL2 Terminal
         │
         ▼
./scripts/enter-lab.sh m01
         │
         ▼
Attacker Container
         │
         ├── ping
         ├── nmap
         └── curl
         │
         ▼
Browser
         │
         ▼
Challenge回答
```

## Script Design

ユーザーが毎回Docker Container名を覚える必要がないよう、接続用Scriptを提供する。

例：

```bash
./scripts/enter-lab.sh m01
```

Scriptでは、ユーザー入力をそのまま任意のDocker Commandへ連結しない。

定義済みMission IDから接続対象Containerを決定する。

概念：

```text
m01
 ↓
Mission Registry
 ↓
offsec-m01-attacker
 ↓
docker exec
```

未知のMission IDは拒否する。

## Alternatives Considered

### xterm.js + WebSocket

将来的な候補とする。

v0.1では実装量およびSecurity Complexityが大きいため採用しない。

### Hostから直接Security Toolを実行

採用しない。

例：

```bash
nmap TARGET
```

をHostから直接実行する方式。

この方法では、Attacker環境の再現性やMission Network Isolationが弱くなる。

Security ToolはAttacker Container内部から使用する。

### SSHでAttackerへ接続

v0.1では採用しない。

SSH ServerをAttacker Containerへ追加すると、以下の追加要素が必要になる。

- Authentication
- SSH Configuration
- Credential Management
- Port Exposure
- Key Management

MVPでは`docker exec`を利用する方が単純である。

## Security Considerations

Attacker ContainerはLab Network内部へ配置する。

原則として以下は禁止する。

```yaml
privileged: true
```

```yaml
network_mode: host
```

Docker SocketもMountしない。

```text
/var/run/docker.sock
```

必要なLinux Capabilityがある場合は、Missionごとに必要最小限のみ追加する。

また、接続Scriptから任意のContainerへ接続できないよう、Mission IDとContainer名の対応はAllowlistで管理する。

## Future Considerations

v0.2以降でBrowser Terminalを再検討する。

導入する場合は最低限以下を設計する。

- PTY Lifecycle
- WebSocket Connection
- Session Isolation
- Container Mapping
- Timeout
- Resource Limits
- Process Cleanup
- Escape Prevention
- Command Logging Policy
- Authentication / Authorization

Browser Terminalを採用する場合は、本ADRを変更するのではなく、新規ADRを作成する。