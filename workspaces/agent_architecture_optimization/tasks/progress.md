# Epic Workspace Progress (SSOT)

**【メタデータ】**
- Epic: `agent_architecture_optimization`
- 種別: `[アーキテクチャ最適化・リファクタリング]`
- 現在地: `[Phase 1: 課題・改善ポイントの洗い出し完了]` ➔ `[Phase 2: 全体最適のための改善案の議論・合意]` ➔ `[Phase 3: 対策の実装]`
- 次回アクション: Phase 2（全体最適のための各論点ディスカッションと確定）

---

## 📋 タスク進捗チェックリスト

### Phase 1: 課題の洗い出しと記録 (Discovery & Problem Definition)
- [x] コンテキスト効率・キュー残骸・パス不整合の課題特定
- [x] `queue/` 完全撤廃方針（Zero-Queue Architecture）の採用決定・記録
- [x] ループエンジニアリング・モデル選択（Pro一律継承）の課題特定
- [x] ハーネスエンジニアリング・プロンプト重複・空ファイル・パスハック残存の課題特定
- [x] 課題正本ドキュメント (`docs/00_Identified_Issues_and_Challenges.md`) の更新

### Phase 2: 局所最適を避けた全体最適のための改善案の議論 (Holistic Architecture Design)
- [ ] 1. Zero-Queue Architecture 移行詳細（`tasks/context.md` + `epics/` への完全移行）
- [ ] 2. サブエージェント Model 最適化マトリクス（Flash vs Pro vs Role Switching）
- [ ] 3. プロンプト純度向上（空ファイル削除、重複ルールのLinter/憲法への集約、パスハック是正）
- [ ] 4. ハーネス強化（`pre_handoff_verify.sh` に `context.md` 行数・クリーンネス自動検査を追加）
- [ ] 5. 3-Step Lazy Bootstrapping プロトコルの確定

### Phase 3: 対策の実装と検証 (Implementation & Verification)
- [ ] `queue/` ディレクトリの完全撤廃と関連コード（`session-manager`, `SystemEventGateway` 等）のリファクタリング
- [ ] 全 `SKILL.md` の Model 指定および Role Switching 境界・記述矛盾の修正
- [ ] `core-service/docs/rules/api_gateway.md` 等の空ファイル整理
- [ ] ドキュメント間パス（`tasks/progress.md`, `tasks/context.md`）の完全統一
- [ ] クリーンネス Linter（`verify_cleanliness.py`）の実装と `pre_handoff_verify.sh` への統合
- [ ] `audit_skills.py` および `make check-all` による全体検証パス

---

## 💡 Session Insights (未登録の教訓・知見)
- `[ ]` **Zero-Queue Architecture**: 誰も消費しない中間キューは必ずデジタルゴミ箱化する。状態の真実（SSOT）があるなら、キューは作らず直接SSOT（`tasks/context.md`）を参照・更新すべき。
- `[ ]` **Harness vs Prompt Rule Balance**: プロンプトで自然言語ルールを暗記させると認知負荷が増大する。ルールはLinter/ASTのハードゲートで機械的に落とし、プロンプトは最小限の文脈のみを渡すべき。

---

## 📝 メモ・コンテキスト (Scratchpad)
- 修正作業は個別に行わず、Phase 2 で全体設計を合意した後に Phase 3 で一括してアトミックに実施する。
