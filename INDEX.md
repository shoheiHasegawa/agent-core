# agent-core 物理ディレクトリ構造マップ

- `config/`: システム全体の設定ファイル（.env等）
- `docs/`: 構成図やアーキテクチャ・ルール類
  - `architecture/`: You_Inc 全体エコシステムの構成図
  - `rules/`: agent-core側の運用・オーケストレーションルール
- `epics/`: エピック（大規模なプロジェクトやゴール）の管理
- `factories/`: core-serviceの依存性を注入する組み立て工場 (Composition Root)
- `jobs/`: 自動化バッチや定期実行スクリプト
- `queue/`: Agent間の非同期通信バッファ（1タスク＝1パケット単位で処理対象とメタデータを格納）
- `skills/`: エージェントの拡張スキル定義
- `templates/`: 各種テンプレート
- `tools/`: Agentが使用するツールや検証スクリプト
- `workspaces/`: 各プロジェクトやエピックのフラットな作業スペース（階層化せず、完了後に削除・破棄する）
