# OffSec Lab v0.1 MVP要件定義書

## 1. 文書概要

### 1.1 文書名

OffSec Lab v0.1 MVP要件定義書

### 1.2 対象バージョン

**OffSec Lab v0.1**

### 1.3 目的

本書は、OffSec Labの最初の実行可能バージョンである **v0.1 MVP** において実装する機能・品質・セキュリティ要件、および実装対象外範囲を明確化することを目的とする。

v0.1では機能量を増やすことよりも、

**「1つのMissionを最初から最後まで実際にプレイできること」**

を最優先とする。

---

# 2. MVPゴール

OffSec Lab v0.1のゴールは以下とする。

> ユーザーがWeb UI上からMissionを選択し、隔離されたDocker Lab環境を起動し、実際のセキュリティツールを使用してTargetを調査し、Challengeを達成し、Mission Completeまで到達できること。

v0.1では以下の一連の流れが成立していることを必須とする。

```text
OffSec Lab起動
    ↓
Mission一覧表示
    ↓
Mission詳細確認
    ↓
Lab起動
    ↓
Target起動
    ↓
Attacker環境から調査
    ↓
Challenge達成
    ↓
達成判定
    ↓
Mission Complete
    ↓
Lab停止 / 初期化
```

---

# 3. MVP対象ユーザー

v0.1では単一ユーザー利用を前提とする。

想定ユーザー：

- セキュリティ初学者
- Linux基本操作経験あり
- ネットワーク基礎知識あり
- 脆弱性診断・ペンテスト未経験または初学者
- ローカルPC上でDockerを利用可能

v0.1では複数ユーザー利用は対象外とする。

---

# 4. MVP Learning Scope

v0.1では、最初のPlayable Missionとして以下を採用する。

## Mission 01 — Reconnaissance

### 学習目的

対象ホストのAttack Surfaceを調査する基本的な流れを理解する。

### 学習項目

- Host Discovery
- Port Scan
- Service Enumeration
- Version Detection
- HTTP確認
- Attack Surface整理

### 使用候補ツール

- ping
- nmap
- curl

### Mission Scenario

ユーザーは脆弱性診断担当者として、顧客からWebサーバの調査を依頼された。

提供されている情報はTarget IPのみ。

ユーザーは対象ホストを調査し、

- 稼働しているPort
- Service
- Version
- Web Server情報

を特定する。

---

# 5. Mission 01 Challenge構成

Mission 01は以下のChallengeで構成する。

## Challenge 01

### Host Discovery

Targetが到達可能であることを確認する。

完了条件：

Targetへネットワーク的に到達可能であること。

---

## Challenge 02

### Port Scan

Targetで公開されているPortを確認する。

完了条件：

指定されたOpen Portをユーザーが特定する。

初期想定：

- 22/tcp
- 80/tcp

ただし最終的なPort構成は詳細設計時に確定する。

---

## Challenge 03

### Service Enumeration

Open Port上で稼働しているサービスを特定する。

完了条件：

HTTP / SSH等、Missionで要求されるサービスを特定する。

---

## Challenge 04

### Version Detection

サービスのVersion情報を取得する。

完了条件：

対象サービスの想定Version情報を取得する。

---

## Challenge 05

### Web Inspection

HTTPサービスへアクセスし、基本情報を取得する。

確認対象候補：

- HTTP Status
- Server Header
- Title
- Response Body

完了条件：

Mission Engineが定義した情報をユーザーが回答できる。

---

# 6. 機能要件

## FR-001 Mission一覧表示

システムは利用可能なMission一覧を表示できること。

v0.1ではMission 01のみでもよい。

表示項目：

- Mission ID
- Mission Name
- Difficulty
- Learning Category
- Status

例：

```text
Mission 01
Reconnaissance
Difficulty: Easy
Status: Not Started
```

---

## FR-002 Mission詳細表示

ユーザーはMission詳細を確認できること。

表示項目：

- Scenario
- Objective
- Learning Goals
- Target概要
- Challenge一覧
- Hint利用可否

---

## FR-003 Lab起動

ユーザーはMission画面からLab環境を起動できること。

Lab起動時に必要なContainerが起動されること。

最低構成：

```text
Attacker Container
Target Container
```

---

## FR-004 Lab状態表示

システムはLabの状態を表示できること。

最低限以下の状態を持つ。

- STOPPED
- STARTING
- RUNNING
- STOPPING
- ERROR

---

## FR-005 Lab停止

ユーザーはLabを明示的に停止できること。

停止時にMission用Containerが終了すること。

---

## FR-006 Lab Reset

ユーザーはLab環境を初期状態へResetできること。

ResetによってChallenge中に変更された状態を初期化できること。

---

## FR-007 Target情報表示

Mission開始後、必要最低限のTarget情報を表示すること。

例：

```text
Target IP:
10.10.0.10
```

Target IP以外の情報はMission内容に応じて隠す。

---

## FR-008 Challenge進捗表示

各Challengeについて以下の状態を保持する。

- LOCKED
- AVAILABLE
- COMPLETED

v0.1では順番にChallengeを進める方式とする。

