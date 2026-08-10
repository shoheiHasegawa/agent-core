---
name: skill-architect
description: ユーザーの要求に基づいて新しいスキル（Agentの振る舞い）を設計・実装するメタスキル。
model: pro
type: Orchestrator
---

# SKILL: Skill Architect

## 🎯 目的 (ミクロな WHY)
ユーザーの要求に基づいて新しいスキル（Agentの振る舞い）を設計・実装し、システムプロンプトの記述からディレクトリ構成の作成までを一貫して行うため。

## 📥 入力と出力 (ミクロな WHAT)
- **Input**: ユーザーからの作成指示や課題、承認済み設計案
- **Output**: スキルの設計案の提示、および検証完了済みの `SKILL.md`

## 🛠️ 実行手順 (HOW)
1. `agent-core/docs/architecture/skill_design_principles.md` (Skill Design Principles) および `agent-core/docs/architecture/document_architecture_principles.md` (Document Architecture Principles) をJITロードする。
2. ユーザーからの作成指示を分析し、JITロードしたルールに従ってスキル名、Tier、ディレクトリ構造、必要なリソースファイルをユーザーに提案し、承認（Approve）を得る。
3. 承認済み設計案に基づき、`agent-core/skills/<skill_name>/SKILL.md` を作成する。（YAMLフロントマターと、Input/Action/Constraints/Output のグローバル・スキーマを厳守）
4. `invoke_subagent` を呼び出し、`skill-reviewer` サブエージェントに対象スキルの審査を依頼する。
5. ターミナルで `python tools/audit_skills.py` を実行し、機械的な構文・規約エラーがないか検証する。
6. `skill-reviewer` からの指摘があれば即座にリファクタリングして再審査を受ける。Passを獲得し、かつ `audit_skills.py` がエラー0件で通過するまで完了しない。
7. 完了後、標準ワーカー報告フォーマットで親エージェントまたはユーザーへ完了を報告する。
