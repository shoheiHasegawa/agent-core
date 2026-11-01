# 📍 Current Context (Working Memory)

> **⚠️ Agentへの絶対ルール**
> - このファイルは**最大50行以内**に保つこと。これを超える場合は古い情報を要約圧縮、または削除すること。
> - 対話ログのコピペは禁止。Agent自身の言葉で抽象化・要約したメタ認知情報のみを記載すること。
> - ユーザーに返答する前に、必ず自律的にこのファイルを最新の文脈に上書き（Update）すること。

---

## 🎯 現在の焦点 (Current Focus / Handoff Point)
- **「`WHY ➔ WHAT ➔ HOW` 原則」と「Timeless SSOT（時系列ノイズ排除）」を単なる文書記載に留めず、① Linter（`tools/audit_skills.py`）による機械的検知、② 独立レビュアー（`compliance-reviewer`）の監査観点、③ 経験ストック（`[EXP-08]`）の3層で完全に仕組み化・コミット完了**。
- 社長へ仕組み化の完了を報告し、クローズ（または `second-brain` への内省蒸留）を確認する。

## 📌 完了サマリー (Final Verification Digest)
1. **`docs/architecture.md` の Timeless SSOT 化**:
   - 移行期の時系列ノイズ（ステータス、旧19スキル廃止、Step 1〜4ロードマップ）を全削除し、冒頭にドキュメント自身の **WHY（①会社の現在地の俯瞰・ブラックボックス化防止、②将来のカイゼン時のベースライン）** を明記。
   - **1. WHY（4大設計思想）➔ 2. WHAT（4層組織図・前例3段階トリアージ・SoR境界）➔ 3. HOW（4大業務フローのシーケンス図・2-Passループ）➔ 4. カイゼン規約** の構造へ刷新。
   - アジャイル段階移行のノウハウは [`agent_antipatterns_and_precedents.md`](../../../docs/experiences/agent_antipatterns_and_precedents.md) の **`[PREC-04]`** として経験ストックへ移管。
2. **思考のOSへの `WHY ➔ WHAT ➔ HOW` 原則のインストール**:
   - [`thinking_os_and_loop_principles.md`](../../../docs/rules/thinking_os_and_loop_principles.md) の第0章に「思考の最上位アルゴリズム：`WHY ➔ WHAT ➔ HOW` の順序原則（HOWへの飛びつき禁止・全ドキュメントへのWHY明記鉄則）」を追加し、他文書（[`zettelkasten_and_dialog_principles.md`](../../../docs/rules/zettelkasten_and_dialog_principles.md), [`AGENTS.md`](../../../AGENTS.md), [`README.md`](../../../README.md), [`core-service/docs/architecture.md`](../../../../core-service/docs/architecture.md)）もすべて `WHY ➔ WHAT ➔ HOW` 構造に統一。
