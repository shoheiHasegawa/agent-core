# Epic Workspace Progress (SSOT)

**【メタデータ】**
- Epic: `corporate_goal_integration`
- 目的: 会社のABC目標とYou_Incの10_Areas（成長）を統合し、タスクの進捗管理とエビデンス作成を自動化する。
- 完了条件: 目標設定スキル（`abc-goal-planner`）が完成し、Task Registryへの一括登録、および月末エビデンスの自動出力がバッチ化されていること。

---

## 📋 タスクリスト (Task Breakdown)
Epicの完了条件を満たすためのタスク分解。
進捗更新のタイミング: タスクの区切り（完了時）ごとに都度更新すること。

- `[ ]` **Phase 1: 仕様定義とフロー設計 (SDD)** 👈 Current
  - `[x]` ABC目標設定・運用に関する業務フロー図（Mermaid等）の作成とドキュメント化
  - `[ ]` 目標設定用テンプレート（`2026_H2_ABC_Goals.md` 等）のフォーマット定義
  - `[ ]` 提出用エビデンスフォーマット（`Evidence_Template.md`）の仕様定義
- `[ ]` **Phase 2: PLANフェーズの実装 (目標設定スキル)**
  - `[ ]` `abc-goal-planner` SKILLのプロンプト・要件定義と実装
  - `[ ]` 今期のABC目標の壁打ちとSSOTへの出力
- `[ ]` **Phase 3: DOフェーズの実装 (実行進捗管理の自動化)**
  - `[ ]` SSOTから Task Registry (SQLite) へ目標を Epic/Tasks として一括登録する仕組みの実装
- `[ ]` **Phase 4: CHECKフェーズの実装 (エビデンス生成の自動化)**
  - `[ ]` `generate_abc_evidence.py` の仕様定義および実装
  - `[ ]` DB（worklogs）からの実績抽出とレポート出力テスト

---

## 📝 メモ・コンテキスト (Scratchpad)
作業中の気付き、ハマったポイント、次回への備忘録など。
