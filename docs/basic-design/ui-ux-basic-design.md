# OffSec Lab v0.1 UI/UX基本設計書

## 1. 文書概要

### 1.1 目的

本書は、OffSec Lab v0.1におけるFrontend UI/UXの基本設計を定義する。

本設計では、単に見た目を整えることを目的とせず、プレイヤーが以下の一連の操作を迷わず実行できることを重視する。

```text
Missionを探す
↓
Mission内容を理解する
↓
Labを起動する
↓
対象を調査する
↓
Challengeへ回答する
↓
必要に応じてHintを利用する
↓
Missionを完了する
↓
次のMissionへ進む
```

OffSec Labは、Cyber Rangeとしての実用性、Developer Toolとしての操作性、学習ゲームとしての進捗体験を組み合わせたUIを目指す。

---

### 1.2 対象バージョン

```text
OffSec Lab v0.1
```

### 1.2.1 ISSUE-028 実装差分

本書はFrontend実装前のUI/UX設計とWireframeを含む。v0.1の実装結果では、
以下を確定状態とする。以降の将来Mission、XP値、Level構成などのWireframe例は
視覚設計資料であり、実装済み機能を示さない。

- 実装Routeは `/dashboard`、`/learning-path`、`/progress`、
  `/missions/{numericMissionId}`、`/missions/{numericMissionId}/lab` とする。
- Mission 01のHintは4段階ではなく、考え方、技術/Tool、具体的Commandの
  **3段階**とする。
- XP、Level、Achievement、複数Learning Path/Missionはv0.1で実装しない。
  Shell上のXP/LEVEL表示は値を持たないPlaceholderである。
- Browser Embedded Terminalは実装せず、WSL2から
  `docker exec -it offsec-m01-attacker bash` を使用する。
- 実装済み画面・状態・API連携の正式な説明は
  [`frontend-mvp-flow.md`](../testing/frontend-mvp-flow.md) と
  [`basic_design_v0.1.md`](../design/basic_design_v0.1.md) を参照する。

---

### 1.3 対象範囲

本書では以下を定義する。

1. Design Concept
2. Sitemap
3. User Flow
4. Screen List
5. Lab Screen Layout
6. Component List
7. UI State
8. Color / Typography
9. Responsive Policy
10. Accessibility
11. Dashboard
12. Learning Path
13. Mission Detail
14. Lab Workspace

---

### 1.4 非対象

v0.1では以下をUI/UX設計対象外とする。

- Multiplayer
- Ranking
- Achievement
- SNS機能
- Chat
- Profile customization
- AI Mentor
- Embedded Browser Terminal
- WebSocket Terminal
- Light Theme
- Marketplace
- Mobile専用Lab UI
- 高度なアニメーション演出
- リアルタイムネットワーク可視化

---

# 2. Design Concept

## 2.1 基本コンセプト

OffSec LabのUIコンセプトを以下とする。

> **Professional Cyber Range × Developer Tool × Game Progression**

UI全体は、一般的なゲーム画面よりも、セキュリティツールや開発ツールに近い操作感を持たせる。

一方で、学習継続を支援するため、

- XP
- Level
- Progress
- Mission Complete
- Learning Path

など、最低限のゲーム要素を取り入れる。

---

## 2.2 デザイン方針

| 項目 | 方針 |
|---|---|
| Theme | Dark Theme |
| 雰囲気 | Cyber Security / Developer Tool |
| 情報密度 | 中～高 |
| 操作性 | 明確かつ直接的 |
| ゲーム性 | 控えめ |
| アニメーション | 状態変化通知を中心に使用 |
| 装飾 | 必要最小限 |
| Hacker演出 | 過度に使用しない |
| Mission情報 | 最優先 |
| Lab状態 | 常に確認可能 |

---

## 2.3 デザイン上の基本原則

### Mission First

画面上では常に、

- 今どのMissionを実行しているか
- 何を達成する必要があるか

を最優先で表示する。

---

### Status Visible

以下の状態をユーザーが常に把握できるようにする。

- Mission Status
- Lab Status
- Challenge Status
- Hint Status

---

### Progressive Guidance

OffSec Labでは、最初から正解を表示しない。

ユーザーが必要に応じて段階的にHintを利用できるUIとする。

---

### Minimal Gamification

XPやLevelなどは学習継続の補助として利用する。

ゲーム演出そのものが目的にならないようにする。

---

### Security Tool Feel

