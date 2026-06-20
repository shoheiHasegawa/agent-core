# ADR 0018: Redefine Obsidian as View Layer

## Date
2026-06-14

## Context
従来のPARAメソッドにおいて、ObsidianはMarkdownの保存場所（DB）とUI（View）、そしてプラグイン等の設定（Config）が混ざり合った存在だった。
Agent駆動アーキテクチャ（You, Inc.）への移行にあたり、手動でのディレクトリ作成を防ぐ「システム的なWIP制限（`make workspace` 等のコマンド強制）」や「ダッシュボードの仕様」が課題として挙がっていた。

## Decision
1. **Obsidianの「View層」としての再定義**: Obsidian を単なるエディタではなく、`second-brain`（データ層）を可視化する「UI / フロントエンド」として明確に再定義する。
2. **`90_Meta` への内包**: `.obsidian/` の設定ファイル、Dataview用のクエリ、ダッシュボード用Markdownなど「Viewの構成要素」はすべて `second-brain/90_Meta/` 配下に集約し、純粋なナレッジと分離する。
3. **運用ルールによる制約**: 複雑なシステムバリデーション（コマンドによるWorkspace生成強制）を放棄し、「`second-brain` 側に勝手にディレクトリを作らない」「ダッシュボードはDataviewプラグイン等で動的に表示する」という運用ルールに倒す。

## Consequences
- **Positive**: 
  - システム開発のオーバーヘッド（Over-engineering）を防ぐことができる。
  - View（Obsidian + Dataview）と Controller（AgentのYAMLタグ更新）が分離され、SOLIDの開放閉鎖の原則（OCP）に沿った拡張性の高い設計になる。
- **Negative**:
  - ユーザーが手動でディレクトリを作るなどの運用ルール違反をした場合、システム（Agent）がそれを検知できない状態（野良プロジェクト化）になるリスクが残る。
