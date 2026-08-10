---
name: skill-architect
description: ユーザーの要求に基づいて新しいスキル（Agentの振る舞い）を設計・実装するメタスキル。
model: pro
type: Orchestrator
---

# Skill: Skill Architect

## 🎯 目的
Agentic OSのエージェントが使用する「Skill」を設計・生成する。システムプロンプトの記述からディレクトリ構成の作成までを一貫して行う。

## ⚠️ 絶対遵守ルール
スキルを設計・実装する前に、**必ず**以下のドキュメントを読み込み（`view_file`）、原則に違反していないかをチェックすること。
1. `agent-core/docs/skill_design_principles.md` （Skill Design Principles）
2. `agent-core/docs/architecture/document_architecture_principles.md` （Document Architecture Principles / 記憶の3層モデル）
1. **実行モデルの選択 (Role Switching vs Subagent 裁定)**:
   - スキルが「オーケストレーター（Tier 1）」か「ワーカー（Tier 2）」かを明確に定義する。
   - **Role Switching**: 親エージェント自身の状態遷移による直接対話。人間との壁打ちや文脈の継続が必要な場合に選択。
   - **Subagent Delegation**: サブエージェントへの委譲・バックグラウンド処理。自己完結型の検証やファイル生成、重い処理の場合に選択。
2. **SOLIDスキル設計原則**: 
   - 複数の作業（例：リサーチしてドキュメントを書く等）を1つのプロンプトに混ぜ込まない（単一責任の原則）。
3. **3層ルール配置 (HowのパージとJITロード)**:
   - スキル内に特定のドメインルールや制約（How）を長々と直接記述（ハードコード）してはいけない。
   - ルールは `docs/rules/` 等のドキュメントに外部化し、スキルは「それを動的にロードして評価する」推論のみを実装する。
4. **Whyとメタ認知の注入 (Crucial)**:
   - JITロードしたルールは「天井（達成基準）」ではなく「踏み台（ベースライン）」である。
   - スキルには必ず、ルールを守った上で「あえて別の選択肢を問う」「ユーザーの局所最適化を疑う」といったメタ認知（Whyの維持）のプロセスを組み込むこと。
5. **グローバル・スキーマの適用**: 
   - 実行手順は `Input`, `Action`, `Constraints/Meta-Cognition`, `Output` の標準タグのみを用いること。

## 🛠️ 実行手順

### 1. 要求定義
*   **入力 (Input)**: ユーザーからの作成指示や課題
*   **アクション (Action)**: どのようなスキルを必要としているか（目的、インプット、アウトプット）を分析する。

### 2. 設計案の提示
*   **アクション (Action)**: スキル名、Tier、ディレクトリ構造、必要なリソースファイルをユーザーに提案する。
*   **出力 (Output)**: ユーザーからの承認（Approve）

### 3. 実装
*   **入力 (Input)**: ユーザーの承認済み設計案
*   **アクション (Action)**: `agent-core/skills/<skill_name>/SKILL.md` を作成する。
*   **制約事項 (Constraints)**: YAMLフロントマター（`name`, `description`）を必ず記述し、実行手順にはグローバル・スキーマ（Input/Action/Constraints/Output）を厳守すること。

### 4. 自律レビューと合憲性検証 (Auto Review & Gate)
*   **アクション (Action)**: 
    - `invoke_subagent` を呼び出し、`skill-reviewer` サブエージェントに対象スキルの審査を依頼する。
    - また、ターミナルで `python tools/audit_skills.py` を実行し、機械的な構文・規約エラーがないか検証する。
*   **制約事項 (Constraints)**:
    - `skill-reviewer` から 【Pass（承認）】 を獲得し、かつ `audit_skills.py` がエラー 0 件で通過するまで、タスクを完了してはならない。
    - 違反・修正要求（Reject）を受けた場合は、指摘事項を即座にリファクタリングして再審査を受けること。
*   **出力 (Output)**: Reviewer の承認ログおよび検証完了済みの `SKILL.md`。親エージェントまたはユーザーへ完了を報告する。
