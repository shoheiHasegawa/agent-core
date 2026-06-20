# Harvest Report: Agent Harness Engineering & Operational Flows

**Date**: 2026-06-14
**Context**: `Proj_Playground_Reconstruction` における、You, Inc. アーキテクチャの運用ガバナンス、安全網（ハーネス）、およびDDD/SDD設計の壁打ちセッション。

## 💡 教訓 (Wisdom & Insights)

1. **自己記述型（Self-Describing）リポジトリの極致**
   - 中央集権（agent-core）にすべてを書くのではなく、各リポジトリの直下に `INDEX.md` と `RULES.md` を置き、Agentに入室時にローカルルールを読み込ませるアプローチ。これはマルチエージェントシステムの自律性と拡張性を最大化する最高峰のコンテキスト・エンジニアリングである。

2. **適応型PRガバナンスと隔離環境（ハーネス）**
   - 変更の「破壊的リスク」に応じてPR必須度を変える。
   - `core-service`（ロジック）と `agent-core`（ルール）はPR必須。`second-brain`（データ）はAgentのDirect Pushを許可しCIのLintで守る。
   - 実行環境は `workspaces/` に `git worktree` で展開し、さらに「Dockerコンテナ内で実行」させることで、ホスト環境を物理的に保護する。

3. **Functional Core, Imperative Shell（I/Oと品質の安定化）**
   - Agentに都度API通信のスクリプトを書かせると品質がばらつく。そのため、クリティカルな処理は `core-service` 内に **「副作用をカプセル化したステートレスなService」** として固定化（実装）し、Agentはそれを呼び出すだけにする。これが品質担保の最大のハーネスとなる。

4. **仕様とテストのトレーサビリティ（SDD + TDD）**
   - Application層にのみ `spec.md` を置き、シナリオID（例: `[SCENARIO-01]`）をテストコードに直接マッピングすることで、仕様とテストの乖離を防ぐ。

## ⚠️ 技術的負債と課題 (Tech Debt & Challenges)

- **動的な運用フロー（Feedback Loop）の未定義**
   - PRがCIで落ちた時や、社長から「Change Requested」を出された際、Agentがそれを検知して再作業ループ（エンキュー）に入る仕組み（WebhookやPolling）がまだ設計されていない。
   - 複数のEpicが並行した際のマージコンフリクトの自律的な解消（`rebase`）フローが未定。
   - 社長に承認を求める「Human-in-the-loop」のUI/UX（ダッシュボード通知なのか、CLIプロンプトなのか）が未定義。

## 🚀 システム改善案 (Next Actions)

- `agent-core` の隔離開発環境として、使い捨ての Docker コンテナ環境を構築する。
- 抽出された運用上の課題（`open-item.md` の課題O〜R）を解決するため、次セッション以降で「Agent間の通信・再実行のシーケンス図レベルの設計」に着手する。
- 各リポジトリの顔となるペルソナ別ドキュメント（`docs/architecture.md`, `docs/implementation.md`, `docs/review.md`）のひな形を作成する。
