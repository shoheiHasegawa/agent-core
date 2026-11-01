---
name: Standard Issue
about: 通常の課題・改善起票用 Markdown テンプレート
title: "[Prefix] 課題タイトル"
labels: ["type:feature", "prio:p2-backlog", "size:M"]
---

## 🎯 WHY (背景と目的)
<!-- なぜ今これをやるのか？どのようなエントロピーや不便を解消するか？放置した場合のコストは？ -->

## 📋 WHAT / DoD (スコープと定量的完了条件)
<!-- 客観的・定量的に検証可能な合格判定基準を箇条書きで記載 -->
- [ ] 条件1 (例: `make check-all` 通過)
- [ ] 条件2 (例: CLIコマンドの挙動検証)

## 🚫 Non-Scope (今回は絶対にやらないこと)
<!-- 過品質や迷走を防ぐための境界線。今回はやらないことを明示 -->
- 今回はスコープ外とする項目

## 🛠️ HOW & CONSTRAINTS (想定アプローチと制約)
<!-- 対象リポジトリ、準拠すべき設計原則、禁止事項、考慮事項 -->
- 対象リポジトリ: `core-service` / `agent-core` / `second-brain`
- 留意事項・制約:
