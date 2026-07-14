---
name: night-routine
description: 1日の終わりに行う内省と明日への準備を統括するOrchestrator（Tier 1）スキル。各フェーズのスキルを順次読み込み、Role Switchingによって対話を進行する。
---

# Skill: Night Routine (Orchestrator)

## 🎯 目的
1日の終わりのルーティンを統括する。ユーザーの内省（ジャーナリング）を支援し、その後タスクの優先順位を整理するプロセスを、専門のサブエージェント（Worker）に委譲して完遂させる。

## ⚠️ 実行ルール (Tier 1 制約)
*   **自身で作業しない**: このスキル自身はカウンセリングやタスクデータの書き換えを行わない。
*   **カレンダー同期の禁止**: スケジュール同期バッチ（`daily_scheduler_batch.py`）を起動してはならない（同期は朝の自動バッチにロックされているため）。

## 🛠️ 実行手順 (Role Switching)

このスキルはユーザーとの壁打ちを伴うため、サブエージェントを起動してはならない。**親エージェント自身**が状態（Role）を切り替えながら進行すること。

### 1. Inbox Triage Mode (`inbox-triage`)
*   **アクション (Action)**: `agent-core/skills/inbox-triage/SKILL.md` を読み込み、そのルールを自身に適用してInboxの仕分け業務を完遂する。
*   **出力 (Output)**: 仕分け完了後、フェーズ2へ移行する。

### 2. Counselor Mode (`journaling-counselor`)
*   **入力 (Input)**: フェーズ1の完了
*   **アクション (Action)**: `agent-core/skills/journaling-counselor/SKILL.md` を読み込み、そのルールに従いカウンセリング業務を完遂する。
*   **出力 (Output)**: カウンセリング完了後、フェーズ3へ移行する。

### 3. Planner Mode (`priority-planner`)
*   **入力 (Input)**: フェーズ2の完了
*   **アクション (Action)**: `agent-core/skills/priority-planner/SKILL.md` を読み込み、そのルールに従い明日へのタスク計画と更新を完遂する。
*   **出力 (Output)**: 計画完了後、フェーズ4へ移行する。

### 4. クロージング
*   **アクション (Action)**: 全ての作業が完了したら、ユーザーにセッションの終了を伝える。
*   **制約事項 (Constraints)**: 以下の旨を必ず伝えること。
    *   「お疲れ様でした。明日の準備は完璧に整いました。」
    *   「明日の朝、あなたが起きる前に私が自動でカレンダーを最新化しておきます。安心してゆっくり休んでください。」
*   **出力 (Output)**: OSセッションの終了
