# ADR-004 — MVPからPostgreSQLを採用する

## Status

**Accepted**

## Context

OffSec Lab v0.1は、以下の条件を持つ小規模なMVPである。

- 単一ユーザー
- Mission 01のみ
- ローカル利用
- Authenticationなし

そのため、技術的には以下のような簡易Storageでも実装可能である。

- JSON File
- SQLite
- In-memory Storage

一方、OffSec Labでは将来的に以下のデータを管理する予定である。

- Mission
- Challenge
- Hint
- Progress
- Learning Path
- Mission Attempt
- Report

またDatabase設計そのものも、本プロジェクトにおけるBackend開発学習およびポートフォリオの対象とする。

## Decision

OffSec Lab v0.1から **PostgreSQL** を採用する。

初期Entityは以下とする。

```text
Mission
Challenge
Hint
Progress
```

Database Schema変更はMigrationによって管理する。

## Rationale

PostgreSQLを採用することで、以下の実務的なBackend技術を経験できる。

- Relational Database Design
- Primary Key
- Foreign Key
- Migration
- Repository Pattern
- Transaction
- Seed Data
- Query
- Data Integrity

OffSec Labの将来的なMission追加やLearning Progress管理にも適している。

また、将来MissionやChallengeが増えた場合でも、JSONやIn-memory方式より構造化して管理しやすい。

## Consequences

### Positive

- Mission追加へ対応しやすい
- Relationalなデータを自然に表現できる
- Foreign Key等でData Integrityを確保できる
- Migrationを利用できる
- 実務に近いBackend構成になる
- Database設計をポートフォリオへ含められる
- 将来の機能拡張に対応しやすい

### Negative

- SQLiteよりSetupが複雑になる
- PostgreSQL ServiceまたはContainerが必要になる
- Migration管理が必要になる
- Database Connection設定が必要になる
- MVPとして構成要素が増える

## Initial Entities

### Mission

Missionそのものを管理する。

主な項目：

```text
id
code
name
description
difficulty
```

### Challenge

Mission内のChallengeを管理する。

主な項目：

```text
id
mission_id
title
description
answer
display_order
```

### Hint

Challengeに紐づくHintを管理する。

主な項目：

```text
id
challenge_id
level
content
```

### Progress

Mission / Challengeの進捗を管理する。

主な項目：

```text
id
mission_id
challenge_id
status
```

## Alternatives Considered

### JSON File

採用しない。

非常に簡単である一方、MissionやChallengeのRelation、Progress更新、将来的な拡張に向かない。

### SQLite

MVPだけを考えれば有力。

しかし将来的にPostgreSQLへMigrationする可能性が高く、Database学習というプロジェクト目的も考慮して採用しない。

### In-memory Storage

Test用途では利用可能。

実際のMVP Storageとしては使用しない。

Application再起動時にProgressが失われるため。

## Design Principles

PostgreSQLを採用するが、v0.1ではSchemaを必要以上に複雑化しない。

以下はまだ実装しない。

- User
- Role
- Permission
- Achievement
- Score
- Skill Tree
- Social Feature

必要になった段階でSchemaを拡張する。

## Security Considerations

Database接続情報はRepositoryへ直接Commitしない。

以下のような値は環境変数で管理する。

```text
DATABASE_URL
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_DB
```

実Credentialは`.env`へ配置し、`.env`はGit管理対象外とする。

Repositoryには`.env.example`のみ配置する。

また、Challengeの正解値はFrontendへ返さず、Backend / Database側でのみ保持する。

## Future Considerations

以下の機能追加時にDatabase Schemaを拡張する可能性がある。

- User Account
- Learning Path
- Mission Attempt
- Achievement
- Report
- Skill
- Score
- AI Mentor History

Schema変更はMigrationによって管理する。

大幅なDatabase Architecture変更が必要な場合は、新しいADRを作成する。