# Idea: Review Watcher Zettelkasten Integration

## 概要
現在、`review_watcher` は AgentOS の教訓（`AGENTS.md` / `personas/*.md`）の自己成長ループに特化して稼働している。
しかし、当初の構想（`spec.md`）では、教訓だけでなく、AIが得た普遍的な洞察を**人間のための第2の脳（Zettelkasten）にも自動でノート化・定着させる**ことが目標だった。

これをMVPのスコープから分離し、本番フェーズ（Phase 3）の拡張アイデアとしてここに記録する。

## 実現したいユースケース
- Midnight Defrag や Distill Memory が生成した提案（Proposal）が人間に承認された際、教訓としての定着だけでなく、必要に応じて新しい Permanent Note を自動生成する。
- 既存のノートと関連が深い場合は、自動でノート間にリンクを張り巡らせる。

## 不足している実装（残タスク）
1. **`SettlementService` の実装**
   - `life-automation/src/application/knowledge/review_watcher/` 内に、知識の定着を司るサービスクラスを新規作成する。
2. **`MarkdownRepository` の DI と連携**
   - Zettelkastenへのノート書き込み処理を実装する。
3. **LLMプロンプトの拡張**
   - Proposalに「この知識は Zettelkasten に反映すべきか？（boolean）」のフラグを持たせ、反映すべき場合は `Note Title` や `Tags` も同時に推論させるように `gemini_client.py` を拡張する。

## 検討事項
- 人格（Persona）と人間の知識（Zettelkasten）は分離すべきか？
  - Agentはあくまで「作業の教訓」を蓄積し、Zettelkastenは「普遍的な知識」を蓄積する。
  - すべての Proposal を Zettelkasten に入れるとノイズになるため、フィルター条件を厳密に定義する必要がある。
