# Harvest Report: 知識の「Source & Compiled」アーキテクチャの確立

## セッション概要
*   **日時**: 2026-06-13
*   **スコープ**: `Proj_Playground_Reconstruction` における `30_Resources` と Zettelkasten の責務分離、および To-Be アーキテクチャの設計。

## 💡 得られた教訓 (Wisdom / Principles)
1.  **Source Code vs Compiled Binary メタファー**: Zettelkasten（フラットで無限に拡張する知識空間）とLLMのハルシネーション対策（コンテキストの絞り込み）という矛盾は、「ローカルをソースコード、NotebookLM用フォルダをコンパイル済みバイナリ」と見立てるビルドプロセスを挟むことで完全に解決できる。
2.  **物理構造とコンテキストの分離**: AI（Agent）にコンテキストを抽出させる場合、フォルダ階層による文脈の隠蔽はアンチパターンである。Zettelkasten領域（`50_Zettelkasten`）は「完全フラット」とし、文脈はYAMLタグ等のメタデータでのみ管理すべき。
3.  **独自コンテキストによるAIの武器化**: LLMの平均的・無難な回答を突破するには、「どこかの一般論」ではなく「自分自身の過去の失敗・一次情報」をZettelkastenに蓄積し、それを強制的に優先させるハーネス（安全帯）を構築することが最も強力な戦略となる。

## 🛠️ 技術的負債・課題 (Tech Debt / To-Do)
*   **移行作業**: 現在 `30_Resources` に同居している `Permanent`（Zettelkastenノート群）を抽出し、新設するトップレベルの `50_Zettelkasten` へ一括移行するスクリプトの実行が必要。
*   **ビルドパイプラインの実装**: `50_Zettelkasten` を解析してNotebookLM用のDriveへデプロイする「Zettelkasten Builder」のCI/CDスクリプト（Python等）の開発。
*   **Agentプロンプトの更新**: AntiGravity側のペルソナ（Architect, Trader等）に対し、専用のNotebookLMコンテキストを絶対視させるシステムプロンプトの作成。

## 🚀 次のステップへの示唆
「ResourcesとZettelkastenの分離」が完了したことで、アーキテクチャの「情報入力・加工レイヤー」の基盤が整った。次はPARAメソッドにおける「Area（責任領域）」の To-Be について、このフラット化・Agent駆動のパラダイムの中でどのような責務を持たせるべきかを再定義する。
