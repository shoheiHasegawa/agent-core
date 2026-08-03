# Epic Workspace Progress (SSOT)

**【メタデータ】**
- Epic: `{{epic_name}}`
- 種別: `[新規機能開発]` / `[機能改修]` / `[バグ修正]`
- 現在地: `[Tier 1A: 協働仕様策定中]` ➔ `[Tier 1B: 自律TDD実装中]` ➔ `[完了]`
- 次回アクション: 

---

## 📋 タスク進捗チェックリスト

### 1. 仕様策定フェーズ (Loop 1: sdd-spec-writer)
- [ ] 要求のヒアリング・背景の深掘り (Socratic Discovery)
- [ ] 6大観点ストレステスト（エッジケース・境界値の壁打ち）
- [ ] `src/application/<domain>/spec.md` の作成・更新（Timeless SSOT）
- [ ] **【Human Gate】ユーザーによる仕様承認 (Approve)**

### 2. TDD自律実装フェーズ (Loop 2: sdd-loop-orchestrator)
- [ ] Outer Red: `tests/integration/` に失敗するテストを作成 (Proof of Red)
- [ ] Inner Loop: `src/` 実装 & `tests/unit/` 単体テスト補強 (Green)
- [ ] Quality Gate: `make check-all` (全テストPASS, カバレッジ>=90%, Linter, AST整合性)
- [ ] Compliance Review: 独立司法エージェントによる合憲性・ルール審査
- [ ] Commit & Handoff: アトミックコミットと進捗完了記録

---

## 💡 Session Insights (未登録の教訓・知見)
作業中に得られた普遍的な教訓・設計判断・AIのハック防止策などをストックする場所。
セッション終了時に Agent が自動スキャンし、Zettelkasten（`second-brain`）への登録を提案する。

- `[ ]` **タイトル**: 教訓の内容・詳細 (tags: タグ)

---

## 📝 メモ・コンテキスト (Scratchpad)
作業中の気付き、ハマったポイント、次回への備忘録など。
