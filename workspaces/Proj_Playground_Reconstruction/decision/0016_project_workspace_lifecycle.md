# ADR 0016: Project Workspace Lifecycle

## Context
従来の `second-brain` 内にプロジェクトフォルダを置く運用では、タスクログやWIP状態のデータが永続的な知識（Permanent Notes）に混入し、God Object化してAIのコンテキストを圧迫・ハルシネーションを誘発するという深刻な課題があった。

## Decision
プロジェクトの実行状態を `second-brain` から完全に追い出し、`agent-core` 側の「一時的な作業場（Workspace）」で管理し、最終的に知識だけを抽出するライフサイクルを採用する。

### ライフサイクルとデータの流れ
1. **Epic層 (`agent-core/epics/`)**: 巨大なプロジェクトのバックログと全体像（Big Picture）を保持する。
2. **Workspace層 (`agent-core/workspaces/active/`)**: 常に「数日〜2週間以内」で完了可能なスコープに分割して生成する。ここで `progress.md` などのトランザクションデータを管理する。
3. **Harvesting & Grace Period**: Workspace完了後、Permanent Notesへのナレッジ抽出を行い、生データは一時凍結（`archive/`）へ回す。
4. **永続化と解体**: 人間がナレッジを確認した後、Workspaceは完全に削除（Teardown）される。

### Guardrails (防衛機構)
- **Amnesia Loop防止**: `progress.md` の上書きによる文脈消失を防ぐため、「なぜ失敗したか」は `decisions.md` に残し、常にGitコミットを強制する。
- **Teardown前のCold Storage**: Harvesting直後にファイルを完全削除せず、`archive/` に一時退避させることで、抽出内容のハルシネーション検証を可能にする。

## Consequences
- `second-brain` が純粋な知識の保管庫としての役割を取り戻す。
- Agentの作業領域が軽量で短期的なWorkspaceに限定されるため、コンテキストウィンドウの枯渇が防げる。
