---
type: epic
status: in_progress
issue: "TBD (Corporate Routine Automation)"
created: "2026-11-02"
---

# Epic Workspace: corporate_routine_automation

## 🎯 Goal (WHY & WHAT)
- **対象 Issue**: TBD (Corporate Routine Automation)
- **目的 (WHY)**: 月末の「勤怠表提出」「Udemy受講レポート送信」「ABC目標進捗・エビデンス提出」など、社長が毎月手作業でメール作成・送信している定常業務摩擦（認知コスト）を根絶するため、ワンコマンドまたは自動バッチによる自動化パイプラインを構築する。

## ✅ DoD (完了条件)
- [ ] **Task 1: 月末定例メール（勤怠・Udemy）自動化**
  - 送信先・文面テンプレートの仕様整理
  - `core-service` 公式CLIによるメール下書き/送信機能の実装
- [ ] **Task 2: ABC目標サイクル自動化**
  - 目標設定・進捗トラッキング・月末エビデンス集計スクリプトの実装
- [ ] **Task 3: E2E結合テストと運用ドキュメント化**
  - 実際のテスト送信確認と運用手順の正本化
- [ ] PRマージによる知見アーカイブ ＆ ワークスペース更地化

## 🧭 Routing
- Working Memory (<=50 lines): [tasks/context.md](tasks/context.md)
- Task Checklist: [tasks/progress.md](tasks/progress.md)
- Lessons Learned: [tasks/lessons_learned.md](tasks/lessons_learned.md)
- 業務フロー設計: [docs/00_ABC_Integration_Workflow.md](docs/00_ABC_Integration_Workflow.md)