UIは一般的なBusiness Dashboardよりも、

- IDE
- Terminal Tool
- Security Tool
- Developer Console

に近い操作感を意識する。

---

# 3. Sitemap

## 3.1 v0.1 Sitemap

```text
OffSec Lab
│
├── Dashboard
│
├── Learning Path
│   │
│   ├── Level 01 Linux Basics
│   ├── Level 02 Networking Basics
│   ├── Level 03 Reconnaissance
│   ├── Level 04 Web Enumeration
│   └── Level 05 Web Vulnerability Basics
│
├── Mission Detail
│
├── Lab Workspace
│
└── Progress
```

---

## 3.2 Navigation

主要NavigationはSidebarに配置する。

```text
Dashboard

Learning Path

Progress
```

MissionおよびLab Workspaceは、Learning Pathから遷移するコンテキスト依存画面とする。

そのためSidebarへ全Missionを直接表示しない。

---

## 3.3 Route設計

Frontendでは以下のRoute構成を基本とする。

```text
/dashboard

/learning-path

/missions/[missionId]

/missions/[missionId]/lab

/progress
```

例：

```text
/dashboard

/learning-path

/missions/1

/missions/1/lab
```

---

# 4. User Flow

## 4.1 基本User Flow

```text
Dashboard
    ↓
Learning Path
    ↓
Mission選択
    ↓
Mission Detail
    ↓
Start Lab
    ↓
Lab Workspace
    ↓
Recon / Enumeration
    ↓
Challenge回答
    ↓
┌─────────────────────┐
│       正解？        │
└─────────┬───────────┘
          │
      ┌───┴───┐
      │       │
     NO      YES
      │       │
    Retry   Mission Complete
      │       │
    Hint      XP獲得
      │       │
    Retry   Next Mission
```

---

## 4.2 Dashboardからの再開

進行中Missionが存在する場合、

```text
Dashboard
↓
Continue Mission
↓
Mission Detail
または
Lab Workspace
```

Labが既にRUNNINGの場合はLab Workspaceへ直接遷移可能とする。

---

## 4.3 Mission Clear後

```text
Mission Complete
↓
┌─────────────────────────┐
│ Back to Learning Path   │
│ Next Mission            │
└─────────────────────────┘
```

ユーザー自身が次の行動を選択できるようにする。

---

# 5. Screen List

v0.1では以下を主要画面とする。

| Screen | 目的 | MVP |
|---|---|---|
| Dashboard | 現在の状況と次の行動を確認する | 必須 |
| Learning Path | 学習経路とMissionを確認する | 必須 |
| Mission Detail | Missionの目的・内容を理解する | 必須 |
| Lab Workspace | 実際にChallengeへ取り組む | 必須 |
| Progress | XP・Level・完了状況を見る | 必須 |
| Profile | User情報管理 | 将来 |
| Settings | 各種設定 | 将来 |
| AI Mentor | AIによる学習支援 | 将来 |

---

# 6. 共通App Shell

## 6.1 Layout

Desktopでは以下を基本Layoutとする。

```text
┌───────────────────────────────────────────────────────────┐
│ OFFSEC LAB                           XP 420   LEVEL 4      │
├─────────────────┬─────────────────────────────────────────┤
│                 │                                         │
│ Dashboard       │                                         │
│ Learning Path   │              Main Content               │
│ Progress        │                                         │
│                 │                                         │
│                 │                                         │
│                 │                                         │
└─────────────────┴─────────────────────────────────────────┘
```

---

## 6.2 AppShell Component

```text
AppShell
├── TopBar
├── Sidebar
└── MainContent
```

---

## 6.3 推奨寸法

| 項目 | 目安 |
|---|---:|
| TopBar | 64px |
| Sidebar | 220～240px |
| Main Content | Flexible |
| Content Padding | 24～32px |
| Max Content Width | 1400～1440px |

---

# 7. Lab Screen Layout

Lab WorkspaceではDesktopの2Column Layoutを基本とする。

```text
Main Area
65～70%

Side Panel
30～35%
```

Main Areaには以下を配置する。

```text
Mission Title
Mission Objective
Challenge
Answer
Challenge Result
```

Side Panelには以下を配置する。

```text
Lab Status
Target Information
Lab Controls
Hints
```

Side Panelは可能な範囲でSticky表示とする。

ユーザーがページをスクロールしても、

- Target
- Lab Status
- Hint

を確認しやすくする。

---

# 8. Component List

