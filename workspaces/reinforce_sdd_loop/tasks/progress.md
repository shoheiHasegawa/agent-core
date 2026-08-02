# Epic Workspace Progress (SSOT)

**【メタデータ】**
- Epic: `reinforce_sdd_loop`
- 目的: SDD/TDDプロセスにおけるSpecと実装の乖離を防ぎ、ループエンジニアリングを強固にする仕組みを構築する。
- 完了条件: 新規specフォーマットの策定、QAプロンプトの強化、ハードゲート化の設計。

---

## 📋 タスクリスト (Task Breakdown)

### 準備・設計フェーズ
- `[x]` ユーザーとの壁打ち（現状の優先課題の特定とアプローチの決定）
- `[x]` You_Inc全体の網羅的分析（サブエージェントによる並列リサーチ）
- `[x]` 課題と原因の洗い出し完了（`01_problem_analysis.md`）
- `[x]` 解決策と設計方針の策定（`02_architecture_design.md`）

### 実装フェーズ（レイヤー別にインクリメンタルに進める）
- `[x]` **Layer 0 (Constitution)**: `GEMINI.md` に Timeless SSOT と インクリメンタリズム（WIP制限）の大原則を追記する
- `[x]` **Layer 1 (Domain Router)**: `AGENT.md` にTDD等を行う際のハードゲートへのルーティングを明記する
- `[x]` **Layer 2 (Meta-Rules & Harness)**: `document_architecture_principles.md` の策定と、ルールの静的解析（`validate_sdd.py`）への移譲・軽量化
- `[x]` **Layer 3 (Meta-Skills)**: `skill-architect` と `skill-reviewer` がSKILLのファット化を防げるように審査基準を強化する
- `[x]` **Layer 4 (Execution Skills)**: ファット化した `core-service-engineer` 等のSKILLの解体と階層化（SRP適用）
- `[x]` **Layer 5 (Templates)**: 型定義とインラインRationaleを持つ、自己完結型の `spec_template.md` を作成する
- `[x]` **Layer 6 (Knowledge Distillation)**: 5つの普遍的教訓をZettelkasten（`20_Sense_Making`）へ正式登録完了

---

## 📋 現在の作業チェックリスト (Current Sprint)
- `[x]` **1. 品質ゲート改ざん防止機能の実装 (`validate_sdd.py`)**
  - `[x]` `Makefile` の `--cov-fail-under` が 90% 以上か検証する関数の作成
  - `[x]` `Makefile` の `check-all` ターゲットに `test`, `lint`, `validate` が全て含まれるか検証する関数の作成
  - `[x]` `pyproject.toml` 等で不正な除外設定がないか検証する関数の作成
  - `[x]` 故意に閾値を下げた場合に正しく FAIL するかテスト検証
- `[x]` **2. Tool API化とSession Insights自動ストック・提案の仕組み構築**
  - `[x]` `agent-core/docs/rules/tool_design_principles.md` の作成（正本仕様）
  - `[x]` `agent-core/AGENT.md` へのポインタ追加
  - `[x]` `agent-core/tools/register_zettelkasten_note.py` のJSON API化（全ノート種別・バッチ対応）
  - `[x]` `register_zettelkasten_note.py` のテスト・検証（単一/複数/全種別）
  - `[x]` `agent-core/templates/Workspace_Progress_Template.md` に `## 💡 Session Insights` 追加
  - `[x]` `agent-core/skills/session-manager/SKILL.md` に Handoff時の知見提案フローを組み込み
- `[x]` **3. Loop Orchestrator の設計・実装 & ダブルループTDD公式標準化**
  - `[x]` ダブルループTDD（Outer Red -> Inner TDD -> Quality Gate）の標準フロー明文化（`testing_strategy.md`）
  - `[x]` 各ワーカーSKILL（`tdd-red-coder`, `tdd-green-refactorer`）のダブルループ対応更新
  - `[x]` ゲート判定CLIツール（`agent-core/tools/verify_loop_state.py`）の実装
  - `[x]` オーケストレータースキル（`agent-core/skills/sdd-loop-orchestrator/SKILL.md`）の実装
  - `[x]` 物理検証とカタログ登録
