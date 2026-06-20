# ADR 0005: Decouple Projects and Knowledge Vault (V2)

## Date
2026-06-13

## Context
従来のアーキテクチャでは、`second-brain` (旧 second-brain) 内の `10_Projects` ディレクトリに、進行中のタスクリストや進捗ログ、決定事項が蓄積されていた。これは「静的な知識の永続化」と「動的な状態の管理」という異なるドメインを混在させるGod Object化を引き起こし、Agentのコンテキスト枯渇（アンチパターン）を招いていた。

また、初期の改善案では「プロジェクト終了後に一時作業場を完全削除する」としていたが、これでは「抽出された教訓に対する人間による文脈検証（Fact-Grounding）」が不可能になるという新たな課題（Teardownの不可逆性）がピアレビューにより指摘された。

## Decision
1. **`10_Projects` の廃止と分離**: `second-brain` から実行領域を撤廃し、実行機能は `agent-core` (Agent OS) に「一時的なWorkspace」として分離する。
2. **Epic層の導入**: 2週間のスコープ制約でWorkspaceを立ち上げるため、上位階層でのBig Pictureのトラッキングを行う Epic 管理層を `agent-core/epics/` に新設する。
3. **Grace Period (猶予期間)**: プロジェクト完了時の Harvesting 後、直ちに Workspace を完全削除せず、`agent-core/workspaces/archived/` に一時凍結（Cold Storage化）させる。
4. **Sense-Making の独立**: ユーザーが抽出物に自分らしさを吹き込むための前室として、`second-brain` トップレベルに `01_Sense_Making/` を新設する。
5. **WIP制限**: `01_Sense_Making/` の未処理キューが一定数を超えた場合、新規Workspaceの立ち上げをブロックする。
6. **Agentの自己圧縮（Amnesia防止）**: `progress.md` は上書き運用とするが、過去の失敗（Why NOT）は必ず `decisions.md` に移譲させ、健忘症ループを防ぐ。

## Consequences

### Positive
*   知識（Vault）と状態（HQ）がDDDの境界に沿って完全に分離され、システムの純度と拡張性が最大化される。
*   Agentのコンテキストが常にクリーンに保たれ、推論精度が向上する。
*   Grace Period と WIP 制限により、人間とAIの協働における認知負荷の破綻（Cognitive Overload）をシステム的に防ぐことができる。

### Negative
*   アーキテクチャが複数リポジトリ（Vault と HQ）にまたがるため、現在何が進行中かを統合的に俯瞰するダッシュボード機能（Agent OS側のCLIやUI）の開発が急務となる。
