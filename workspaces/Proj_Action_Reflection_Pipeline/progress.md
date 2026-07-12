# Proj_Action_Reflection_Pipeline Progress Tracker

## 📌 プロジェクト概要
CEO（社長）が管理のプレッシャーから解放され、高いパフォーマンスと精神的なウェルビーイングを両立するための「秘書モデル（Secretary Paradigm）」に基づくスケジューリングのコアエンジンと対話インターフェースを構築する。

## ✅ 完了したEpic
- `[x]` **Epic 01: 構想とアーキテクチャ定義**
  - 秘書モデル、M/S/W分類、リカバリーファースト等のパラダイムを定義済。
- `[x]` **Epic 02: 詳細仕様策定**
  - iOSショートカット連携、カレンダー同期ロジックなどのドキュメント作成。
- `[x]` **Epic 03: core-service (計算エンジン) の実装**
  - 9つのスケジューリング制約を実装し、テスト戦略の改修と専門家レビューを完了。
- `[x]` **Epic 04: 朝夜のジャーナリング/ブリーフィング SKILL の実装**
  - カレンダー同期を「朝の1回」にロックする堅牢なドメインモデルを確立。
  - `night-routine` (Orchestrator), `journaling-counselor` (Worker), `priority-planner` (Worker) の2-Tier SKILL群を実装。
  - プロンプトへのハードコード（立法）を排除し、Orchestratorから引数としてパスやルールを注入（DI）する「JIT Context Loading」を実装。
  - UXを崩壊させる「サブエージェントの伝言ゲーム」を防ぐため、親Agentが自身にルールを読み込ませる「Role Switching (自己状態遷移)」のアーキテクチャモデルを考案し、メタスキル（`skill-architect`, `skill-reviewer`）の原則としてシステムレベルに昇華させた。
  - JSON直接更新の脆弱性を防ぐ `validate_task_registry.py` と、osascript のシェルインジェクションを修正した安全な `daily_scheduler_batch.py` を実装完了。

- `[x]` **Epic 04-B: システムガバナンスと安全装置の実装**
  - セッション終了時に未検証コードを残さないため、`agent-core/scripts/pre_handoff_verify.sh` によるオーケストレーションを実装。
  - `AGENT.md` と `session-manager/SKILL.md` に Commit & Push 義務を明記。
  - `core-service` に `make check-all` を強制する Pre-commit フックを導入。

## 🚀 次のアクション (Current Status)
- `[ ]` **Epic 05: 実運用テスト (Dashboard開発はスコープ外のため除外)**
  - 実際に `night-routine` を稼働させてフィードバックループを回す。
