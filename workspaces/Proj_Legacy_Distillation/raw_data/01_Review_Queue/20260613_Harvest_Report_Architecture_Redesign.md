# Harvest Report: Agent-Centric Architecture Redesign & Orchestration

**Date**: 2026-06-13
**Context**: `second-brain` と `life-automation` の密結合解消に向けたアーキテクチャ再設計セッション

## 1. Wisdom (セッションから得られた教訓・パラダイムシフト)
- **テクニカル分割の罠**: 「データ」と「処理」という技術的な役割で物理リポジトリを分割すると、必ずドメイン貧血症と密結合を引き起こす。
- **Agent-Centric Orchestration**: 「第3のリポジトリ（実行層）」は単なるスクリプト置き場ではなく、「AIエージェントの拠点（本社）」として機能させるべき。これが、Zettelkasten（静的DB）とライブラリ（機能）を繋ぐオーケストレーターとなる。
- **NotebookLM と Zettelkasten の両立**: ローカル（Git/Obsidian）をソースコードとし、NotebookLMを「コンパイル済み成果物」と見なす。エージェントがビルド（抽出・配備）パイプラインを回すことで、文脈の肥大化を防ぐ。
- **私とAgentの会社 (You, Inc.) メタファー**: このメタファーを通すことで、エージェント間通信、権限移譲（ガバナンス）、Human-in-the-loop の必要性がシステム課題として鮮明になった。

## 2. Tech Debt (浮き彫りになった技術的負債)
- **パスのハードコード (DIP違反)**: `life-automation` 内（テスト、SKILL.md、シェルスクリプト等）に `second-brain` へのパスがハードコードされており、インフラ層としてのカプセル化が機能していない。
- **スキルの分散**: エージェントのプロンプトやSKILL定義（`.agent/`）が、複数リポジトリに散在しており、管理・ガバナンスが効かなくなっている。

## 3. System Improvement Proposals (システム改善案 / Next Steps)
1. **リポジトリの再編**:
   - `ai-learning`, `daily-tools` の廃止・整理。
   - `agent-os`（仮）の立ち上げと、分散スキルの統合。
2. **インフラ層の抽象化**:
   - `life-automation` からハードコードされたパスを排除し、すべて引数/DIによる「情報の注入」方式にリファクタリングする。
3. **モバイル連携のThin Client化**:
   - `Task_and_Calendar_Automation` で進めている通り、モバイル側は「InputのDrop」と「コンパイル済みToday.mdのView」に徹させ、複雑な処理は全て `agent-os` 側に集約する。
4. **アーキテクチャ・レビューの自動化**:
   - 今回策定した `02_architecture_review_guidelines.md` をAIエージェントの `.cursorrules` に組み込み、自律的なガバナンスを効かせる。

---
*Generated autonomously by AntiGravity Agent based on Global Constitution Rule 8.*
