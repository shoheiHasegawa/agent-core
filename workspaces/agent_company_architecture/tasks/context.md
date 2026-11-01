# 📍 Current Context (Working Memory)

> **⚠️ Agentへの絶対ルール**
> - このファイルは**最大50行以内**に保つこと。これを超える場合は古い情報を要約圧縮、または削除すること。
> - 対話ログのコピペは禁止。Agent自身の言葉で抽象化・要約したメタ認知情報のみを記載すること。
> - ユーザーに返答する前に、必ず自律的にこのファイルを最新の文脈に上書き（Update）すること。

---

## 🎯 現在の焦点 (Current Focus / Handoff Point)
- **Epic `agent_company_architecture` の全実装・実サブエージェント試運転・`main` マージ・Worktree回収（`make ws-harvest`）が完了**。
- 社長へクローズ時の **「3点内省ブリーフィング（Executive Digest）」** を提示し、今回の気づき（ルートB）を `second-brain` へ蒸留するか、または Step 4（第1回作戦会議）へ進むかを確認する。

## 📌 完了サマリー (Final Verification Digest)
1. **ドキュメント統廃合とSSOT昇格（引き算の達成）**:
   - `agent-core/docs/` の旧 `system/`・`agent_rules/`・旧テンプレート（計22ファイル）を削除し、正本 [`docs/architecture.md`](../../../docs/architecture.md)、思考原則 [`docs/rules/`](../../../docs/rules/thinking_os_and_loop_principles.md)（2ファイル）、経験ストック [`docs/experiences/`](../../../docs/experiences/README.md)（2ファイル）へ完全統合。
   - `core-service` も `INDEX.md`・`AGENT.md`・`docs/_index.md`・`docs/spec/` を整理し、`README.md` と `AGENTS.md` に一本化。
2. **実サブエージェント協働（2-Passループ）による公式CLI実装と検証**:
   - `team-leader`（`2f05ff1a`, `Model="pro"`）が自らコードを書かず、`tdd-red-worker`（`64572896`, `flash`）➔ `tdd-green-worker`（`ec948bed`, `flash`）➔ `compliance-reviewer`（`788d34d8`, `pro`）を計4回起動。
   - Pass 1 で生じた DTO への不要な足し算パッチを `compliance-reviewer` が検知し、Pass 2 の引き算リファクタリングで完全解消（`MUST: 0, SHOULD: 0, IMO: 1`）。
   - `core-service`（169 tests passed, Cov `93.99%`）および `agent-core` の両方で `make check-all` 完全パスを確認し、`main` へのマージと `make ws-harvest` を完遂。
