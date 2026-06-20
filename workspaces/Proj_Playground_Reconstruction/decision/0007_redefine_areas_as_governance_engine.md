# ADR 0007: Redefine 20_Areas as Governance & Persona Engine

## Date
2026-06-13

## Context
従来のPARAメソッドにおける `20_Areas`（責任領域）は、人間のための「維持すべき標準・ルール」の置き場所として機能していた。しかし、Agent-Centricなアーキテクチャへの移行に伴い、「普遍的な知識（Permanent Notes）」と「動的な実行機能（Agent OS / Workspace）」が分離された結果、`20_Areas` がシステム全体において果たすべき役割が曖昧になっていた。また、実行層である `.agent` ディレクトリが依然として `second-brain` 内に混在しており、ドメイン境界に摩擦（Friction）が生じていた。

## Decision
1. **`20_Areas` の再定義**: `20_Areas` を、各部門Agent（CEO, CIO, CFO等）の「ガバナンス・エンジン」および「ペルソナ（System Prompt）のソースコード」として再定義する（DDDにおけるドメインルール層）。
2. **Context Harnessing（文脈の注入）**: エージェント（実行層）は、起動時に自身が管轄する `20_Areas/[部門]/` の `README.md`（ペルソナ定義）と `Policies/`（制約・方針）を動的に読み込み、自身のSystem Promptとして組み込むアーキテクチャとする。
3. **記載粒度とコンテキストエンジニアリング**:
   - ポリシーは1ファイル1テーマ（マイクロポリシー）に分割し、AgentがRAGで必要な制約のみをピンポイントで引き出せるようにする。
   - 過去の履歴（ADR）は持たず、常に「最新のSSOT（Single Source of Truth）」のみを記述する。
   - ルール追加・変更時は必ず直下に `↳ *[Why(根拠)]*:` を記載し、コンテキストの局所性（Locality）を担保する。
4. **役割の境界（Areas vs Workflows vs Skills）**:
   - `20_Areas` (ドメイン層): 「何をすべきか、なぜか、何をしてはならないか（宣言的制約）」。
   - `.agent/workflows/` (オーケストレーション層): 「どう協調して進めるか（手続的ロジック）」。
   - `.agent/skills/` (インフラ層): 「APIや単一タスクをどう実行するか（単一機能）」。

## Consequences

### Positive
*   Agentの行動原則や制約を人間が自然言語（Markdown）で修正するだけで、即座にAgentの振る舞いが変わる「プログラマブルな組織」が実現する。
*   ルールとその背景（Why）が密結合するため、AgentのハルシネーションやContext Pollution（コンテキスト汚染）が劇的に減少する。
*   システムにおける「ドメイン（ビジネスルール）」と「アプリケーション（実行エンジン）」の境界が明確になる。

### Negative
*   `second-brain` と `play_ground` を跨ぐ「コンテキストの動的結合」の仕組み（Agent OS側の実装）が必要となる。
*   現在の `second-brain/.agent/` に残存する実行系を、上位の `play_ground/.agent/` または `agent-core` に物理的に移行しなければならない（マイグレーションコスト）。
