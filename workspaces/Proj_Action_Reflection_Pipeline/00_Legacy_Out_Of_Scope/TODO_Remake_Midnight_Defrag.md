# [TECH DEBT] Remake Midnight Defrag (CIO Socratic Reporting)

## 概要
以前 `life-automation/src/application/knowledge/midnight_defrag` に存在した自動整理機能を、アーキテクチャのクリーンアップに伴い一旦削除しました。
この機能は非常に有益な思想（Zettelkastenの自動メンテナンスとソクラテス式AIコーチング）を持っているため、将来のフェーズで再構築（リメイク）します。

## 元の機能が持っていた思想と機能
1. **ベクトルDB（ChromaDB）連携による重複検知**:
   - 毎日深夜にZettelkasten（Permanent Notes）をスキャン。
   - ChromaDBにUpsertし、類似度（Distance）が近いノートのペアを抽出。
   - グラフ（リンク構造）をチェックし、直接リンクされていない「隠れた類似ノート（重複の疑い）」のみをフィルタリング。
2. **Geminiによる診断とコーチング（Socratic Question）**:
   - 類似ノートのペアをGeminiに渡し、「本当に重複しているか？」「どう統合すべきか？」を推論させる。
   - 孤立したノート（Orphan Notes）を見つけ出し、「これはどの知識と接続できるか？」を問う。
   - これらの結果をまとめ、CIO Agentからの「Socratic Report（問答形式のコーチングレポート）」としてファイル出力する。

## リメイク時の要件（Next Actions）
- [ ] 完全にSOLID原則とDIP（依存性逆転の原則）に従うこと。
- [ ] インフラ（GeminiClientやChromaDBRepository）を直接インポートせず、Domain/Application層で定義した Port（Protocol）を経由させること。
- [ ] 出力されたレポートが確実に人間の目に入り、トリアージされる仕組み（Agent OS Inbox パイプラインへの統合）を確立すること。

## 参考
- 削除前のコード: `life-automation/src/application/knowledge/midnight_defrag/midnight_defrag_use_case.py` (Gitの履歴を参照)