## 8.1 Layout

```text
AppShell
TopBar
Sidebar
PageHeader
MainContent
ContentContainer
```

---

## 8.2 Navigation

```text
SidebarItem
Breadcrumb
Tabs
```

---

## 8.3 Generic UI

```text
Button
Card
Badge
Input
ProgressBar
Spinner
Alert
Modal
Tooltip
Toast
Skeleton
```

---

## 8.4 Dashboard

```text
ContinueMissionCard
ActiveLabBanner
LearningProgress
XPProgress
LevelBadge
```

---

## 8.5 Learning Path

```text
LearningPathProgress
LevelSection
MissionRow
MissionStatusBadge
```

---

## 8.6 Mission Detail

```text
MissionHeader
MissionBriefing
MissionMetadata
LearningObjectives
LabEnvironmentInfo
SecurityNotice
StartLabButton
```

---

## 8.7 Lab Workspace

```text
ChallengePanel
AnswerForm
ChallengeResult
LabStatusPanel
TargetInfo
LabControls
HintPanel
HintItem
MissionCompleteModal
```

---

# 9. UI State

## 9.1 Mission State

Missionは以下の状態を持つ。

```text
LOCKED
AVAILABLE
IN_PROGRESS
COMPLETED
```

| State | 意味 |
|---|---|
| LOCKED | 前提Mission未完了 |
| AVAILABLE | 実行可能 |
| IN_PROGRESS | 現在進行中 |
| COMPLETED | 完了済 |

---

### 表示例

```text
🔒 LOCKED

○ AVAILABLE

▶ IN PROGRESS

✓ COMPLETED
```

色だけで状態を表さない。

---

# 10. Lab State

Lab状態は以下を基本とする。

```text
STOPPED
STARTING
RUNNING
STOPPING
RESETTING
ERROR
```

---

## 10.1 STOPPED

```text
○ STOPPED

The lab environment is not running.

[ Start Lab ]
```

---

## 10.2 STARTING

```text
◌ STARTING

Preparing attacker and target containers...

[ Spinner ]
```

起動処理中はStart / Stop / Reset等の競合操作を無効化する。

---

## 10.3 RUNNING

```text
● RUNNING

Target
10.10.0.20

[ Stop Lab ]

[ Reset Lab ]
```

---

## 10.4 STOPPING

```text
◌ STOPPING

Stopping the lab environment...
```

---

## 10.5 RESETTING

```text
◌ RESETTING

Rebuilding the lab environment...
```

---

## 10.6 ERROR

```text
⚠ LAB ERROR

The lab environment could not be started.

[ Try Again ]
```

必要に応じて内部Error Codeを表示する。

```text
Error Code:
LAB_START_FAILED
```

内部Stack TraceなどはUser UIへ表示しない。

---

# 11. Challenge State

Challengeは以下の状態を持つ。

```text
UNANSWERED
SUBMITTING
INCORRECT
CORRECT
COMPLETED
```

---

## 11.1 UNANSWERED

```text
Which TCP port is open?

[                 ]

[ Submit Answer ]
```

---

## 11.2 SUBMITTING

```text
Checking answer...

[ Spinner ]
```

重複送信を防止する。

---

## 11.3 INCORRECT

```text
✕ INCORRECT

That doesn't appear to be the correct answer.

Review your reconnaissance results and try again.
```

正解そのものは表示しない。

---

## 11.4 CORRECT

```text
✓ CORRECT

You identified the exposed TCP port.

+25 XP
```

複数Challengeがある場合：

```text
[ Next Challenge ]
```

を表示する。

---

# 12. Hint State

Hintには以下を使用する。

```text
LOCKED
AVAILABLE
OPENED
```

---

## 12.1 Hint Level

OffSec Lab v0.1ではHintを以下の3段階とする。

### Hint Level 1 — Concept

考え方を示す。

例：

```text
Think about how you can discover services
listening on another host.
```

---

### Hint Level 2 — Technique / Tool

使用できるToolを示す。

例：

```text
A port scanning tool can help identify
listening TCP services.
```

---

### Hint Level 3 — Command

具体的なCommand例を示す。

例：

```text
nmap <target>
```

---

## 12.2 Unlock Flow

```text
Hint 1   Available
Hint 2   Locked
Hint 3   Locked
```

Hint 1閲覧後：

```text
Hint 1   Opened
Hint 2   Available
Hint 3   Locked
```

段階的に解放する。

---

# 13. Color

