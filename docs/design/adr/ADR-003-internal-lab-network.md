# ADR-003 — Docker Internal NetworkをLab Isolationに使用する

## Status

**Accepted**

## Context

OffSec Labでは、学習目的で意図的に脆弱なTarget Containerを実行する。

Targetが以下から直接アクセス可能な状態は避ける必要がある。

- Internet
- LAN
- Host Network上の不要なService
- 他MissionのLab Container

Mission 01では、基本的な通信経路を以下に限定する。

```text
Attacker
    ↓
Target
```

Target上ではSSHやHTTP等のServiceをListenさせるが、これらをHostや外部Networkへ直接公開する必要はない。

## Decision

Missionごとに専用Docker Networkを作成する。

Mission 01では以下のNetworkを使用する。

```text
offsec-m01-net
```

Docker Composeでは原則として以下を設定する。

```yaml
networks:
  lab:
    internal: true
```

Target ContainerではHost PortをPublishしない。

構成は以下とする。

```text
Internet
   X
   │
Target

Host
   X
   │
Target

Attacker
   │
   ▼
Target
```

## Rationale

Cyber Rangeでは、意図的に脆弱なServiceを外部へ露出させないことが重要である。

Mission単位でNetworkを分離することにより、以下を実現する。

- Target Isolation
- Mission Isolation
- External Exposure Prevention
- Reproducible Network Environment

また、プレイヤーがTargetへアクセスする経路をAttacker Container経由へ限定できる。

## Consequences

### Positive

- Vulnerable Targetの外部公開を防止できる
- Mission単位でNetworkを分離できる
- 他Missionへの不要な通信を防ぎやすい
- Network Architectureが理解しやすい
- Lab環境の再現性が向上する

### Negative

- Lab ContainerからInternetへ直接接続できない
- RuntimeでPackageをDownloadできない
- 必要なToolはImage Build時に導入する必要がある
- Internet通信が必要なMissionでは追加設計が必要になる

## Host Port Policy

Target Containerでは原則として以下を使用しない。

```yaml
ports:
```

例えば以下のようなHost Port Publishは禁止する。

```yaml
ports:
  - "8080:80"
```

TargetへのアクセスはDocker内部Networkからのみ行う。

```text
attacker-m01
      ↓
target-m01:80
```

## Build Policy

Lab実行時にInternet Accessを必要としないよう、Missionで必要なPackageやSecurity ToolはDocker Image Build時に導入する。

例：

```text
Attacker Image
├── nmap
├── curl
├── ping
└── dnsutils
```

RuntimeでのPackage Installは原則行わない。

## Mission Isolation

将来的にMissionが複数存在する場合、MissionごとにNetworkを分離する。

```text
offsec-m01-net
├── attacker-m01
└── target-m01
```

```text
offsec-m02-net
├── attacker-m02
└── target-m02
```

異なるMission間で通信できないことを基本とする。

## Future Considerations

以下のようなMissionを実装する場合は、Network Architectureを再検討する。

- OSINT
- External Service Simulation
- Supply Chain Attack
- Package Repository Attack
- C2 Simulation
- Internet-dependent Exercise

Internet Accessが必要な場合も、必要最小限の通信経路だけを許可する。

変更が大きい場合は新しいADRを作成する。