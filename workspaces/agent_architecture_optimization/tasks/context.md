# 📍 Current Context (Working Memory)

> **⚠️ Agentへの絶対ルール**
> - このファイルは**最大50行以内**に保つこと。
> - ユーザーに返答する前に、必ず自律的にこのファイルを最新の文脈に上書き（Update）すること。

---

## 🎯 現在の焦点 (Current Focus)
- **PR 1, PR 2, PR 3**: 完了・テスト/クリーンネス/孤立監査全通過・コミット完了。
- **PR 4: 全18スキルのリファクタリング (高付加価値化 & ルール純度向上)** に着手。

## 📌 次の実行内容 (PR 4)
- `docs/04_Skill_Refactoring_Matrix_and_High_Value_Specs.md` の仕様に従い、4つのカテゴリ別にスキルを順次リファクタリング:
  1. **Category A (対話7スキル)**: `night-routine`, `inbox-triage`, `journaling-counselor`, `priority-planner`, `johari-profiler`, `socratic-interviewer`, `sdd-spec-writer`
  2. **Category B (重ワーカー4スキル)**: `tdd-green-refactorer`, `tool-architect`, `skill-architect`, `skill-reviewer`
  3. **Category C (軽ワーカー4スキル)**: `tdd-red-coder`, `compliance-reviewer`, `zk-formatter-qa`, `workspace-architect`
  4. **Category D (オーケストレーター3スキル)**: `session-manager`, `sdd-loop-orchestrator`, `zk-distillation-orchestrator`
- 各カテゴリごとに `audit_skills.py` および `./tools/pre_handoff_verify.sh` で検証。

## ❓ なぜ今ここにいるのか (Why we are here)
- ハーネス（PR 2）と契約テンプレート（PR 3）が完成したため、全スキルのプロンプト純度向上と知能注入（Few-Shot / ヒューリスティクス）を安全に実行できる状態になった。