## 13.1 Background

```text
Primary Background
#0B0F14

Secondary Background
#111820

Card Background
#161B22
```

---

## 13.2 Border

```text
Border
#25303B
```

---

## 13.3 Text

```text
Primary Text
#E6EDF3

Secondary Text
#AAB4BE

Muted Text
#7D8590
```

---

## 13.4 Brand Accent

Primary AccentはCyanを使用する。

```text
#22D3EE
```

目的：

- Cyber Securityらしい印象
- Developer Toolとの親和性
- Dark Themeとの相性
- 他Cyber Rangeとの差別化

---

## 13.5 Semantic Color

以下の用途別Tokenを定義する。

```text
Success
Warning
Error
Info
```

具体的な色値はFrontend実装時にContrastを確認した上で決定してよい。

ただしComponent内への色値直接記述を避け、Design Tokenを利用する。

---

# 14. Typography

## 14.1 Standard UI

標準UIには以下を推奨する。

```text
Geist
```

利用例：

```text
Mission Title
Navigation
Button
Description
Status
```

---

## 14.2 Technical Information

技術情報にはMonospace Fontを使用する。

推奨：

```text
Geist Mono
```

対象：

```text
IP Address
Port
Command
Code
Container Name
Error Code
```

例：

```text
TARGET

10.10.0.20
```

`10.10.0.20`のみMono Fontとする。

---

# 15. Responsive Policy

## 15.1 基本方針

OffSec Labは、

> **Desktop First**

で設計する。

理由：

脆弱性診断学習では、

- Terminal
- Browser
- Burp Suite
- Nmap
- OffSec Lab

などを複数Windowで利用することが想定されるため。

---

## 15.2 Device Support

| Device | Policy |
|---|---|
| Desktop | Full Support |
| Laptop | Full Support |
| Tablet | Limited Support |
| Smartphone | Limited / Read-oriented |

---

## 15.3 Breakpoints

目安として以下を使用する。

```text
Desktop
>= 1280px

Laptop
>= 1024px

Tablet
>= 768px

Mobile
< 768px
```

---

## 15.4 Mobile

MobileではSidebarをDrawer等に切り替える。

ただしv0.1ではスマートフォンからの本格的なLab操作を主用途としない。

必要に応じて以下を表示する。

```text
Desktop environment recommended for lab exercises.
```

---

# 16. Accessibility

## 16.1 基本方針

WCAG 2.2 AA相当を意識した設計を行う。

---

## 16.2 Keyboard Navigation

以下のKeyboard操作を考慮する。

```text
Tab
Shift + Tab
Enter
Space
Esc
```

主要操作がMouseなしでも実行できることを目標とする。

---

## 16.3 Focus Indicator

Keyboard Focus時には明確なFocus Indicatorを表示する。

例：

```text
[ Submit Answer ]
```

TabでFocusした場合、十分視認可能なBorderまたはOutlineを表示する。

---

## 16.4 Color Onlyの禁止

状態を色だけで表現しない。

悪い例：

```text
●
```

良い例：

```text
● RUNNING
```

---

## 16.5 Error Message

Errorは原因または修正方法が分かる表現とする。

悪い例：

```text
Invalid
```

良い例：

```text
Answer must be a TCP port number between 1 and 65535.
```

---

## 16.6 Semantic HTML

可能な範囲で、

```text
nav
main
header
button
form
label
input
```

などSemantic Elementを利用する。

Clickableな操作要素を単なる`div`として実装しない。

---

# 17. Dashboard

## 17.1 目的

Dashboardは、

> **ユーザーが次に何をすればよいかを判断する画面**

とする。

分析Dashboardではない。

大量のKPIやChartは配置しない。

---

## 17.2 Wireframe

```text
┌──────────────────────────────────────────────────────────────┐
│ Dashboard                                                    │
│ Continue your security training.                             │
│                                                              │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ CONTINUE TRAINING                                        │ │
│ │                                                          │ │
│ │ Level 03 / Reconnaissance                                │ │
│ │ Mission 01                                               │ │
│ │ Find the Open Port                                       │ │
│ │                                                          │ │
│ │ Discover the exposed service on the target.              │ │
│ │                                                          │ │
│ │ Progress ███████░░░ 70%                                  │ │
│ │                                                          │ │
│ │                             [ Continue Mission → ]        │ │
│ └──────────────────────────────────────────────────────────┘ │
│                                                              │
│ Learning Progress                                            │
│                                                              │
│ Level 01 Linux Basics              ██████████ 100% ✓         │
│ Level 02 Networking Basics         ██████████ 100% ✓         │
│ Level 03 Reconnaissance            █████░░░░░  50%           │
│ Level 04 Web Enumeration           ░░░░░░░░░░   0% 🔒        │
│                                                              │
│ ┌─────────────────────┐ ┌─────────────────────┐              │
│ │ LEVEL               │ │ XP                  │              │
│ │ 4                   │ │ 420 / 500           │              │
│ └─────────────────────┘ └─────────────────────┘              │
│                                                              │
│                                      [ View Learning Path ]  │
└──────────────────────────────────────────────────────────────┘
```

