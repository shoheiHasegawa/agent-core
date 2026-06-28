---
status: completed
created: "2026-06-21"
---

# Epic 05: Legacy Inbox Distillation

## 概要
移行プロジェクト（Proj_Playground_Reconstruction）にて生じた、過去数年分の未処理・未フォーマットなレガシーデータ群（旧Inboxの内容）を完全に整理・消化するためのプロジェクト。
Zettelkastenの純粋性を守るため、これらは `second-brain` に直接入れるのではなく、この実行層（agent-core）で1つずつ評価・処理（蒸留）する。

## 方針 (Distillation Pipeline)
以下の3つのアクションのいずれかに仕分けし、全てを処理しきる。

1. **Delete（削除）**
   - 価値を失った一時的なメモ、古いタスクリストなどは思い切って破棄する。
2. **Distill（蒸留 / Permanent Note化）**
   - 普遍的な価値を持つ知識の種は、正規のYAMLフォーマット（`Permanent_Note_Template.md`）を適用し、タグ付けした上で `second-brain/40_Permanent_Notes/` へ投入する。
3. **Absorb（部門ルールへの吸収）**
   - 行動指針や会社のルールに関する記述は、知識ではなく「ガバナンス」であるため、`second-brain/10_Areas/` の該当部門（例えば `03_Engineering/` や `01_CEO/`）へ統合・吸収させる。

## バックログ (Backlog)
- [x] `agent-core/workspaces/Proj_Legacy_Distillation/raw_data/` に退避された全ファイル（約80件）のインベントリリストを作成し、AIによる一括仕分け（Delete/Distill/Absorb）の提案レポートを出力する。 -> **[Bypassed] 対象ファイルはすでに `second-brain/00_Inbox/` に手動で集約・移行済みのため不要。**
- [x] 提案レポートを社長がレビュー後、Agentが一括でフォーマット変換・移動処理を実行する。 -> **[Bypassed] 以降は日常のZettelkasten運用（Inbox消化タスク）として処理するため、本Epicとしてはクローズ。**
- [x] 処理完了後、`raw_data/` ディレクトリおよび本ワークスペースをTeardownする。 -> **[Bypassed] ワークスペース自体未作成のため削除不要。**
