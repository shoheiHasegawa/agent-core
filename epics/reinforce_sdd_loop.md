---
type: epic
status: completed
created: "2026-08-01"
updated: "2026-08-02"
tags: [architecture, sdd, loop_engineering]
---

# Epic: Reinforce SDD Loop (SDDループと品質ゲートの補強)

## 📖 Background (背景と課題)
core-serviceにおけるSDD/TDDの開発において、Specと実装の乖離が後から発覚する問題が起きていた。
AgentがTDDの細かなステップをスキップしたり偽装テスト（`assert True`等）を作成してしまうバイアスを物理的に防ぎ、三権分立と機械的検証を徹底する仕組みを構築した。

## 🎯 Goal (目的)
「ループエンジニアリング」を安全かつ確実に回すための「品質のハードゲート」と「機械可読な仕様（Machine-Readable Spec）」の仕組みを構築・導入する。

## 🚧 Scope (やらないこと・境界)
- 既存の全spec.mdの一括書き換え（まずは仕組みとルールの策定、テンプレート化に留める）
- LLMのモデル自体のファインチューニング

## ✅ DoD (完了条件)
1. `spec.md` の記述粒度を上げ、ハルシネーションの余地をなくすための新しいフォーマット（テンプレート）が策定されていること。 -> ✅ 完了 (`Spec_Template.md`)
2. QA Reviewerによる意味論的な反証レビューのプロンプトが強化されていること。 -> ✅ 完了 (`tdd-red-coder`, `tdd-green-refactorer`, `sdd-loop-orchestrator`)
3. Agentが手順をスキップできないようにするWorkflowのハードゲート化の設計が完了していること。 -> ✅ 完了 (`verify_loop_state.py`, `validate_sdd.py`)
4. 既存パッケージ（`mobile_vault`, `second_brain`, `task_operations`）の新標準移行と結合テスト監査の完了。 -> ✅ 完了 (114件パス, カバレッジ 92.63%)

## 🛡️ 【必須】開発・実装の制約と前提知識 (TO-BE Architecture)
このEpicの詳細な設計とタスク管理は、すべて以下のワークスペースで行われた。
👉 **Workspace**: `agent-core/workspaces/reinforce_sdd_loop/_index.md`
