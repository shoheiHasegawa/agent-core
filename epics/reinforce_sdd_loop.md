---
type: epic
status: in_progress
created: "2026-08-01"
updated: "2026-08-01"
tags: [architecture, sdd, loop_engineering]
---

# Epic: Reinforce SDD Loop (SDDループと品質ゲートの補強)

## 📖 Background (背景と課題)
core-serviceにおけるSDD/TDDの開発において、Specと実装の乖離が後から発覚する問題が起きている。
AgentがTDDの細かなステップを面倒に感じてエスケープ（`assert True`などの偽装テストや手順スキップ）を行ってしまうバイアスがあり、現在の自然言語主体の `spec.md` と `validate_sdd.py` だけでは意味論的な乖離を防ぎきれていない。

## 🎯 Goal (目的)
「ループエンジニアリング」を安全かつ確実に回すための「品質のハードゲート」と「機械可読な仕様（Machine-Readable Spec）」の仕組みを構築・導入する。

## 🚧 Scope (やらないこと・境界)
- 既存の全spec.mdの一括書き換え（まずは仕組みとルールの策定、テンプレート化に留める）
- LLMのモデル自体のファインチューニング

## ✅ DoD (完了条件)
1. `spec.md` の記述粒度を上げ、ハルシネーションの余地をなくすための新しいフォーマット（テンプレート）が策定されていること。
2. QA Reviewerによる意味論的な反証レビューのプロンプトが強化されていること。
3. （必要に応じて）Agentが手順をスキップできないようにするWorkflowのハードゲート化の設計が完了していること。

## 🛡️ 【必須】開発・実装の制約と前提知識 (TO-BE Architecture)
このEpicの詳細な設計とタスク管理は、すべて以下のワークスペースで行うこと。
👉 **Workspace**: `agent-core/workspaces/reinforce_sdd_loop/_index.md`
