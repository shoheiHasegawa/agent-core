# Epic Workspace Progress (SSOT)

**【メタデータ】**
- Epic: `agent_company_architecture`
- 目的: 「社長 ⇄ 秘書 ⇄ チームリーダー ⇄ メンバー」で稼働するAgent会社の組織構造・Issue管理・Sandbox環境・学習ループを定義し、MVP基盤を構築する。
- 完了条件: WHY-WHAT-HOWのアーキテクチャ合意と、MVP Step 1〜3 の基盤移行・実サブエージェント試運転・`main` マージ完了。

---

## 📋 タスクリスト (Task Breakdown)

- `[x]` **Phase 1〜4: WHY / WHAT / HOW のアーキテクチャ設計とロードマップ策定 (`docs/00_Architecture_Discussion.md` ➔ `docs/architecture.md` へ昇格)**
- `[x]` **Phase 5: MVP 実装（Step 1〜3 の順次実行）**
  - `[x]` **Step 1 (Bootstrap & Worktree Harness)**:
    - `[x]` `main` 未コミット変更の整理・コミット（`.pem` 鍵の除外含む）
    - `[x]` `validate_sdd.py` と `check_markdown_links.py` の `core-service` 移管・単体 `make check-all` 自立化
    - `[x]` `agent-core/Makefile` に `make ws-new` / `make ws-harvest` / `make ws-list`（`tools/workspace_manager.py`）を実装し、Worktreeマウント成功
  - `[x]` **Step 2 (3-Layer Docs, Experience Stock & 7 Core Skills)**:
    - `[x]` 3階層 `GEMINI.md` / `AGENTS.md` 整備と `README.md` 一本化（`INDEX.md` 廃止、`/you_inc/GEMINI.md` シンボリックリンク解除）
    - `[x]` 旧 `docs/system/`・`docs/agent_rules/`・旧テンプレート（計22ファイル）の引き算削除と、`docs/architecture.md`・`docs/rules/`（2ファイル）・`docs/experiences/`（2ファイル）への集約
    - `[x]` 既存19スキルの廃止と、4大フロー逆算の7コアSKILLの作成・Linter検証パス
  - `[x]` **Step 3 (DI Self-Containment, Official CLI & Multi-Agent E2E Trial)**:
    - `[x]` `core-service` の DI自己完結化（`CoreServiceConfig.from_env()` & `CoreServiceContainer.from_env()`）と Python 3.13+ 引き上げ
    - `[x]` `agent-core/app_context.py` および旧SQLite用 `tools/`・`jobs/` の完全廃止（-1,102行の引き算達成）
    - `[x]` `team-leader (pro)` ➔ `tdd-red-worker (flash)` ➔ `tdd-green-worker (flash)` ➔ `compliance-reviewer (pro)` の実サブエージェント起動（計4回）により、`core-service/src/entrypoints/cli/main.py` を2-Passスパイラルループで実装・監査パス（169 tests passed, Cov 93.99%, MUST=0, SHOULD=0）
    - `[x]` `core-service` / `agent-core` の独立 GitHub Actions CI（`.github/workflows/ci.yml`）配置完了
- `[x]` **Phase 6: クローズ・`main` マージ・Worktree回収 (`make ws-harvest`) と3点内省ブリーフィング**
