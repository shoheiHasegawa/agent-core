# Harvest Report: Inboxの物理的分離とObsidian UXの再定義

**Date**: 2026-06-13
**Context**: 新アーキテクチャ（You, Inc.）における `00_Inbox` のあり方の議論から、iCloud同期の制約を活かしたアーキテクチャの純化と、新リポジトリへの段階的移行戦略の合意まで。

## 1. Wisdom (セッションから得られた教訓)
- **摩擦ゼロとアーキテクチャ純化の両立**: 「人間が雑に書き捨てる場所」と「型を保証すべきDB」を同じリポジトリ（Vault）に同居させると、必ず破綻（例外ルールの発生）が起きる。これらを**物理的に分離（iCloud Capture Zone と knowledge-vault）**し、Agentを「国境の入国審査官・清書係」として配置することで、最高のUXと完璧なデータガバナンスが両立する。
- **Seed保管庫としてのInbox**: DB内のInboxは「ゴミ溜め」ではなく、Agentによって綺麗に陳列・メタデータ付与された「人間のための思考のショーケース」である。完全フラット構造とDataviewを組み合わせることで、ノイズのない洗練された体験を作れる。

## 2. Tech Debt (浮き彫りになった技術的負債)
- **旧Inboxへのゴミの蓄積**: 現在の `second-brain/00_Inbox` には、旧時代のスクリプトによって持ち込まれたフォーマット未整備のファイルが蓄積している。これらをそのまま新環境に持ち込むことはできない。

## 3. System Improvement Proposals (システム改善案 / Next Steps)
1. **Parallel Build（段階的移行）の実行**: 既存の `second-brain` を改修するのではなく、新しい `knowledge-vault` リポジトリをゼロから立ち上げ、徐々にデータをクレンジングしながら移管していく。
2. **クレンジング作業の開始**: 次のステップとして、現在 `00_Drop_Zone` や `02_Review_Queue` に眠っているデータのトリアージと、新環境への移行手順の確立に着手する。

---
*Generated autonomously by AntiGravity Agent based on Global Constitution Rule 8.*
