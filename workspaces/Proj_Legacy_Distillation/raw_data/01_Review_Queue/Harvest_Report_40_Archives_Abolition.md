# Harvest Report: 40_Archives の廃止と "Distill or Delete" パラダイム

## 1. 概要 (Context)
* **Target Project**: Proj_Playground_Reconstruction
* **Session Goal**: Agent-Centricアーキテクチャにおける `40_Archives`（過去の遺物）の責務とライフサイクルの再定義。
* **Key Outcome**: `40_Archives` の完全廃止と、すべての完了データを「Zettelkastenへの蒸留」か「完全削除」の二択に強制するパラダイムシフトの合意。

## 2. 獲得した教訓・知識 (Wisdom for Zettelkasten)
* **[Anti-Pattern] The "Just in case" Archive**:
  「後で使うかもしれない」という心理的安全性のために用意されたArchiveは、AgentにとってはRAG検索時の深刻なノイズ（Context Pollution）となる。エージェントシステムにおいて「中途半端な生データ」は有害である。
* **[Principle] Distill or Delete (蒸留か、さもなくば削除か)**:
  システムには現在進行形のデータ（Workspace/OS）と、普遍的な知識（Zettelkasten）、最新のルール（Areas）のみが存在すべきである。プロジェクトが完了した際は、必ず失敗の歴史や教訓を「アンチパターン（Permanent Note）」として抽出し、それ以外の残骸は潔く消去（rm -rf）しなければならない。

## 3. 解消された技術的負債 (Tech Debt Resolved)
* `second-brain` と `play_ground` の境界を跨いでプロジェクトの残骸が残留してしまう構造的な矛盾を根本から排除した。
* 「古いルールの参照によるAgentのハルシネーション」の最大の温床をアーキテクチャレベルで塞いだ。

## 4. 次のアクションとシステム改善案 (Next Actions)
1. **[Migration]** 新リポジトリへの移行時、既存の `40_Archives`（Decisions等）を自動走査し、Zettelkastenへ教訓を抽出するマイグレーションスクリプト/SOPの作成。
2. **[Skill Development]** Agentがプロジェクトを終了する際に起動する `project-closer`（Harvest抽出＆自動削除機能）の実装。
3. **[Next Session]** 次回セッションにて、`99_System` のアーキテクチャ再定義に着手する。
