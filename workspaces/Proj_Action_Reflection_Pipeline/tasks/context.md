# Context

## 現在地 (Current Status)
- Phase 1.5（情報の棚卸し）およびPhase 2（Task Registryへの流し込み）が完了。
- ワークスペースの統廃合（`Personal_Finance`, `Harness_Construction`のInboxへの退避、`Systematic_Trading`の統合）およびルール明文化が完了。

## 次回の論点 (Next Focus)
- **逆方向の実績回収（Reverse Recovery Flow）の詳細仕様決定と実装**
  - Dashboard（`Briefing.md`）のチェックボックス実績をパースしてTask Registryを更新するフローの実装。
  - 実装前に以下の3点についてユーザーと壁打ちを行うこと：
    1. MarkdownとJSONの紐付け方法（IDマッピング：不可視コメント、リンク、完全一致など）
    2. 定期タスク（ルーティン）完了時の挙動（クローン生成など）
    3. 実績回収パーサーの起動タイミング（深夜バッチ vs ジャーナリング直前フック）
