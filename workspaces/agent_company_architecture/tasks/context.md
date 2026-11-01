# 📍 Current Context (Working Memory)

> **⚠️ Agentへの絶対ルール**
> - このファイルは**最大50行以内**に保つこと。これを超える場合は古い情報を要約圧縮、または削除すること。
> - 対話ログのコピペは禁止。Agent自身の言葉で抽象化・要約したメタ認知情報のみを記載すること。
> - ユーザーに返答する前に、必ず自律的にこのファイルを最新の文脈に上書き（Update）すること。

---

## 🎯 現在の焦点 (Current Focus / Handoff Point)
- **Phase 4（HOW詳細設計・MVPロードマップ策定）が100%完了**し、[00_Architecture_Discussion.md](file:///Users/shoheihasegawa/you_inc/agent-core/workspaces/agent_company_architecture/docs/00_Architecture_Discussion.md) に全決定事項を統合済み。
- 次アクションとして **Phase 5 - Step 1（Bootstrap：`main` 未コミット変更の整理、`validate_sdd.py` の `core-service` 移管、`make ws-new` / `ws-harvest` の実装）** に着手する。

## 📌 最終確定したアーキテクチャの核心 (Architecture Essence)
1. **3層の知識構造（「SKILLは薄く、原則は鋭く、経験は厚く」）**:
   - ① `SKILL.md`（薄いI/O契約と停止条件）、② `docs/rules/`（DDD/SOLID/YAGNI＋「引き算ファースト」の思考プロセス）、③ `docs/experiences/`（失敗パターンや過去の社長判断＝前例のストック。リーダーがタスクに応じてJIT注入）。
2. **前例ベース3段階トリアージと社長の内省化**:
   - 🟢前例あり＝自律決定＆事後承認、🟡応用＝根拠＋推奨案で1タップ承認、🔴初判断＝事前確認（判断後は経験ストックへ記録し次回から🟢へ）。
   - クローズ時は「①何をなぜ変えたか、②Agentの学びと仕組み化、③社長自身の気づき（Second Brain）への問い」の3点ブリーフィングでブラックボックス化を防ぎ自己成長に繋げる。
3. **2-Pass スパイラル × SDD/TDD ダブルループ**:
   - 後続工程を狂わせる上流（`spec.md` 等）の曖昧さは無条件で 🔴 `MUST`。
   - **Pass 1（貫通）**で契約（Outer/Inner）を一通り動かし、**Pass 2（引き算と洗練）**で溜まった 🟡 `SHOULD` と責務抽出（UseCase➔Domain）を一括リファクタリングして収束させる（同一エラー2回・最大3往復で強制停止）。
4. **DI・公式CLIの `core-service` 集約と Worktree 運用**:
   - 公式CLIと `validate_sdd.py` は `core-service` に集約し、`agent-core` は `config/secret` を注入してキックするだけ（脱 `app_context.py`）。

## 🚀 直近の実行ステップ (Step 1: Bootstrap)
1. `core-service` と `agent-core` の現在の `main` 未コミット変更を点検・コミットし、クリーンなベースラインを作る。
2. `validate_sdd.py` を `core-service/tools/` へ移管し、`core-service` 単体で `make check-all` が通るようにする。
3. `agent-core/Makefile` に `make ws-new` / `make ws-harvest` を実装し、Step 2 以降を Worktree＋PR 運用に乗せる。
