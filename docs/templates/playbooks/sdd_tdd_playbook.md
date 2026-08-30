# SDD & Double Loop TDD Playbook

このファイルは、新規機能開発・改修におけるマクロな進行表（Tracker）の雛形です。
プロジェクト開始時にこのファイルを `tasks/progress.md` としてコピーし、Session Manager がこの順序に従ってファシリテーションを行います。逆流が発生した場合は、前のフェーズの `[x]` を `[ ]` に戻してループを表現します。

## 📍 Current State (Tracker)
- **Current Phase**: 1. SPEC
- **Sub-Loop Count**: 0
- **Blockers / Notes**: None

---

## 🗺️ Execution Flow (WHATの順番)

### Outer Loop (仕様と設計)
- `[ ]` **1. SPEC (要件定義)**
  - ユーザーと `/grill-me` 等で壁打ちし、`spec.md` を完成させる。
- `[ ]` **2. DESIGN (設計方針)**
  - 既存のドメインルール（Layer 4）と照らし合わせ、アーキテクチャやディレクトリ配置を合意する。
- `[ ]` **3. ARCHITECTURE_REVIEW (局所最適化の排除)**
  - 実装に進む前に、`global-alignment-reviewer` を起動し、上記の設計が局所最適化（パッチ修正）になっていないか、システム全体のSSOTと矛盾しないかを監査させる。

### Inner Loop (TDD実装)
- `[ ]` **4. RED (テスト先行作成)**
  - `tdd-red-worker` を起動し、`spec.md` を満たして失敗するテストを書かせる。
- `[ ]` **5. GREEN (実装)**
  - `tdd-green-worker` を起動し、テストをパスさせる。
  - *(※仕様の矛盾に気づいた場合は、Phase 1 or 2 に巻き戻す)*
- `[ ]` **6. REFACTOR (構造レビューと洗練)**
  - 実装コードがドメインルールに沿っているかレビューし、修正する。
  - *(※品質Gateが通るまで、このフェーズ内でループを回す)*

### Handoff (Epicの永続化とクローズ)
- `[ ]` **6. KNOWLEDGE_SYNC (知識の永続化と矛盾解消)**
  - Epic内で作成したADRや決定事項をもとに、ルートの `AGENT.md` や `docs/` 配下の公式ドキュメントを更新する。
  - `research-worker` 等を起動し、更新漏れや古いキーワードの残骸（矛盾）がないかシステム全体を監査・修正する。
- `[ ]` **7. SENSE_MAKING (教訓の退避)**
  - Epic内で得られた学び（ハック防止策や仕組みの穴）を抽出し、Zettelkasten等（Second Brain）へ退避する。
- `[ ]` **8. CHECK-OUT (終了の儀式)**
  - 不要なワークスペースの一時ファイルをクリーンアップし、Gitコミットして人間にハンドオフする。

---

## 💡 Session Insights (未登録の教訓・知見)
作業中に得られた教訓や改善案をストックする場所。完了時にZettelkastenへ退避。
- `[ ]` 
