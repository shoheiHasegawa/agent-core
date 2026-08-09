---
name: session-manager
description: Agentic OSのセッション開始時（起動シーケンス）および終了時（ハンドオフ）の進捗管理とルーティングを行うスキル。
---

# Skill: Session Manager (Model: 親 Orchestrator / Pro)

## 🎯 目的
Agentic OSにおいて、エージェントがセッションを開始（起動）した際の初期行動と、セッションを終了（ハンドオフ）する際の申し送り手順を標準化し、正本（SSOT）の原則に基づく強固な進捗管理とルーティングを提供する。

## ⚠️ ルールのJITロードと自律更新 (SSOT & Zero-Prompt Update)
1. **ルールのJITロード**: `agent-core/docs/rules/system_heuristics.md` （状態管理とZero-Queueの原則）をJITロードし、それに従って起動・ハンドオフシーケンスを実行せよ。
2. **【メタ認知と自律更新の強制】**: 
   - エージェントは、ユーザーから「進捗を更新して」と指示されるのを待ってはならない。JITロードしたプロトコルを踏み台にし、ユーザーに返答する前に**自律的にツールを呼び出して状態を更新すること**。
   - 単なる進捗の記録ではなく、「今回の議論から、将来の意思決定に活かせる教訓やメタ知識（Why）は得られなかったか？」を常に自問し、それをコンテキストに反映させること。

## 🛠️ 実行手順

本スキルは状態（State）やライフサイクルイベントに応じた振る舞いを行う。

### 1. 起動シーケンス (3-Step Lazy Bootstrapping)
*   **入力 (Input)**: 対象ワークスペースの `tasks/context.md` と `tasks/progress.md`
*   **アクション (Action)**: 以下の3ステップによる最速起動（Zero-Queue）を行う。
    1. **Context Load**: `tasks/context.md` (≤50行) を読み込み、前回の文脈と直近のFocusを把握する。
    2. **Progress Check**: `tasks/progress.md` を読み込み、現在のEpicにおける進捗（Loop状態）を確認する。
    3. **Routing**: 状態に応じた適切なスキルの起動、またはユーザーへの提案を行う。
       - `progress.md` の現在地が「Loop 1: 仕様策定中」の場合 ➔ `sdd-spec-writer` 等による再開。
       - `progress.md` の現在地が「Loop 2: 自律TDD実装中」の場合 ➔ `sdd-loop-orchestrator` による再開。
*   **出力 (Output)**: ユーザーへの着手提案、または自律的なスキルチェーンの再開。

### 2. セッション中の自律更新
*   **入力 (Input)**: セッション中の対話や議論の結論
*   **アクション (Action)**: セッション中は Agent自身が `progress.md` と `context.md` を自律的に維持管理・バックグラウンド更新し続ける。

### 3. セッション終了・申し送り (Handoff)
*   **入力 (Input)**: セッション終了・中断の指示
*   **アクション (Action)**: セッション終了の準備として、知見の蒸留（Session Insights）、事前検証、コミット、およびEnqueue（申し送りパケット生成）を実行する。
*   **制約事項 (Constraints)**: 以下の手順を必ず厳守すること。
    1. **【Wisdom Extraction (知見の蒸留提案)】**:
       - `progress.md` の `## 💡 Session Insights` に未登録（`[ ]`）の教訓・知見があるかスキャンする。
       - 存在する場合、ユーザーに「本セッションで以下の知見がストックされています。Zettelkasten（`second-brain`）へ登録しますか？」と提示する。
       - ユーザーの承認が得られたら、`register_zettelkasten_note.py`（JSON API）を実行して登録し、`progress.md` 側を `[x]` に更新する。
    2. `context.md` に次回の論点（Current Focus）が書き残されているか確認。
    3. **【Handoffクリーンネスの物理保証】**: `bash tools/pre_handoff_verify.sh` を実行し、検証に合格することを確認する。
    4. パスしたら、作業したリポジトリで `git add . && git commit -m "chore: Handoff - [作業のサマリ]" && git push` を実行。
*   **出力 (Output)**: 知見のZettelkasten登録、およびGit同期完了

