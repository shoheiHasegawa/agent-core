# Epic Workspace Progress (SSOT)

**【メタデータ】**
- Epic: `agent_company_architecture`
- 目的: 「社長 ⇄ 秘書 ⇄ チームリーダー ⇄ メンバー」で稼働するAgent会社の組織構造・Issue管理・Sandbox環境・学習ループを定義し、MVP基盤を構築する。
- 完了条件: WHY-WHAT-HOWのアーキテクチャ合意と、MVP Step 1〜3 の基盤移行完了。

---

## 📋 タスクリスト (Task Breakdown)

- `[x]` **Phase 1: WHY & 組織トポロジーの定義 (Organization & Communication)**
  - `[x]` 専用ワークスペース `agent_company_architecture` の立ち上げ
  - `[x]` 社長・秘書・チームリーダー・メンバー（実装者・独立レビュアー）の階層構造の確定
  - `[x]` 未決事項発生時の介入プロトコル（秘書経由 vs チームリーダー直接対話）の確定
- `[x]` **Phase 2: WHAT & 情報管理・Gitガバナンス・ループ設計の定義**
  - `[x]` 会社のIssue管理基盤の決定（GitHub Issues を採用）
  - `[x]` Workspaceのブランチ戦略の決定（方式A: `git worktree` + PR回収）
  - `[x]` 3リポジトリ（`core-service`, `agent-core`, `second-brain`）の品質ゲート（CI観点）の定義
  - `[x]` 「SKILLは薄く、思考原則は鋭く、経験は厚く」の3層知識構造と2系統学習還流（Agent改善 vs 社長内省）の合意
  - `[x]` Argon / Flash の配分と「分母固定 × 引き算レビュー」の合意
  - `[x]` 社長の2大窓口（PC＝Antigravity / スマホ＝Geminiアプリ × Google Calendar/Tasks × Obsidian連携）の決定
- `[x]` **Phase 3: HOWの基本構造（文書階層・DDD境界・DI/Config・通信規約）の合意**
  - `[x]` 既存19スキルの退避と、4大業務フロー逆算によるゼロベースSKILL構築方針の決定
  - `[x]` コンテキスト劣化・圧迫を防ぐ「ファイル参照渡し（Pass-by-Reference）」通信プロトコルの合意
  - `[x]` `README.md` 一本化と `AGENTS.md`（本社起動＆Workspace常駐メモリ）の役割定義
  - `[x]` `core-service`（DI組み立て・公式CLI集約）と `agent-core`（`config/secret` 注入でキックするだけ）の境界確定
- `[x]` **Phase 4: HOWの詳細設計とアジャイル実装ロードマップへのブレイクダウン**
  - `[x]` 前例（Precedent）ベースの3段階判断トリアージと、社長のブラックボックス化を防ぐ「3点内省ブリーフィング」の定義
  - `[x]` 自律ループの5大定義項目、後続波及（上流の曖昧さ＝MUST）を軸にした重要度分類、および「2-Pass スパイラル（貫通 ➔ 引き算リファクタリング）」の定義
  - `[x]` ギャップ分析と MVP 実装ロードマップ（Step 1〜4）の確定（`docs/00_Architecture_Discussion.md` 完成）
- `[ ]` **Phase 5: MVP 実装（Step 1〜3 の順次実行）** 👈 Current Phase!
  - `[ ]` **Step 1 (Bootstrap)**: 現状の `main` 未コミット変更の整理、`validate_sdd.py` の `core-service` 移管、`make ws-new` / `ws-harvest` の構築
  - `[ ]` **Step 2 (Headquarters & Skills)**: 3階層 `GEMINI.md` / `AGENTS.md` 整備、既存19スキル退避＆経験抽出、新コアSKILL作成
  - `[ ]` **Step 3 (DI & Official CLI)**: `core-service` の DI自己完結化・`entrypoints/cli` 移管、`agent-core/app_context.py` 廃止、3リポジトリCI配置