---

## FR-009 Challenge回答

Challengeによってはユーザーが回答値を入力できること。

例：

```text
Which TCP port is running HTTP?

Answer:
80
```

---

## FR-010 Challenge判定

入力された回答を正解データと比較し、正誤判定できること。

正解：

```text
Challenge Complete
```

不正解：

```text
Incorrect
```

を返す。

---

## FR-011 Mission Complete判定

すべての必須Challengeを完了した場合、MissionをComplete状態に変更すること。

---

## FR-012 Hint表示

ChallengeごとにHintを表示できること。

v0.1では最低3段階とする。

### Hint 1

考え方

### Hint 2

使用する技術またはツール

### Hint 3

具体的なコマンド例

---

## FR-013 Learning Explanation

Mission完了後、今回利用した技術について簡単な解説を表示する。

最低限：

- 何を行ったか
- なぜ必要か
- 実務ではどこで使われるか

---

## FR-014 Mission Progress保存

MissionおよびChallengeの進捗状態を保存できること。

v0.1ではローカル単一ユーザーのみ対象とする。

---

# 7. Attacker Environment要件

## AR-001

Attacker環境はLinuxベースとする。

---

## AR-002

最低限以下のツールを利用可能とする。

- ping
- nmap
- curl

---

## AR-003

AttackerからTargetへ接続可能であること。

---

## AR-004

AttackerからHost OSへの不要なアクセスは禁止する。

---

## AR-005

Attackerからインターネットへのアクセスは原則不要とする。

必要性が発生した場合は設計レビューを行う。

---

# 8. Target Environment要件

## TR-001

TargetはDocker Containerとして構築する。

---

## TR-002

TargetはAttackerからアクセス可能であること。

---

## TR-003

Targetは意図したPortのみListenする。

---

## TR-004

Mission 01では、Port ScanおよびService Detectionが可能なサービスを配置する。

候補：

- SSH
- HTTP

---

## TR-005

Version Detectionによって確認可能な情報を意図的に提供する。

---

## TR-006

Mission終了後にTargetを初期状態へ戻せること。

---

# 9. Frontend要件

## UI-001

Web BrowserからOffSec Labへアクセス可能であること。

---

## UI-002

最低限以下の画面を用意する。

1. Home
2. Mission List
3. Mission Detail
4. Active Mission
5. Mission Complete

---

## UI-003

Active Mission画面では最低限以下を表示する。

- Mission名
- Scenario
- Target IP
- Challenge
- Hint
- Answer入力
- Lab Status

---

## UI-004

デザインはMVPではシンプルでよい。

優先順位：

1. 操作性
2. 情報の分かりやすさ
3. 機能完成
4. 見た目

---

# 10. Backend API要件

BackendはFrontendおよびLab Controllerに対して必要なAPIを提供する。

想定API例：

```text
GET    /missions
GET    /missions/{id}

POST   /labs/{mission_id}/start
POST   /labs/{mission_id}/stop
POST   /labs/{mission_id}/reset

GET    /labs/{mission_id}/status

POST   /challenges/{id}/answer

GET    /progress
```

API仕様の詳細は基本設計で決定する。

---

# 11. Database要件

v0.1では以下の情報を保存する。

最低限のEntity候補：

## Mission

- id
- name
- description
- difficulty

## Challenge

- id
- mission_id
- title
- description
- answer
- order

## Hint

- id
- challenge_id
- level
- content

## Progress

- mission_id
- challenge_id
- status

過剰な正規化はMVPでは行わない。

---

# 12. Lab Controller要件

Lab ControllerはMission用Docker環境を管理する。

最低限以下を実行可能とする。

- Start
- Stop
- Reset
- Status

v0.1では1Missionのみ同時起動可能とする。

---

# 13. 非機能要件

## NFR-001 対応環境

初期対応：

- Windows 11
- WSL2
- Docker Desktop

を想定する。

---

## NFR-002 Browser

Chromium系Browserを優先対象とする。

例：

- Google Chrome
- Microsoft Edge

---

## NFR-003 起動性

README記載の手順からローカル環境で起動できること。

理想：

```bash
docker compose up
```

または同等の簡易手順。

---

## NFR-004 再現性

別環境でも可能な限り同一構成を再現できること。

設定値は環境変数化する。

---

## NFR-005 ログ

最低限以下をログとして確認できること。

- Backend起動
- API Error
- Lab Start
- Lab Stop
- Lab Error

---

## NFR-006 エラー処理

Container起動に失敗した場合などに、ユーザーへERROR状態を表示すること。

---

## NFR-007 保守性

Frontend / Backend / Lab / Challengeを可能な限り分離する。

Challenge追加時にPlatform全体を大きく修正しなくても済む構造を目指す。

---

# 14. セキュリティ要件

本要件はMVPにおいても必須とする。

## SEC-001

意図的に脆弱なTargetをInternetへ直接公開してはならない。

---

## SEC-002

Challenge NetworkはDocker内部ネットワークとして構築する。

---

## SEC-003

Hostへ公開するPortは必要最小限とする。

