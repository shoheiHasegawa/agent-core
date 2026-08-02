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
- `[/]` **2. Loop Orchestrator の設計・実装**
  - `[ ]` SDD/TDDステートマシンの設計（各フェーズのI/O、権限境界、差し戻し条件）
  - `[ ]` `tdd_controller.py`（またはオーケストレータースクリプト/スキル）の実装
  - `[ ]` 実行テストと統合検証

---

## 📌 Next Epic / Backlog (未解決の構造的課題)
今回のルール強化・SKILL解体によって「ワーカー」は整備されたが、完全な自律ループエンジニアリングを実現するためには以下の要素が不足している。
- `[ ]` **QA / CIパイプラインの整備**: TDD完了後のPR作成、Git側での自動CI/CD（Linter/Testの実行）、および `code-reviewer` ペルソナによるアーキテクチャの最終監査体制の確立。

## 📝 メモ・コンテキスト (Scratchpad)
- **【完了報告】2026-08-01 Session Handoff**:
  - Epic「ルールのFat化防止と、インクリメンタリズム・TDDパイプラインの再構築」を完遂。
  - ルール（立法）、Linter（司法）、SKILL（行政/ワーカー）の三権分立が確立された。
  - 複数Agentによるレビューを実施し、SKILLのGod Prompt違反の修正および、GEMINI.md内の `Timeless SSOT` を上位（第3条）へ昇格させるリファクタリングを完了。
  - **次回のセッション (Next Action)**: 
    1. 刷新された新ルールとドキュメントアーキテクチャ（`readme_template.md`, `spec_template.md` 等）に基づき、現在のリポジトリ内容（特に `core-service` の実装やドキュメント）が違反していないかをチェックし、負債を解消するところから再開すること。
    2. `agent-core` のPython実行環境（`python-dotenv`等の不足）を修復すること。
    3. 以下の5つの教訓を `agent-core/tools/register_zettelkasten_note.py` を用いてZettelkasten (Sense-Making) へ正式に登録すること。
       - **教訓1 (三権分立)**: LLMは長文ルールを守れないため、システムを「立法(Markdown)」「司法(Linter)」「行政(SKILL)」に物理分離すること。
       - **教訓2 (確証バイアスとSRP)**: TDDでは、テストを書くペルソナと実装するペルソナを完全に分割し、AIの確証バイアス（自己都合のテスト改ざん）を防ぐこと。
       - **教訓3 (Timeless SSOT)**: SSOTドキュメントからは「過去の過程」を一切排除し、「現在の真実」のみを冷徹に記述すること。LLMは過去のポエムを現在の文脈と誤認するため。
       - **教訓4 (Context Engineering)**: 機能ディレクトリの `README.md` に全レイヤーのテストや仕様へのポインタを集約し、AIが迷子にならないためのルーティングハブとすること。
       - **教訓5 (Goodhart's Lawと評価基準改ざん防止)**: AIに定量的指標を与えると評価基準（閾値設定）側を緩めて回避しようとするため、品質設定（Makefile等の閾値）の完全性を司法（Linter）で物理的にロックすること。
