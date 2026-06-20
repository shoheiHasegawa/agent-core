# Harvest Report: You, Inc. パラダイムシフトとデータガバナンス設計

**Date**: 2026-06-13
**Context**: Agent-Centric Architecture 実装前における、各リポジトリのディレクトリ構成調査、および `second-brain` と `life-automation` の責務再定義セッション。

## 1. Wisdom (セッションから得られた教訓・パラダイムシフト)
- **Inboxの一次受け移管**: 外部からの情報をいきなり `second-brain` に放り込むのはアンチパターン。「受付機能（Inbox・キュー）」は `agent-os` 側に移管し、AIがパース・整理した後に `knowledge-vault` へ格納すべきである。
- **純粋なZettelkastenとディレクトリ依存の脱却**: 人間の認知用UIとしてのPARA階層は維持するが、Agentから見れば「一意なIDとメタデータが付与されたフラットなグラフDB」でなければならない。
- **純粋関数への進化**: `life-automation` は「ファイルを読み書きして自動化するツール」ではなく、「文字列を受け取って計算して返す」だけの状態・副作用を持たない**純粋関数ライブラリ**へと進化させる。

## 2. Tech Debt (浮き彫りになった技術的負債)
- **情報の混入とGod Object化**: 現在の `second-brain` には「不変のナレッジ」と「日々のタスク実行ログ（`progress.md`等）」が混在しており、Zettelkastenとしての純度が落ちている。
- **Agentの作業スキーマ不在**: 各ディレクトリに何を・どう書くか（フォーマット）が厳密に定義されておらず、Agentの作業品質を均一に保つガバナンスが欠如していた。

## 3. System Improvement Proposals (システム改善案 / Next Steps)
1. **リネームとフラット化**: 実態に合わせ、リポジトリを `you-inc-hq` (オーケストレーター), `knowledge-vault` (DB), `you-inc-core` (ライブラリ) に改名し、並列（フラット）に配置する。
2. **データクレンジングの実施**: 新アーキテクチャへの物理的移行の**前**に、進行中プロジェクトの棚卸しとタスクの切り戻し、および現在の `00_Inbox` のゼロクリアを実施する。
3. **【Next Session】ディレクトリ毎の詳細設計**: 次のセッションにて、`second-brain` (`knowledge-vault`) の各ディレクトリ（Inbox, Projects, Areas, Resources）の中身が「具体的にどうあるべきか（What & How）」をさらに深掘りして定義する。

---
*Generated autonomously by AntiGravity Agent based on Global Constitution Rule 8.*
