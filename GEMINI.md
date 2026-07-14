# 🌍 Global Constitution: GEMINI.md

ここは You_Inc システムの最上位ルート環境である。
Agentは以下の境界と絶対安全ルールを厳守し、適切なリポジトリへルーティングせよ。

## <global_rules_and_safety>
1. 【言語】思考・応答など全アウトプットにおいて日本語（Japanese）を徹底せよ。
2. 【Git安全装置】破壊的・大規模操作前は必ず事前に Commit し、復元可能にせよ。
3. 【Shell安全装置】シェル実行時は `set -e` や `&&` を用い、エラー時即時停止させよ。
4. 【Leave No Trace】一時ファイルは `.gitignore` された `scratch/` 等で使用し自律破棄せよ。
5. 【Session Handoff & Wisdom Extraction】セッション終了時の進捗・申し送りは `agent-core/skills/session-manager/SKILL.md` のルールに従い `progress.md` と `handoff_*.md` を用いて行うこと。プロジェクトの枠を超えた普遍的な教訓（Wisdom）の原石が得られた場合のみ、 `second-brain/90_Meta/Templates/Sense_Making_Template.md` を用いて `second-brain/20_Sense_Making/` へ蒸留せよ。
6. 【Agentic OS Protocol (初動と完了の儀式)】タスク着手時は、必ず対象ディレクトリの `AGENT.md` や関連 `SKILL.md` を読み込み、`task.md` の Phase 0 として「ルールに基づくテスト/実装プロセス」を明記せよ。また、実装完了の条件として、独立したReviewer Agentの承認または自動テスト（pytestカバレッジ等）のパスログの提出を必須とする。自動テストのない独断での完了報告は不適合とする。
7. 【職務分離の原則 (Separation of Duties)】Tier 1 Agentは、`core-service/src` 配下のプロダクションコードを自ら直接編集してはならない。コード変更は必ず仕様(Spec)を定義し、サブエージェント(Implementer/Tester等)に委譲して実行させよ。
</global_rules_and_safety>

## <jit_routing>
- 👉 `agent-core/`: AIの司令塔・運用層。システム構成図やタスク（Epic）の指示はここの `AGENT.md` を見よ。
- 👉 `core-service/`: ステートレスな機能工場。実際の機能実装・コーディングはここのローカルルールに従って行え。
- 👉 `second-brain/`: ナレッジベース。知識や過去の記録が必要な場合はここを探せ。
</jit_routing>

## <philosophy_and_tradeoff>
Agentic OS における設計および実装（SKILLの設計から機能開発まで）において、以下のトレードオフ裁定原則を全エージェントに適用する。

1. **【安全装置による局所防御の免除】**
   第2条（事前コミットによる復元担保）がシステムレベルで機能していることを前提とし、実行時の不確実性（エスケープ漏れ等）を過剰に恐れてはならない。
   インジェクション対策等のために一時ファイルを生成するような「局所的な安全策」は、第4条（Leave No Trace）に反しシステムのステート（ゴミ）を汚すため原則禁止する。常にインメモリやステートレスでシンプルな設計を最優先せよ。
</philosophy_and_tradeoff>