---

## 17.3 表示要素

### Continue Training

```text
Current Level
Mission Number
Mission Title
Short Description
Progress
Continue Mission Button
```

---

### 初回User

Missionを一度も開始していない場合：

```text
START YOUR FIRST MISSION

Level 01
Linux Basics

[ Start Learning ]
```

---

## 17.4 Active Lab Banner

LabがRUNNINGの場合はDashboard上部に表示する。

```text
┌──────────────────────────────────────────────────────────┐
│ ● LAB RUNNING                                            │
│ Mission 01 / Find the Open Port                          │
│ Target: 10.10.0.20                         [ Open Lab ]   │
└──────────────────────────────────────────────────────────┘
```

Labの起動忘れを防止する目的も持つ。

---

# 18. Learning Path

## 18.1 目的

Learning Pathでは、

> 今どこを学習していて、次に何を学ぶか

を明確にする。

---

## 18.2 Layout

縦型Timelineを採用する。

```text
Level 01
  ↓
Level 02
  ↓
Level 03
  ↓
Level 04
  ↓
Level 05
```

横方向に大量のCardを並べるUIは原則使用しない。

---

## 18.3 Wireframe

```text
┌──────────────────────────────────────────────────────────────┐
│ Learning Path                                                │
│ Build practical offensive security skills step by step.      │
│                                                              │
│ Overall Progress                                             │
│ █████████████░░░░░░░ 34%                                    │
│                                                              │
│ ● LEVEL 01                                                   │
│ │ Linux Basics                                     COMPLETE  │
│ │                                                            │
│ ├── ✓ Mission 01 Navigation Basics                   +50 XP │
│ ├── ✓ Mission 02 Reading Files                       +50 XP │
│ └── ✓ Mission 03 Permissions                         +75 XP │
│ │                                                            │
│ ● LEVEL 02                                                   │
│ │ Networking Basics                                COMPLETE  │
│ │                                                            │
│ ├── ✓ Mission 01 IP and Ports                       +50 XP  │
│ └── ✓ Mission 02 TCP / UDP                          +75 XP  │
│ │                                                            │
│ ● LEVEL 03                                                   │
│ │ Reconnaissance                                   CURRENT   │
│ │                                                            │
│ ├── ▶ Mission 01 Find the Open Port                 +100 XP │
│ ├── ○ Mission 02 Service Enumeration                +100 XP │
│ └── 🔒 Mission 03 Version Detection                 +125 XP │
│ │                                                            │
│ ○ LEVEL 04                                                   │
│   Web Enumeration                                   LOCKED   │
└──────────────────────────────────────────────────────────────┘
```

---

## 18.4 Mission操作

AVAILABLE / IN_PROGRESS / COMPLETEDのMissionは選択可能とする。

クリックすると：

```text
/missions/[missionId]
```

へ遷移する。

---

## 18.5 Locked Mission

LOCKED Missionは選択不可とする。

HoverまたはFocus時：

```text
Complete Mission 01 to unlock this mission.
```

等の説明を表示する。

---

# 19. Mission Detail

## 19.1 目的

Mission Detailは、

> **Mission Briefing**

として扱う。

プレイヤーはLab開始前に、

- 目的
- Scope
- 学習内容
- Lab Environment

を確認する。

実務における診断前のScope / Objective確認と対応させる。

---

## 19.2 Wireframe

