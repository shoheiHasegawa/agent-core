# Harvest Report: レガシー環境からのアーキテクチャ統合と移行完了

**Date**: 2026-06-20
**Context**: `life-automation-legacy`, `daily-tools-legacy`, `second-brain-legacy` の旧環境から、新生アーキテクチャ（`agent-core`, `core-service`, `second-brain`）への完全移行フェーズ（Phase 02 / Phase 03）の完了記録。

## 🧠 教訓・得られた知見 (Accumulated Wisdom)

1. **Inbox Bankruptcy (自己破産) の有効性**:
   - 長期間蓄積された未処理のメモやアイデア群（約90件）を新環境のInboxにそのまま持ち込まず、「Legacy_Inbox」としてアーカイブに一括退避させるアプローチを採用した。
   - 新環境の認知負荷を下げ、綺麗な状態からAgentic OSを稼働させる上で非常に有効な手段だった。
   - 過去のゴミ（古いADRやPJ残骸）も思い切って破棄することで、RAG検索におけるハルシネーション要因（ノイズ）を未然に防ぐことができた。

2. **Agentic OS における「5つのコア領域」への再編**:
   - 旧環境の「CxO（8部門）」体制は、一人社長＋Agentの環境下ではオーバーヘッドが大きすぎた。
   - 今回の移行を機に、エージェントのドメイン（タスク管轄）に基づく「5つのコア領域（Executive, Operations, Engineering, Wealth, Wellness）」に再定義した。
   - これにより、「誰（どのAgent）が、どの領域の情報を正本（SSOT）として参照するのか」というシステム構造とディレクトリ構造が完全に一致した。

3. **レガシー実装の「参考アーカイブ化」**:
   - 古いテンプレートに依存したAgentの `.agent/skills/` や `workflows/` を無理にそのまま動かそうとせず、「後日の要件定義・再実装のための参考書」として `40_Archives/Legacy_Agent_Reference/` へ退避させた判断は適切だった。
   - 新しいAPIや `core-service` を前提としたクリーンな再実装が促進される。

## ⚠️ 技術的負債・今後の課題 (Tech Debt)

1. **20_Areas ドキュメントのリライト**:
   - 旧CxOフォルダから5つのコア領域へファイルを物理移動させたが、ドキュメント内の表現は旧体制（CxOメタファー）のままとなっている。
   - 各Agentがプロンプト内で参照する前に、文脈をAgentic OS向けに修正（マージ・リライト）する必要がある。
2. **孤児画像のクレンジング**:
   - `99_System/Attachments` を `90_Meta/Attachments/` にそのまま移行したため、使われていない画像データが大量に残存している可能性がある。後日クレンジングスクリプトの実行が必要。
3. **レガシー自動化ツールの再実装**:
   - 破棄・退避とした `verify_knowledge.py` などの自動化スクリプトや旧スキル群について、新生 `core-service` と `agent-core` の連携による再実装タスクがバックログとして残っている。

## 💡 システム改善案 (System Improvement Proposals)

*   **RAG検証テストの実施**: 大量の不要ファイルを破棄したことで、新 `second-brain` のRAG精度が大きく向上しているはず。早期に検索テストを行い、期待通りに必要な知識（Zettelkastenや新Areasのルール）だけが抽出されるか検証する。
*   **新旧ルールのマージエージェント稼働**: `20_Areas` に集められた旧ポリシー群を、「新しい Agent 用の Instruction（SKILL.md や RULES.md など）」として自動変換・再構築する専用のワークフローを組むとスムーズ。
