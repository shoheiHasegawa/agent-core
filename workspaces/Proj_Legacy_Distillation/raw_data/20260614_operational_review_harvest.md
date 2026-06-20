# Harvest Report: Agent-Core 運用フローの再レビュー

## 1. Context (背景)
`agent-core` および `core-service` のアーキテクチャ設計・運用フロー（`11_agent-core_operational_flow.md`, `30_core-service_architecture.md`）に関する更新の再レビューを実施。前回の懸念点（無限ループ、コンフリクト破壊、GC、Direct Push等）の解決状況を確認し、新たに発生しうる運用上のエッジケースを探索した。

## 2. Wisdom & Tech Debt (得られた教訓と技術的負債の発見)
- **AI同士の無限ループの盲点**: CIエラーにはサーキットブレーカー（3回上限）が設けられたが、「作業Agent」と「レビューAgent」間のレビュー指摘・修正ループに対する上限がなく、AI同士の無限対話に陥るリスクが発覚した。
- **Webhook起点の非同期処理における「直前」の難しさ**: GitHubのような非同期イベント駆動システムにおいて、人間がマージボタンを押す「直前」をAgentが割り込んでフックすることは難しい。「Mergeイベント検知後、Workspaceを消す前」にHarvest Reportを抽出するよう、物理的な実行順序を再定義する必要がある。
- **失敗からの学びの喪失**: PRがマージされた時だけでなく、PRがClose（破棄）されたり、定期バッチでWorkspaceが強制削除される際にも、未コミットのコードや失敗の履歴から「なぜ失敗したか」をHarvest Reportとして残さなければ、重要な知見が永久に失われる。

## 3. Recommended Actions (今後のアクション案)
- `11_agent-core_operational_flow.md` の更新:
  - レビューAgentと作業Agentの往復回数に上限（例: 3往復で人間の裁定にエスカレーション）を設定する。
  - Harvest Reportの抽出タイミングを「マージ直前」から「Merge/Close Webhook検知直後、かつTeardown実行前」に修正する。
  - PR Close/Cancel、および強制クリーンアップの際にもHarvest Report生成（およびWIPのコミット・退避）を必須プロトコルとして追記する。