```text
┌──────────────────────────────────────────────────────────────┐
│ Learning Path / Level 03 / Mission 01                        │
│                                                              │
│ LEVEL 03 · RECONNAISSANCE                                    │
│                                                              │
│ Mission 01                                                   │
│ Find the Open Port                                           │
│                                                              │
│ Difficulty: EASY      XP: 100       Challenges: 1            │
│                                                              │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ Mission Briefing                                         │ │
│ │                                                          │ │
│ │ A target machine has been discovered on the lab network.│ │
│ │ Your task is to identify the exposed TCP service.       │ │
│ └──────────────────────────────────────────────────────────┘ │
│                                                              │
│ Objective                                                    │
│                                                              │
│ Identify which TCP port is open on the target machine.       │
│                                                              │
│ ──────────────────────────────────────────────────────────── │
│                                                              │
│ You will practice                                            │
│                                                              │
│ • Network reconnaissance                                     │
│ • Port scanning                                              │
│ • Reading scan results                                       │
│                                                              │
│ ──────────────────────────────────────────────────────────── │
│                                                              │
│ Lab Environment                                              │
│                                                              │
│ Attacker     Linux attacker container                        │
│ Target       Isolated target container                       │
│ Network      OffSec Lab isolated network                     │
│                                                              │
│ Security Notice                                              │
│ Perform all scanning only against the provided lab target.   │
│                                                              │
│                                             [ Start Lab → ]   │
└──────────────────────────────────────────────────────────────┘
```

---

## 19.3 Mission Detailで表示しない情報

Challengeの答えにつながる情報は表示しない。

例：

```text
Open Port
Service Version
具体的なExploit
具体的なScan結果
```

---

## 19.4 You Will Practice

Missionごとに学習対象を明示する。

例：

```text
You will practice

Network Reconnaissance
Port Scanning
Service Enumeration
```

---

## 19.5 Real-world Skill

短い実務接続情報を表示してもよい。

例：

```text
REAL-WORLD SKILL

Security engineers use reconnaissance to identify
services exposed by systems before vulnerability analysis.
```

詳細解説はMission Clear後またはLearning Documentで提供する。

---

## 19.6 Start Lab

通常：

```text
[ Start Lab → ]
```

Labが既にRUNNING：

```text
[ Open Lab → ]
```

Mission完了済：

```text
[ Replay Mission ]
```

---

## 19.7 Start後の遷移

Start Lab実行後はLab起動完了をMission Detailで待たず、

```text
Mission Detail
↓
Start Lab
↓
Lab Workspace
```

へ遷移する。

Lab Workspace上で、

```text
STARTING
```

状態を表示する。

---

# 20. Lab Workspace

## 20.1 目的

Lab WorkspaceはOffSec Labにおけるメインゲーム画面とする。

ユーザーはこの画面を確認しながらTerminal等を利用し、実際の調査・攻撃・回答を行う。

---

## 20.2 Desktop Wireframe

```text
┌────────────────────────────────────────────────────────────────────────┐
│ OFFSEC LAB          Level 03 / Mission 01           ● RUNNING         │
├──────────────────┬─────────────────────────────────────────────────────┤
│                  │                                                     │
│ Dashboard        │ Find the Open Port                                  │
│ Learning Path    │                                                     │
│ Progress         │ Identify which TCP port is exposed by the target.   │
│                  │                                                     │
│                  │ ┌───────────────────────────┐ ┌───────────────────┐ │
│                  │ │ CHALLENGE                 │ │ LAB STATUS        │ │
│                  │ │                           │ │                   │ │
│                  │ │ Challenge 1 of 1          │ │ ● RUNNING         │ │
│                  │ │                           │ │                   │ │
│                  │ │ Which TCP port is open?   │ │ Target            │ │
│                  │ │                           │ │ 10.10.0.20        │ │
│                  │ │ [____________________]    │ │                   │ │
│                  │ │                           │ │ [ Stop Lab ]      │ │
│                  │ │ [ Submit Answer ]         │ │ [ Reset Lab ]     │ │
│                  │ └───────────────────────────┘ └───────────────────┘ │
│                  │                                                     │
│                  │ ┌───────────────────────────┐ ┌───────────────────┐ │
│                  │ │ MISSION OBJECTIVE         │ │ HINTS             │ │
│                  │ │                           │ │                   │ │
│                  │ │ Discover the exposed TCP  │ │ ▸ Hint 1         │ │
│                  │ │ service on the target.    │ │ 🔒 Hint 2         │ │
│                  │ │                           │ │ 🔒 Hint 3         │ │
│                  │ └───────────────────────────┘ └───────────────────┘ │
│                  │                                                     │
│                  │ Attacker Environment                                │
│                  │                                                     │
│                  │ Open your terminal and connect to the attacker      │
│                  │ environment before investigating the target.        │
└──────────────────┴─────────────────────────────────────────────────────┘
```

