# Phase 05: Zettelkasten Distillation (非同期クレンジングと知識の蒸留)

## 概要
本タスクは、`second-brain` の Inbox 等に蓄積された日々のメモ（Fleeting Notes）や、AIとの対話から自律生成された「Harvest Report」を定期的にレビューし、体系的な知識（Permanent Notes）へと昇華（Distillation）させる継続的プロセスである。

## 作業手順（チェックリスト）

- [ ] **1. Harvest Report の取り込み (最優先)**
  - AIが自律的に `second-brain/00_Inbox/01_Review_Queue/`（または検疫エリア）へ出力した「Harvest Report」をレビューする。
  - システム改善案や個人の教訓（Wisdom）を、エージェントの実体ファイル（`personas/xxx_agent.md` 等）の `Accumulated Wisdom` セクションへ反映、または該当する Zettelkasten ノートに追記する。
- [ ] **2. Inboxのトリアージと蒸留**
  - `second-brain/00_Inbox` 内の未整理メモを確認する。
  - 一時的なメモから「普遍的な概念」を抽出し、`10_Projects` や `30_Resources` に移行して Permanent Note として書き直す。
  - 不要となった元メモは `40_Archives` へ移動するか破棄する。
- [ ] **3. ノート間の双方向リンク強化**
  - 新たに作成したノートに対して、関連する既存ノートへの双方向リンク（例: Obsidian の `[[Note Name]]` 形式）を付与する。
  - 孤立しているノート（Orphan Notes）がないかをグラフビュー等で確認し、ハブとなる MOC (Map of Content) ノートに接続する。
- [ ] **4. メタデータのクレンジング**
  - ノートのFrontmatter（YAML）に適切な `tags`, `aliases`, `date` 等が統一されたフォーマットで付与されているかを確認・修正する。
