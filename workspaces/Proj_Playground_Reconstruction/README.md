# Proj_Playground_Reconstruction

## プロジェクト概要
`second-brain` と `life-automation` の間にある密結合と技術的負債を解消し、ドメイン駆動設計（DDD）に基づいた健全なアーキテクチャへと再構築するためのプロジェクト。

## ドキュメント構成と厳密な責務 (What & Bounds)
ASIS（現状）とTOBE（未来）の混同を防ぐため、本プロジェクトのドキュメントは以下の境界ルールに従います。

- `as-is/` (現状と課題 - "Where we are")
  - 変更を加える前の現在の状態とペインポイントの事実記録。解決策や移行手順は記載禁止。
- `decision/` (意思決定/ADR - "Why we change")
  - アーキテクチャ変更の「理由」と「歴史的経緯」。Before/Afterの比較はここにのみ許容。
- `to-be/` (理想像・仕様 - "Where we want to be")
  - システム完成後の純粋な仕様書。ASIS用語（旧〜等）やBefore/Afterの比較、移行手順は一切記載禁止。
- `migration/` (移行計画 - "How we get there")
  - ASISからTOBEへ安全に移行するための具体的な手順書（ブリッジ）。
- `progress.md`: PJの進捗管理。計画段階で「未決事項の解決（仕様化）」を必須とする。
- `open-item.md`: 検討中の未確定要件。決定事項はADR等に移動しクローズする。

## 進捗ログ
- 2026-06-13: `10_Projects` の分離と `01_Sense_Making` の新設（ADR 0005）
- 2026-06-13: `30_Resources` と `50_Zettelkasten` の分離・フラット化（ADR 0006）
- 2026-06-13: `20_Areas` のガバナンス・エンジンとしての再定義（ADR 0007）
