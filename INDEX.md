# agent-core 物理ディレクトリ構造マップ

このファイルは `agent-core` の大まかな役割分担を示すマップです。
※最新の正確な内部構造は、Agent自身が `list_dir` ツールを用いて動的に確認すること。

- `backlog/`: 未着手のエピック（大規模プロジェクトの企画書）の管理
- `config/`: システム全体の設定ファイル（.env等、sops暗号化）
- `data/`: 内部タスクのSoRであるSQLiteデータベース群
- `docs/`:
  - `system/`: You_Inc 全体エコシステムの構成図やアーキテクチャ方針
  - `agent_rules/`: agent-core側の運用・オーケストレーションルール
  - `templates/`: 各種Markdownテンプレート
- `jobs/`: 自動化バッチや定期実行スクリプト（`core-service` を呼び出す薄いラッパー）
- `scratch/`: Agentが一時的に使用するサンドボックス（作業終了時に破棄）
- `skills/`: エージェントの振る舞い（Role別に階層化）
- `tools/`: Agentが手動/適宜使用するステートレスなCLIツール群
- `workspaces/`: 各プロジェクトやエピックの作業スペース（`_index.md`, `docs`, `tasks`, `scratch` の構造を持つ）
