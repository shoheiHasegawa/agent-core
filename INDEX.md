# agent-core 物理ディレクトリ構造マップ

- `config/`: システム全体の設定ファイル（.env等）
- `docs/`: 構成図やアーキテクチャ・ルール類
  - `architecture/`: You_Inc 全体エコシステムの構成図
  - `rules/`: agent-core側の運用・オーケストレーションルール
- `epics/`: エピック（大規模なプロジェクトやゴール）の管理
- `factories/`: core-serviceの依存性を注入する組み立て工場 (Composition Root)
- `jobs/`: 自動化バッチや定期実行スクリプト。直接のドメインロジックは持たず、`app_context.py` を経由して `core-service` を呼び出す薄いラッパー。
  - `generate_daily_briefing.py`: 毎朝実行。1日の計画生成とカレンダー同期。（仕様SSOT: `docs/03_Core_Service_Scheduler_Constraints.md` 等）
  - `sync_worklogs.py`: 毎晩実行。Mobile Vaultの実績を読み取りTask Registryを更新。（仕様SSOT: `docs/02_Mobile_Vault_Integration_Spec.md`）
- `queue/`: Agent間の非同期通信バッファ（1タスク＝1パケット単位で処理対象とメタデータを格納）
- `skills/`: エージェントの拡張スキル定義
- `templates/`: 各種テンプレート
- `tools/`: Agentが手動/適宜使用するツールや検証スクリプト。
  - `validate_sdd.py`, `pre_handoff_verify.sh`: 品質保証およびアーキテクチャ検証ツール。
  - `peek_mobile_inbox.py`, `process_mobile_packet.py`: Mobile Vault との連携ツール（inbox-triageにて使用）。
  - `search_zettelkasten.py`, `register_zettelkasten_note.py`: Second Brain の操作ツール。
- `workspaces/`: 各プロジェクトやエピックのフラットな作業スペース（階層化せず、完了後に削除・破棄する）
