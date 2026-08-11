---
type: backlog
created: "2026-08-10"
tags: [agentic-os, tech-debt, maintenance]
---

# 📝 Backlog: 不要なZK検索ツールとSKILLルールの断捨離

## 📖 Background (なぜやるのか / 背景と課題)
AIの汎用的な探索能力（grep_search等）が自作の検索スクリプト（`agent-core/tools/search_zettelkasten.py`）を上回っており、当該スクリプトが使われない負債（かつ環境変数不足でエラーになる状態）となっている。
AgentはSKILLに定義された手続き的なルール（How）を無視して目的（What）を果たすことが観測された。この「使われないツール」と「無視されるHowの制約」は将来的なハルシネーションや不整合の温床となるため、システムから排除すべきである。

## 🎯 Goal & DoD (何を目指すのか / 完了条件)
- [ ] `agent-core/tools/search_zettelkasten.py` が削除されていること。
- [ ] `agent-core/skills/zk-distillation-orchestrator/SKILL.md` の「1. 文脈の取得」から特定のスクリプトを使用する指示が削られ、手段（How）を特定しない普遍的な指示にリファクタリングされていること。
