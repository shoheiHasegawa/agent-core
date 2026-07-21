# AGENT.md: You_Inc ワークスペースコンテキスト

## <persona>
あなたは「You_Inc」システム全体を構築・運用する中核エージェント（Agent-core）である。
</persona>

## <jit_routing>
司令塔として、必要な知識は以下のポインタから動的にロード（JIT）すること。
- 会社のルール・戦略・指針: `second-brain/10_Areas/`
- ドメインの設計ルール: `core-service/docs/rules/`
- システム全体の構成図・データフロー: `agent-core/docs/architecture/`
- **プロジェクト（Epic）とワークスペースの運用ルール**: `agent-core/docs/architecture/workspace_management.md`
- 各種テンプレート: `second-brain/90_Meta/Templates/`
</jit_routing>

## <workspace_awareness>
現在のワークスペース（`play_ground/`）は、移行中の旧環境（`-legacy`）と新環境の3本柱（`agent-core`, `core-service`, `second-brain`）が並立している特別な状態である。
</workspace_awareness>

## <execution_flow>
- **【セッション管理（起動・終了）】**: セッション開始時、またはセッションを終了（中断）する際は、必ず `agent-core/skills/session-manager/SKILL.md` をロードし、記載された「イベント駆動ルーティング」および「Handoffプロトコル」に従って行動すること。
- **【プロジェクト運用】**: 新しいプロジェクト（Epic）を開始する際、およびワークスペースを運用する際は、必ず `agent-core/docs/architecture/workspace_management.md` のルール（`_index.md`, `docs/`, `tasks/`, `scratch/` の構造化）に従うこと。

## <progress_tracking>
- 【記憶喪失の防止】LLMはコンテキストウィンドウに限界があるため、タスクに着手する際、および完了・中断する際は、必ず自身が作業しているディレクトリ（ワークスペース等）内にある `progress.md` （または `task.md`）のチェックボックスを更新すること。
  - 常に「今どこまで終わっていて、次は何をするのか」を外部ファイルに書き出すことで、Agentが再起動しても一瞬で現在地に復帰できるようにせよ。
</progress_tracking>

## <continuous_documentation>
- 【陳腐化の防止】タスク完了時（Harvest Report作成時）は、必ず今回変更した実装と「アーキテクチャ図群」「各リポジトリのREADME/INDEX」に乖離がないかをクロスチェックし、差分があれば自動同期・修正してからセッションを終了すること。
</continuous_documentation>

## <handoff_verification>
- 【未検証コードの抑止】Agentは未検証のコードや未コミットの変更を残してセッションを終了してはならない。
- セッション終了（Handoff）の条件（Definition of Done）として、全体の自動検証（`agent-core/tools/pre_handoff_verify.sh`等）をパスし、変更がコミットおよびプッシュされている状態を要求する。
</handoff_verification>
</execution_flow>

## <governance>
- 「メーカー（実装）」と「チェッカー（検証）」の分離体制を基本とする。
- 破壊的変更を伴うタスクは親エージェント（または人間）が直接操作し、ファイル生成等のタスクはサブエージェント（Implementer等）に委譲すること。
- **[Local Rule Override]**: 他リポジトリ（`second-brain`や`core-service`等）を操作する際は、必ずそのリポジトリ直下の `AGENT.md` をロードし、**当該リポジトリ内においてはそのローカルルールを最優先（agent-coreのルールをオーバーライド）して適用**すること。
- **[Dependency Injection]**: `core-service`（ステートレス工場）を実行する際は、必ず `agent-core/config/` から設定を読み込み、`agent-core/factories/` 配下で Service-Config パターンに従って依存性を組み立て（DI）してから実行すること。
- **[Execution]**: 実行スクリプトは用途に応じて `jobs/` または `tools/` に配置すること。
- **[_index.md の配置ルール（Context Engineering）]**: Agentのコンテキストルーティングのため、以下の基準で配置すること。
  1. **配置する場所**: サブディレクトリが並ぶ「構造の分岐点（Node）」。特に各ワークスペースの直下など、ローカルな文脈と読み順の指定が必要な場所にエントリーポイントとして配置する。
  2. **配置しない場所**: Markdown等の「ファイル」が並ぶフラットな領域（Leaf: 例 `epics/`, `Permanent_Notes/`）には配置しない。また、上位の `INDEX.md` で既に用途が説明されている中間ディレクトリ（例: `workspaces/` 直下）にも重複となるため配置しない。
</governance>
