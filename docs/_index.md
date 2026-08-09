---
# ドキュメント・インデックス
title: "You_Inc Agentic OS: Document Architecture & Index"
description: "Agentと人間が参照すべきSSOT（Single Source of Truth）の3層構造とエントリーポイント"
---

# Agentic OS: Document Index

本リポジトリ（および関連リポジトリ）のドキュメントは、LLMのメタ認知を促進し、かつ認知負荷を下げるために以下の**3層アーキテクチャ**に分離して管理されています。
Agentはタスクの性質に応じて、適切な階層のドキュメントをJITロードしてください。

## 1. 憲法・思想 (Philosophy / Why)
システムの存在意義、最上位の制約、およびトレードオフの裁定原則。
*   [GEMINI.md](../../GEMINI.md): 全Agentと人間の共通認識。自己成長への寄与、フェイルファストとメタ認知のバランス原則。

## 2. ルール・踏み台 (Law & Heuristics / Must & What if)
Agentがタスク実行時に**JITロードする対象**。単なる手順（How）ではなく、最低限の「防護ネット」と、メタ認知を促す「問い」がセットになっています。

### Agentic OS 共通・メタスキル系 (`agent-core/docs/rules/`)
*   [dialog_heuristics.md](./rules/dialog_heuristics.md): 対話、ソクラテス的探求、優先度付けの踏み台。
*   [zettelkasten_heuristics.md](./rules/zettelkasten_heuristics.md): 第二の脳へのノート蒸留、抽象化の踏み台。
*   [sdd_tdd_heuristics.md](./rules/sdd_tdd_heuristics.md): 仕様定義、TDD（異常系網羅）、リファクタリングの踏み台。
*   [system_heuristics.md](./rules/system_heuristics.md): セッション管理、Zero-Queue状態管理、アーキテクチャ境界検知の踏み台。
*   [tool_design_principles.md](./rules/tool_design_principles.md): ツール実装時のJSON-Firstやエラーハンドリングの制約。
*   [orchestration.md](./rules/orchestration.md): Agent間通信とタスク委譲のプロトコル。
*   [skill_design_principles.md](./skill_design_principles.md): SKILL自体の設計に関するメタ・ルール。

### バックエンド機能実装系 (`core-service/docs/rules/`)
*   `ddd_guidelines.md`: DDDの実装制約とエンティティの純粋性。
*   `testing_strategy.md`: 自動テスト戦略とカバレッジ要件。
*   `dependency_injection.md`: DIコンテナの利用ルール。
*   `error_handling.md`: エラー分類とロギングの規則。
*   `context_engineering.md`: コンテキスト引き渡しの原則。

## 3. 構造・設計 (Architecture / What & How)
システム構成、データフロー、ディレクトリ構造など、静的な全体の「地図」。
*   [Architecture Index](./architecture/_index.md): `agent-core` の全体アーキテクチャ、データフロー、Optimization 2026の設計履歴など。
*   `core-service/docs/architecture.md`: バックエンドサービスのシステム構造。
