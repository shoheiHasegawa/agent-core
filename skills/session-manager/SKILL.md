---
name: session-manager
description: Agentic OSのセッション開始時（起動シーケンス）および終了時（ハンドオフ）のキュー・進捗管理とルーティングを行うスキル。
---

# Skill: Session Manager

## 🎯 目的
Agentic OSにおいて、エージェントがセッションを開始（起動）した際の初期行動と、セッションを終了（ハンドオフ）する際の申し送り手順を標準化し、正本（SSOT）の原則に基づく強固な進捗管理とルーティングを提供する。

## ⚠️ 絶対遵守ルール（SSOTの原則）
1. **正本（状態の真実）**: `workspaces/<epic_name>/progress.md` のみが進捗の正本である。
2. **Queue（ルーティング）**: `agent-core/queue/handoff_*.md` は進捗状態を一切持たず、「次にどのWorkspaceを見るべきか」という**軽量なルーティング情報（チケット）**のみを保持する。
3. **分離の原則**: セッションマネージャー自身は個別のタスク（コーディングやリサーチ等）を実行しない。ルーティングと状態管理に専念する（Tier 1 Orchestratorとしての振る舞い）。

## 🔄 起動シーケンス (Boot Sequence)
Agentはセッション開始時（またはタスク再開時）に、現在の状態に応じたルーティング（状態遷移）を行う。手続き的な処理（AをしてBをする）ではなく、以下のStateに基づいて振る舞うこと。

- **State A: キューにHandoffパケットが存在する場合 (Resume)**
  - **条件**: `agent-core/queue/` に `handoff_*.md` が存在する（最優先）。
  - **行動**: パケットが示すポインタ先の `progress.md` を読み込み進捗を把握した上で、元のHandoffパケットを破棄（Dequeue）する。その後、ユーザーにタスク再開を提案する。

- **State B: キューが空の場合 (New Task)**
  - **条件**: `agent-core/queue/` が完全に空である。
  - **行動**: `agent-core/epics/` のバックログをスキャンし、次に着手すべきEpic候補を見つけ出してユーザーに提案する。

## 📦 キュー処理と進捗管理のライフサイクル
各ライフサイクルイベントにおける状態の遷移ルール（責務）は以下の通り。

- **進捗の更新 (Progress Update)**: `workspaces/<workspace_dir_name>/progress.md` はタスクの区切りごとに都度更新されなければならない。終了時まで後回しにすることは禁止する。
- **Workspace展開 (Epic to Workspace)**: 新規Epicの着手時、`agent-core/epics/` の定義をもとに `workspaces/<workspace_dir_name>/` ディレクトリと `agent-core/templates/Workspace_Progress_Template.md` に基づく `progress.md` が作成されなければならない。
- **Pre-Handoff Verification (事前検証とコミット)**: セッション終了の準備として、Agentは以下の手順を必ず実行しなければならない。
  1. `agent-core/` ディレクトリに移動し、`bash scripts/pre_handoff_verify.sh` を実行する。
  2. エラーが出た場合はエラー内容を修正し、成功するまで繰り返す。
  3. 検証にパスしたら、作業したリポジトリで `git add . && git commit -m "chore: Handoff - [作業のサマリ]" && git push` を実行する。
- **Enqueue（申し送り）**: 上記の検証とコミットが完了した後、`agent-core/templates/Handoff_Packet_Template.md` に基づくパケットを `agent-core/queue/handoff_<workspace_dir_name>.md` として生成（上書き）しなければならない。**【重要】パケットの宛先やファイル名には「Epic 04」のような抽象的な名称や番号を絶対に使わず、必ず物理的に一意なワークスペースのディレクトリ名を使用すること。**

## 🛠️ トリガー
*   セッションが開始され、「次に何をすべきか」を尋ねられた時
*   セッションを終了、あるいは中断し、状態を保存・申し送りするよう指示された時