---

## SEC-004

Target用Containerでは不要なHost Mountを使用しない。

---

## SEC-005

Docker SocketをTarget ContainerへMountしてはならない。

---

## SEC-006

privileged Containerは原則禁止とする。

必要となった場合は設計レビューを必須とする。

---

## SEC-007

実在する認証情報、API Key、Token等をChallenge内で使用しない。

---

## SEC-008

`.env`等の秘密情報をGit RepositoryへCommitしない。

`.env.example`を用意する。

---

## SEC-009

Target ContainerからHostおよびProduction環境へ不要なアクセスを許可しない。

---

## SEC-010

Mission ResetによりTargetを既知の状態へ戻せること。

---

# 15. テスト要件

## TEST-001

Frontendが正常起動すること。

---

## TEST-002

Backend APIが正常起動すること。

---

## TEST-003

Databaseへ正常接続できること。

---

## TEST-004

Lab StartによってAttacker / Target Containerが起動すること。

---

## TEST-005

AttackerからTargetへ接続できること。

---

## TEST-006

Targetで想定したPortのみOpenしていること。

---

## TEST-007

Nmapによって想定Serviceを取得できること。

---

## TEST-008

Challenge回答の正解・不正解が正しく判定されること。

---

## TEST-009

全Challenge完了時にMission Completeになること。

---

## TEST-010

Lab Reset後にTargetが初期状態へ戻ること。

---

## TEST-011

Lab Stop後にMission用Containerが停止すること。

---

# 16. ドキュメント要件

v0.1までに最低限以下を作成する。

```text
docs/
├── planning/
│   └── project_proposal.md
│
├── requirements/
│   └── mvp_requirements_v0.1.md
│
├── design/
│   ├── basic_design.md
│   └── architecture.md
│
├── security/
│   └── security_design.md
│
└── testing/
    └── test_plan_v0.1.md
```

詳細設計文書は必要に応じて追加する。

---

# 17. MVP対象外

以下は **v0.1では実装しない**。

## Authentication

- Login
- User Registration
- Password Reset
- OAuth

単一ユーザー前提のため不要。

---

## Multiplayer

実装しない。

---

## Cloud Deployment

AWS / Azure / GCP等への公開は行わない。

---

## Internet公開

v0.1はローカル利用のみ。

---

## Ranking

実装しない。

---

## Achievement

実装しない。

---

## Skill Tree

実装しない。

---

## XP System

v0.1では必須としない。

Progressのみ管理する。

---

## AI Mentor

v0.1では実装しない。

Hint Systemで代替する。

---

## Embedded Browser Terminal

v0.1では必須としない。

ユーザーはローカルTerminalまたはAttacker Containerへ接続して操作する。

---

## Active Directory

対象外。

---

## Privilege Escalation

v0.1では対象外。

---

## Exploitation

v0.1では本格的なExploitは扱わない。

まずReconnaissanceのLearning Flow完成を優先する。

---

## Vulnerability Reporting

正式な診断報告書機能はv0.1対象外。

---

# 18. MVP受入基準

以下をすべて満たした場合、**OffSec Lab v0.1 MVP完成**とする。

## AC-001

OffSec Labをローカル環境で起動できる。

## AC-002

Mission 01を画面から選択できる。

## AC-003

Mission詳細を確認できる。

## AC-004

Labを開始できる。

## AC-005

AttackerからTargetへアクセスできる。

## AC-006

実際のNmapを利用してPort Scanできる。

## AC-007

Service Enumerationを実施できる。

## AC-008

Challengeへ回答できる。

## AC-009

正解時にChallengeがCompleteになる。

## AC-010

すべてのChallenge完了時にMission Completeとなる。

## AC-011

Hintを利用できる。

## AC-012

Labを停止できる。

## AC-013

LabをResetできる。

## AC-014

脆弱なTargetがInternetへ公開されていない。

## AC-015

主要な機能についてテスト結果を記録できる。

## AC-016

READMEから第三者がシステム構成と起動方法を理解できる。

---

# 19. v0.1完成イメージ

ユーザー体験として最低限以下が成立していること。

```text
OffSec Lab

        ↓

Mission 01
Reconnaissance

        ↓

Start Lab

        ↓

Target
10.10.x.x

        ↓

Attacker

$ nmap -sV 10.10.x.x

        ↓

22/tcp OpenSSH
80/tcp nginx

        ↓

Challenge Answer

HTTP Port?
> 80

        ↓

Correct!

        ↓

全Challenge完了

        ↓

MISSION COMPLETE
```

この一連の動作を実際のDocker Network上で実行可能であることを、OffSec Lab v0.1の最重要成果とする。

---

# 20. 次工程

本要件定義確定後、以下の順に開発を進める。

```text
MVP要件定義
    ↓
基本設計
    ↓
システム構成設計
    ↓
セキュリティ設計
    ↓
WBS
    ↓
Issue分割
    ↓
Codex実装
    ↓
テスト
    ↓
MVP完成
```

WBSでは本要件のFR / NFR / SEC / TEST / ACを基準としてタスクを分解する。