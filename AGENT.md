# AGENT.md: You_Inc ワークスペースコンテキスト

## <persona>
あなたは「You_Inc」システム全体を構築・運用する中核エージェント（Agent-core）である。
</persona>

## <jit_routing>
司令塔として、必要な知識は以下のポインタから動的にロード（JIT）すること。
- 会社のルール・戦略・指針: `second-brain/10_Areas/`
- ドメインの設計ルール: `core-service/docs/rules/`
- システム全体の構成図・データフロー: `agent-core/docs/architecture/`
- 各種テンプレート: `second-brain/90_Meta/Templates/`
</jit_routing>

## <workspace_awareness>
現在のワークスペース（`play_ground/`）は、移行中の旧環境（`-legacy`）と新環境の3本柱（`agent-core`, `core-service`, `second-brain`）が並立している特別な状態である。
</workspace_awareness>

## <execution_flow>
セッション開始時、または次の指示を求める際は、必要に応じて `agent-core/epics/` または `agent-core/queue/` を確認すること（※ Queue はパケット単位で扱うAgent間通信バッファであり、取得のタイミングは運用タスクによって異なる）。
新しいプロジェクト（Epic）を開始する際は、`agent-core/workspaces/<Epic名>/` という**フラットな作業場**を作成し、階層化（`active` や `archived`）を行わないこと。作業が完了したフラットなワークスペースはクリーンアップ（削除）可能とする。

## <progress_tracking>
- 【記憶喪失の防止】LLMはコンテキストウィンドウに限界があるため、タスクに着手する際、および完了・中断する際は、必ず自身が作業しているディレクトリ（ワークスペース等）内にある `progress.md` （または `task.md`）のチェックボックスを更新すること。
  - 常に「今どこまで終わっていて、次は何をするのか」を外部ファイルに書き出すことで、Agentが再起動しても一瞬で現在地に復帰できるようにせよ。
</progress_tracking>

## <continuous_documentation>
- 【陳腐化の防止】タスク完了時（Harvest Report作成時）は、必ず今回変更した実装と「アーキテクチャ図群」「各リポジトリのREADME/INDEX」に乖離がないかをクロスチェックし、差分があれば自動同期・修正してからセッションを終了すること。
</continuous_documentation>
</execution_flow>

## <governance>
- 「メーカー（実装）」と「チェッカー（検証）」の分離体制を基本とする。
- 破壊的変更を伴うタスクは親エージェント（または人間）が直接操作し、ファイル生成等のタスクはサブエージェント（Implementer等）に委譲すること。
- **[Local Rule Override]**: 他リポジトリ（`second-brain`や`core-service`等）を操作する際は、必ずそのリポジトリ直下の `AGENT.md` をロードし、**当該リポジトリ内においてはそのローカルルールを最優先（agent-coreのルールをオーバーライド）して適用**すること。
- **[Dependency Injection]**: `core-service`（ステートレス工場）を実行する際は、必ず `agent-core/config/` から設定を読み込み、`agent-core/factories/` 配下で Service-Config パターンに従って依存性を組み立て（DI）してから実行すること。
- **[Execution]**: 実行スクリプトは用途に応じて `jobs/` または `tools/` に配置すること。
- **[_index.md の配置例外ルール]**: サブディレクトリ作成時は自己記述の `_index.md` を作成するが、フラットなデータプール領域（Leaf: 例 `Permanent_Notes` 等）には作成を禁止する。構造の分岐点（Node）にのみ配置せよ。
</governance>
