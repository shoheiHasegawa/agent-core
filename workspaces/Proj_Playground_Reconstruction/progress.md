# Progress Log

### Phase 1: 計画段階 (Planning)
- `[x]` プロジェクトディレクトリの立ち上げと情報整理の枠組み作成
- `[x]` To-Beアーキテクチャの基本方針とディレクトリ構成の決定（ADR群の反映）
- `[x]` 移行計画書 (Migration Plan) の策定
- `[x]` **You, Inc. 会社アーキテクチャ・3大リポジトリ（agent-core, second-brain, core-service）の定義完了**
- `[x]` **同名リポジトリ衝突を回避するための退避・移行手順の確定 (03_repository_migration_plan.md)**
- `[x]` 未決事項・必要SKILLの洗い出し (open-item更新)
- `[ ]` **未決事項の解決・仕様の確定**（ダッシュボード設計、WIP制限、RAG仕様、承認UI等）

### Phase 2: TO-BEの作成 (Preparation & Build)
- `[ ]` 旧 `second-brain` の `second-brain-legacy` への退避とリネーム
- `[ ]` 3大リポジトリ (`agent-core`, `second-brain`, `core-service`) の初期化とルートへの配置（フラット構造）
- `[ ]` `agent-core` の隔離作業用 Dockerコンテナ環境の構築 (Harness)
- `[ ]` `second-brain` のベースディレクトリ（00, 10, 30, 40）の作成
- `[ ]` 各リポジトリの自己記述ドキュメント（INDEX.md, RULES.md等）のひな形作成
- `[ ]` HQ側の必須機能（ダッシュボード、WIP制限チェッカー）の初期実装

### Phase 3: 移行作業 (Migration)
- `[ ]` 旧 `second-brain` のReadOnly化とParallel Buildの開始
- `[ ]` 既存の `10_Projects` 内のプロジェクトをHQのWorkspaceへ移管
- `[ ]` 既存の `30_Resources` からPermanentノートを抽出し `40_Zettelkasten` へ移行
- `[ ]` `40_Archives` の精査、Distill or Deleteの実施
- `[ ]` 旧 `second-brain` ディレクトリの凍結・廃止完了
