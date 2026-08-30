# Epic: Loop Engineering Refactoring

## 目的
You_Incにおける「ループエンジニアリング（自律的改善サイクル）」の再構築。
肥大化した独自SKILL群を断捨離し、Antigravityネイティブ機能（Slash Command等）を活用したリアーキテクチャを行うことで、Agentの作業品質（特に実装時のルール・ディレクトリ構造の遵守）を劇的に向上させる。

## 概要
- **As-Is**: プロンプトで複雑な進行管理（オーケストレーション）を行おうとしており、Agentのコンテキストが圧迫され、ルール遵守がおろそかになっている。
- **To-Be**: 人間がSDD・方針決定の壁打ちを行い、実装時のオーケストレーションはネイティブ機能（`/goal`等）に委譲。SKILLは「ルールの遵守」のみに純化させる。

## 関連資料
- [tasks/context.md](./tasks/context.md): プロジェクト開始時のコンテキスト
- [tasks/progress.md](./tasks/progress.md): タスクの進捗管理
- [docs/ADR/0001-shift-orchestration-to-native.md](./docs/ADR/0001-shift-orchestration-to-native.md): アーキテクチャ決定記録 (オーケストレーションの外部化)
- [docs/ADR/0002-agentic-os-design-principles.md](./docs/ADR/0002-agentic-os-design-principles.md): **[NEW]** 100点満点のAgentic OS設計図（ハーネス、状態管理、契約型、自己進化、フェイルセーフの決定事項）
