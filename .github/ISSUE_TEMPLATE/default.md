---
name: Standard Issue
about: 通常の課題・改善起票用 Markdown テンプレート
title: "[Prefix] 課題タイトル"
labels: ["type:feature", "prio:p2-backlog", "size:M"]
---

## 🎯 WHY & Value (背景・目的と実現する価値)
<!-- なぜ今これをやるのか（放置コスト）？完了すると何がどう良くなるか（Before ➔ After）？ -->

## 📋 WHAT / DoD (完了イメージと定量的完了条件)
<!-- 検証可能な合格判定基準。先行Issue待ち等で未決の細部は捏造せず `TBD（〜完了後に確定）` と明記 -->
- [ ] 条件1 (例: `make check-all` 通過)
- [ ] 条件2 (未決時は `TBD: Phase 0 で確定`)

## 🚫 Non-Scope (今回はやらないこと・境界 ※任意／着手時確定可)
<!-- 見えているスコープ外の境界線があれば記載。未決なら着手時に team-leader と確定 -->
- 今回はスコープ外とする項目

## 🛠️ CONSTRAINTS (対象リポジトリと絶対制約 ※詳細HOWは書かない)
<!-- 対象リポジトリ、準拠すべき設計原則・禁止事項 -->
- 対象リポジトリ: `core-service` / `agent-core` / `second-brain`
- 制約:
