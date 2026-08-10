---
name: skill-reviewer
description: 既存または新規作成されたスキルの品質を、SOLID原則とAgentic OSアーキテクチャに基づいてレビューするメタスキル。
model: pro
type: Worker
---

# SKILL: Skill Reviewer

## 🎯 目的 (ミクロな WHY)
実装されたスキルのコード（`SKILL.md` や関連スクリプト）を静的解析・論理レビューし、アンチパターン（責務過多、ハードコード、状態の持ち込み等）を検出してリファクタリングを促すため。

## 📥 入力と出力 (ミクロな WHAT)
- **Input**: レビュー対象のスキル名またはフォルダパス
- **Output**: スキルの合否判定（Pass/Fail）および修正案のレポート

## 🛠️ 実行手順 (HOW)
1. 対象のスキルフォルダ（`agent-core/skills/<skill_name>/`）内の全ファイルを読み込む。
2. `/Users/shoheihasegawa/you_inc/GEMINI.md` (合憲性チェック) および `agent-core/docs/architecture/document_architecture_principles.md` などをJITロードし、審査基準となるルールを抽出する。
3. JITロードしたルールの観点（プロンプト純度、メタ認知の注入、職務分離、Few-Shotの具体性、契約遵守など）に基づいて対象スキルを独立して評価する。
4. 評価をまとめ、片方でも違反がある場合は総合評価を【Fail（差し戻し）】とし、具体的な修正案を提示するレポートを作成する。
5. レポートをユーザーに提示し、修正を実行するかどうかを確認する。
6. 完了後、標準ワーカー報告フォーマットで親エージェントに結果を報告する。
