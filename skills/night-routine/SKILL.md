---
name: night-routine
description: 1日の終わりに行う内省と明日への準備を統括するOrchestrator（Tier 1）スキル。各フェーズのスキルを順次読み込み、Role Switchingによって対話を進行する。
---

# Skill: Night Routine (Orchestrator)

## 🎯 目的
1日の終わりのルーティンを統括する。ユーザーの内省（ジャーナリング）を支援し、その後タスクの優先順位を整理するプロセスを、各フェーズの専門ロール（Role Switching）に切り替えながら完遂させる。

## ⚠️ 実行ルール (Tier 1 制約)
*   **自身で作業しない**: このスキル自身はカウンセリングやタスクデータの書き換えを行わない。
*   **順次呼び出し**: 以下に定義されたPhase 1 -> Phase 2 -> Phase 3 の順序で、各スキルの専門家に「Role Switching」を行いながら処理を進行させる。
*   **カレンダー同期の再キック**: 必要に応じて、フェーズの中でスケジュール同期のジョブネットがキックされることを許容する。

---

## 1. ワークログの回収と対話開始 (Phase 1)
必ず最初に行うこととして、ユーザーが日中に入力した `Briefing.md` の実績を回収します。
```bash
uv run python3 agent-core/tools/sync_worklogs.py "agent-core/Briefing_YYYY-MM-DD.md"
```
（※YYYY-MM-DDは本日の日付に置き換えてください。親ディレクトリにある場合もあります。もしエラーが出た場合はユーザーに報告してください）

回収が完了したら、ユーザーに「1日お疲れ様でした。」と挨拶し、本日の進捗を共有します。
ここでは深いヒアリングは行わず、回収した実績データ（特に未完了タスクの情報）のコンテキストを保持したまま、Phase 2（`journaling-counselor`）へ引き継ぎます。

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
