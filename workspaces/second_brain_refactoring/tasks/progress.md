# Epic Workspace Progress (SSOT)

**【メタデータ】**
- Epic: `second_brain_refactoring`
- 種別: `[機能改修]`
- 現在地: `[Tier 1A: 協働仕様策定中]`
- 次回アクション: `sdd-spec-writer` による 6大観点仕様（`src/application/second_brain/spec.md`）の策定・壁打ちと Human Gate 承認

---

## 📋 タスク進捗チェックリスト

### 1. 仕様策定フェーズ (Loop 1: sdd-spec-writer)
- [ ] 要求のヒアリング・背景の深掘り (Socratic Discovery)
- [ ] 6大観点ストレステスト（エッジケース・境界値・ファイル衝突等の壁打ち）
- [ ] `src/application/second_brain/spec.md` の作成・更新（Timeless SSOT）
- [ ] **【Human Gate】ユーザーによる仕様承認 (Approve)**

### 2. TDD自律実装フェーズ (Loop 2: sdd-loop-orchestrator)
- [ ] Outer Red: `tests/integration/second_brain/` に失敗する結合テストを作成 (Proof of Red)
- [ ] Inner Loop: `src/` 実装 & `tests/unit/` 単体テスト補強 (Green)
- [ ] Quality Gate: `make check-all` (全テストPASS, カバレッジ>=90%, Linter, AST整合性)
- [ ] Compliance Review: 独立司法エージェントによる合憲性・ルール審査
- [ ] Commit & Handoff: アトミックコミットと進捗完了記録

---

## 💡 Session Insights (未登録の教訓・知見)

- `[ ]` **エラーハンドリング**: ファイル重複時は `FileExistsError`、未存在は `FileNotFoundError`、パラメータ不正は `ValueError` で一貫させる。

---

## 📝 メモ・コンテキスト (Scratchpad)
- Zettelkasten ノートの登録におけるフロントマター、リンク整合性、日跨ぎ、パストラバーサル防御などの観点を網羅する。