---

## 20.3 Target Information

TargetはSide Panelに表示する。

```text
TARGET

10.10.0.20
```

Target IP等はMonospace Fontを使用する。

Challengeの答えにつながる以下は表示しない。

```text
Open Port
Service
Service Version
OS
Known Vulnerability
```

Missionによって意図的に公開する場合のみ例外とする。

---

# 21. Lab Controls

## 21.1 Start Lab

```text
[ Start Lab ]
```

STOPPED時のみ操作可能。

---

## 21.2 Stop Lab

```text
[ Stop Lab ]
```

RUNNING時のみ操作可能。

---

## 21.3 Reset Lab

```text
[ Reset Lab ]
```

RUNNING時のみ操作可能。

Resetは破壊的操作として確認Modalを表示する。

---

## 21.4 Reset Confirmation

```text
Reset Lab?

This will destroy the current lab environment
and recreate it from its initial state.

Any changes inside the target or attacker
containers will be lost.

[ Cancel ]

[ Reset Lab ]
```

---

# 22. Challenge Area

複数Challengeへ対応できる構造とする。

```text
Challenge 1 of 3
```

---

## 22.1 Answer Input

例：

```text
Which TCP port is open?

[                 ]

[ Submit Answer ]
```

Validationが必要な場合はFrontend側で最低限実施する。

ただし最終的な正誤判定はBackendで行う。

---

# 23. Hint Panel

Side Panel内に配置する。

初期表示：

```text
Hint 1   Available

Hint 2   Locked

Hint 3   Locked
```

Hint閲覧後：

```text
Hint 1   Opened

Hint 2   Available

Hint 3   Locked
```

---

# 24. Attacker Environment

v0.1ではBrowser Embedded Terminalは実装しない。

ユーザーはローカルTerminalからAttacker Containerへ接続する。

例：

```text
docker exec -it <attacker-container> bash
```

ただし具体的なCommandがMissionの回答につながる場合は、表示位置を考慮する。

---

## 24.1 Embedded Terminalをv0.1対象外とする理由

Browser Terminalには追加で、

- WebSocket
- PTY
- Session Management
- Container Exec
- Resize Handling
- Reconnection
- Authentication / Authorization
- Container Escape対策

などが必要になる。

MVPの目的である、

```text
Missionを選択
↓
Lab起動
↓
調査
↓
Challenge回答
↓
Mission Complete
```

の完成を優先する。

Embedded Terminalはv0.2以降の候補とする。

---

# 25. Mission Complete

最後のChallengeに正解するとMission Complete状態へ遷移する。

Mission Complete Modalを表示する。

```text
┌───────────────────────────────────────────┐
│                                           │
│                   ✓                       │
│                                           │
│          MISSION COMPLETE                 │
│                                           │
│          Find the Open Port               │
│                                           │
│               +100 XP                     │
│                                           │
│ You learned                               │
│                                           │
│ ✓ Port Scanning                           │
│ ✓ Network Reconnaissance                  │
│                                           │
│ [ Back to Learning Path ]                 │
│                                           │
│ [ Next Mission → ]                        │
│                                           │
└───────────────────────────────────────────┘
```

Mission Complete時のみ、通常画面より多少強い視覚的Feedbackを許容する。

ただし以下は原則使用しない。

- 大量のConfetti
- 強いScreen Flash
- 長時間のAnimation
- 操作不能になる演出

---

# 26. Screen Responsibility

各画面が回答すべきユーザーの疑問を以下とする。

| Screen | User Question |
|---|---|
| Dashboard | 次に何をすればいいか |
| Learning Path | 今何を学んでいて、この先何を学ぶか |
| Mission Detail | このMissionでは何をするのか |
| Lab Workspace | 今どう調査し、どう回答するのか |

画面間で役割を重複させすぎない。

---

# 27. Frontend Component Structure

概念的には以下の構造とする。

```text
AppShell
│
├── TopBar
├── Sidebar
│
├── Dashboard
│   ├── ActiveLabBanner
│   ├── ContinueMissionCard
│   ├── LearningProgress
│   └── XPProgress
│
├── LearningPath
│   ├── LearningPathProgress
│   ├── LevelSection
│   └── MissionRow
│
├── MissionDetail
│   ├── MissionHeader
│   ├── MissionBriefing
│   ├── LearningObjectives
│   ├── LabEnvironmentInfo
│   ├── SecurityNotice
│   └── StartLabButton
│
└── LabWorkspace
    ├── ChallengePanel
    ├── AnswerForm
    ├── ChallengeResult
    ├── LabStatusPanel
    ├── TargetInfo
    ├── LabControls
    ├── HintPanel
    └── MissionCompleteModal
```

