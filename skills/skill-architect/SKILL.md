---
name: skill-architect
description: ユーザーの要求に基づいて新しいスキル（Agentの振る舞い）を設計・実装するメタスキル。
---

# Skill: Skill Architect

## 🎯 目的
Agentic OSのエージェントが使用する「Skill」を設計・生成する。システムプロンプトの記述からディレクトリ構成の作成までを一貫して行う。

## ⚠️ 絶対遵守ルール
スキルを設計・実装する前に、**必ず**以下のドキュメントを読み込み（`view_file`）、原則に違反していないかをチェックすること。
1. `agent-core/docs/skill_design_principles.md` （Skill Design Principles）
2. `agent-core/docs/architecture/document_architecture_principles.md` （Document Architecture Principles / 記憶の3層モデル）
1. **2-Tier Architectureと実行モデルの選択**:
   - 作成しようとしているスキルは「オーケストレーター（Tier 1）」か「ワーカー（Tier 2）」かを明確に定義すること。
   - オーケストレーターの場合、呼び出すワーカーの性質に応じて**「Role Switching（親エージェント自身の状態遷移による直接対話）」**か**「Subagent Delegation（サブエージェントへの委譲・バックグラウンド処理）」**のどちらが適切かを判断し、プロンプトに明記すること。
2. **SOLID (単一責任)**: ワーカーの場合、複数の作業（例：リサーチしてドキュメントを書く）を1つのプロンプトに混ぜ込まないこと。
3. **Zettelkastenの独立性**: スキル内に固有のドメイン知識をハードコードしないこと。
4. **立法と司法の分離 (Separation of Concerns)**: スキル内に特定のドメインルール（DDDの制約やハードコード禁止等）を直接記述してはいけない。ルールは `docs/rules/` 等のドキュメントに外部化（立法）し、スキルは「それを動的にロードして評価する」アルゴリズム（司法）のみを実装すること。
5. **グローバル・スキーマの適用 (CRITICAL)**: 作成するSKILLの「実行手順」は必ず以下の4項目の標準タグのみを用いたフォーマットに統一すること。
   - **入力 (Input)**: 前工程から受け取るもの
   - **アクション (Action)**: 行うべき具体的な処理
   - **制約事項 (Constraints)**: 絶対に守るべきルール
   - **出力 (Output)**: 次の工程へ渡すもの、または最終結果

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