- `[x]` **4. 独立品質監査と120点へのシステム堅牢化（Harden Gates）**
  - `[x]` 独立シニアレビュアーによる多角的品質監査の実施
  - `[x]` Outer Red時のImportErrorデッドロック解消（`sdd-spec-writer`での空スタブ生成＆`verify_outer_red`のNotImplementedError許容）
  - `[x]` `validate_sdd.py` の `ast.AsyncFunctionDef` AST走査漏れ対応
  - `[x]` 単体テスト（Unit Test）における要求ID強制の緩和（結合テストへの集中）
  - `[x]` Proof of Red（状態遷移の永続証跡メタデータ）の出力と記録
  - `[x]` The "God Prompt" 予防（リトライ時のプロンプト・サニタイズ規定）
- `[x]` **5. ナレッジの蒸留（Zettelkasten登録）**
  - `[x]` 普遍的教訓5件の Sense-Making 登録完了
  - `[x]` 「自律ループエンジニアリングにおける監視ポイントと4大アンチパターン」の Sense-Making 登録完了
- `[ ]` **6. 既存実装・ドキュメントの新標準への適合（Migration & Test Audit）**
  - `[x]` **Step 1: `mobile_vault` パッケージの標準化＆テスト漏れ監査**
    - `[x]` 現状の仕様・テストの棚卸しと未決事項・設計判断の洗い出し（ユーザー壁打ち）
    - `[x]` `spec.md` の新標準化（Rationale, Contract, 要求ID体系）
    - `[x]` テスト漏れ（未検証シナリオ・エッジケース・Mock排除）の補強
    - `[x]` `README.md` のルーティングポータル化
    - `[x]` `make check-all` 検証とアトミックコミット
  - `[x]` **Step 2: `second_brain` パッケージの標準化＆テスト漏れ監査**
    - `[x]` 現状の仕様・テストの棚卸しと未決事項・設計判断の洗い出し（ユーザー壁打ち）
    - `[x]` `spec.md` の新標準化（Rationale, Contract, 要求ID体系）
    - `[x]` テスト漏れ（未検証シナリオ・エッジケース・Mock排除）の補強
    - `[x]` `README.md` のルーティングポータル化
    - `[x]` `make check-all` 検証とアトミックコミット
  - `[x]` **Step 3: `task_operations` パッケージの標準化＆テスト漏れ監査**
    - `[x]` 現状の仕様・テストの棚卸しと未決事項・設計判断の洗い出し（ユーザー壁打ち）
    - `[x]` `spec.md` の新標準化（Rationale, Contract, 要求ID体系）
    - `[x]` テスト漏れ（未検証シナリオ・エッジケース・Mock排除）の補強
    - `[x]` `README.md` のルーティングポータル化
    - `[x]` `make check-all` 検証とアトミックコミット
  - `[x]` **Step 4: 全体結合・フルカバレッジ総合監査 (`make check-all`)**
    - `[x]` カバレッジ >= 90%（現在 92.63%）
    - `[x]` SDD 仕様トレーサビリティの完全一致
    - `[x]` Linter / 静的解析の完全パス
    - `[x]` 孤立スクリプト監査（`audit_orphan_scripts.py`）
    - `[x]` 最終コミット

---

## 📌 Next Epic / Backlog (今後の発展ロードマップ)
今回のEpic（`reinforce_sdd_loop`）完了後、次の段階として検討可能なEpic：
- `[ ]` **Epic: CI/CDパイプラインとリモート自動化の確立**: 
  - TDD完了後の自動PR作成
  - GitHub Actions 等でのリモート自動CI/CD（Linter / Test / SDD検証）
  - リモート環境での自動マージゲート構築

---

## 📝 メモ・コンテキスト (Scratchpad)
- **【方針】既存資産マイグレーションの進め方**:
  - 各ステップごとに「仕様棚卸し → ユーザーとの壁打ち（設計判断） → spec.md/テスト補強 → README作成 → make check-all → コミット」のサイクルを厳守する。
  - AIが自己判断で勝手に仕様を決めつけず、未決事項や設計の迷いが生じた場合は必ずユーザーに設計判断を仰ぐ。