---

# 28. Frontend実装方針

UIは一括実装せず、Issue単位で段階的に実装する。

推奨順：

```text
Frontend Foundation
↓
Dashboard
↓
Learning Path
↓
Mission Detail
↓
API Integration
↓
Lab Workspace
↓
Challenge / Hint UI
↓
Mission Complete / Progress
```

Lab WorkspaceはFrontendの中でも最も複雑なため、原則として単独Issueで扱う。

---

# 29. v0.1 Security UX

UI/UX上でもOffSec LabのSecurity Principleを反映する。

### Lab Targetの明示

ユーザーが実在システムを誤ってScanしないよう、対象を明確に表示する。

例：

```text
Target

10.10.0.20
```

---

### Security Notice

Mission Detailに以下のような注意事項を表示する。

```text
Perform all scanning and exploitation only
against the target provided by OffSec Lab.
```

---

### Destructive Operation

Reset等の状態破棄を伴う操作には確認を要求する。

---

### Secret Handling

Frontendへ以下を埋め込まない。

```text
Database Password
Docker Socket Information
Backend Secret
Real Credentials
Production Credentials
```

---

# 30. MVP Definition

OffSec Lab v0.1のFrontendにおいて最優先する体験は以下とする。

```text
Learning Pathを確認する

↓

Missionを選択する

↓

Mission内容を読む

↓

Labを開始する

↓

Targetを調査する

↓

Challengeへ回答する

↓

Missionを完了する
```

このFlowが正常に動作することを、追加機能やVisual Enhancementより優先する。

---

# 31. 将来拡張候補

v0.1完成後、以下を検討する。

## v0.2候補

- Embedded Terminal
- Mission Result詳細画面
- Vulnerable → Fix → Retest Flow
- Achievement
- より高度なProgress Visualization
- Command History連携
- Hint使用量に応じたXP調整

---

## 将来候補

- AI Mentor
- Multiplayer
- Ranking
- Team Lab
- Attack Path Visualization
- Network Topology
- Real-time Event Log
- Advanced Cyber Range Management

---

# 32. UI/UX Acceptance Principles

Frontend IssueのReviewでは、最低限以下を確認する。

- プレイヤーが現在のMissionを把握できる
- 次に行う操作が分かる
- Lab状態が明確に表示される
- Targetが明確に表示される
- LOCKED / AVAILABLE / RUNNING等が色だけに依存しない
- Challengeの正解を不用意にUIへ露出しない
- Hintが段階的に提示される
- Keyboard操作が可能
- Dark Themeで十分なContrastを持つ
- Mission開始から完了までのFlowを妨げない
- 不要な情報をDashboardへ追加しない
- Frontendが単なるGeneric Admin Dashboardになっていない
- OffSec Labの学習目的がUI上から理解できる

---

# 33. Design Philosophy Summary

OffSec Lab v0.1のUI/UX設計では、以下の5原則を最重要とする。

1. **Mission First**
   - ユーザーが今やるべきことを最優先で表示する。

2. **Status Visible**
   - Mission / Lab / Challengeの状態を常に把握可能にする。

3. **Security Tool Feel**
   - 一般的な管理画面ではなくCyber Range / Developer Toolとして設計する。

4. **Progressive Guidance**
   - 即座に正解を表示せず、段階的なHintで学習を支援する。

5. **Minimal Gamification**
   - v0.1ではProgressとMission Completeを実装する。XPやLevelは将来候補とし、
     ゲーム演出より実践的なSecurity Learningを優先する。

---

# 34. Conclusion

OffSec Lab v0.1では、見た目の豪華さではなく、

```text
理解する
↓
実際に操作する
↓
考える
↓
失敗する
↓
調査する
↓
成功する
↓
振り返る
```

という学習体験をUI/UXの中心に置く。

Frontendは単なるBackend操作画面ではなく、

> **ユーザーをRecon → Enumeration → Vulnerability Analysisへ導くCyber Security Learning Interface**

として設計する。

同時に、MVPでは過剰実装を避け、

> **「実際に1つのMissionを最後まで遊べること」**

を最優先とする。
