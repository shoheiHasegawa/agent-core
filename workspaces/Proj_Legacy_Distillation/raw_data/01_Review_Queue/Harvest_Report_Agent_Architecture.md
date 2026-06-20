# Harvest Report: Agent-Centric Architecture Evolution
**Date**: 2026-06-14
**Context**: Proj_Playground_Reconstruction における未決事項（Open Items）の解消とアーキテクチャ詳細化セッション

## 1. 得られた教訓 (Wisdom & Insights)
- **Over-engineeringの回避**: AgentによるWIP制限やフォルダ生成を「システムコマンド」でガチガチに縛るより、**「ルール化（手動でフォルダを作らない）」と「View層（Obsidian Dataview）での可視化」**に倒す方が、システム全体が圧倒的にシンプルになり、SOLIDのOCP（開放閉鎖の原則）を満たす。
- **Obsidianの「View層」としての明確化**: これまで曖昧だったObsidianの位置づけを「フロントエンド（UI）」として再定義し、その設定ファイルをすべて `90_Meta` に内包することで、純粋なデータ（Markdown）とシステム（View）の分離に成功した。
- **Agent間通信とI/Oのイベント駆動化**: APIを使った同期通信や直接のパス操作はコンフリクト（特にiCloud環境）を生む。DI（依存性注入）と非同期キュー（`mv`コマンドによるアトミックな移動ロック）を組み合わせることで、完全な疎結合と排他制御が実現できる。

## 2. アーキテクチャの進化 (Architectural Evolutions)
今回のセッションにより、以下のドキュメントと概念が新たに追加・更新された。
- **[更新]** `to-be/00_overall_architecture.md`: Obsidianを第4のコンポーネント（View層）として図式化。
- **[追加]** `to-be/50_obsidian_view_architecture.md`: ObsidianのUIとしての責務と、`90_Meta`への設定集約。
- **[追加]** `to-be/99_cicd_pipeline_architecture.md`: 各リポジトリ（second-brain, agent-core, core-service, mobile-vault）の責務に合わせたPre-commitとActionsのCI/CDパイプライン設計。
- **[追加]** `to-be/13_event_driven_batch_architecture.md`: DIを用いたInbox回収バッチとコンフリクト保護。
- **[追加]** `ADR 0018 ~ 0020`: 上記設計パラダイムの決定根拠（ラショナール）。

## 3. 技術的負債と今後のアクション (Tech Debt & Next Steps)
- **Day 1 フォールバックの運用検証**: CI失敗時の「人間へのフォールバック（Error Inbox起票）」が実際に回るか、WebhookやGitHub Actionsの実装フェーズで検証が必要。
- **移行スクリプト（Migration Agent）の開発**: 旧アーキテクチャのYAMLフォーマットの一括変換と、リンク切れレポート（broken links）を出力する使い捨てスクリプトの実装。
- **CI/CDパイプラインの実装**: 策定された設計に基づき、実際に各リポジトリに `.github/workflows/` および `.pre-commit-config.yaml` を実装するタスク。

## 4. 最終フェーズでの追加決定とSRE的教訓 (Session End Update)
- **UI/WIP制約の最終決定**: ダッシュボードはObsidianの `Dataview` プラグインで十分担保可能（Over-engineering回避）。WIP制約は `agent-core` 側で作業用ディレクトリを作成する機構（`make workspace` 等）でシステム的にブロックすることで解決。
- **SRE視点でのシステムの穴とその対策（超重要）**:
  - **Direct Pushの罠**: GitHub ActionsはPush事後でしか走らないため、CIで弾いても `main` 汚染は防げない。必ず「PR必須＋Auto-Merge」でクリーンな状態を担保すること。
  - **クロスファイルシステム間の非アトミック性**: iCloudからローカルへの `mv` は内部で `cp+rm` となるため、移動中に落ちると二重処理になる。移動時にTask_IDを付与する等の冪等性担保が必須。
  - **Poison Pill（無限クラッシュ）**: Agentを確定で落とすエラーファイルが来た場合、セルフヒーリングが無限ループになる。リトライ回数をカウントし、Dead Letter Queue (DLQ) へ隔離する安全弁が必要。
  - **承認待ちのデッドロック**: 社長が承認（PRマージ）を放置するとWIPが上限に達しシステムがフリーズする。WIPカウントから「社長承認待ちタスク」は除外するルールが必要。
