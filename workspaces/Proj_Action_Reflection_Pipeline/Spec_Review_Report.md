# 厳格仕様レビューレポート (compliance-reviewer)

対象ファイル:
- `/Users/shoheihasegawa/you_inc/core-service/src/application/action_pipeline/spec.md`
- `/Users/shoheihasegawa/you_inc/agent-core/workspaces/Proj_Action_Reflection_Pipeline/03_Advanced_Scheduling_Algorithms.md`

## 1. 概要
指定された `spec.md` と `03_Advanced_Scheduling_Algorithms.md` を比較・検証しました。
ドキュメントには全体で **4セクション・計12個のルール** が定義されていますが、現在定義されている `[SCENARIO-01] ~ [SCENARIO-04]` では全体のうち **5ルールしか網羅されておらず、残り7ルールのエッジケース・異常系の検証シナリオが完全に欠落しています。**

## 2. 追加・修正すべきテスト可能シナリオの提案
- **[SCENARIO-05] 異常系: コンテキストスイッチの超過（1-B対応）**
- **[SCENARIO-06] 異常系: 未Readyタスクの自動不可視化（1-C対応）**
- **[SCENARIO-07] 正常系/エッジケース: 戦略的投資枠（第2象限）の強制ブロック（2-B対応）**
- **[SCENARIO-08] 異常系: 孤立タスク（Orphan Task）の排除（2-C対応）**
- **[SCENARIO-09] 異常系: ディープワーク連続稼働リミット到達（3-B対応）**
- **[SCENARIO-10] 正常系: サーカディアン・ディップの自動処理（4-B対応）**
- **[SCENARIO-11] 正常系: シャットダウン・リチュアルの固定配置（4-C対応）**
- **[SCENARIO-12] 異常系: 午前中の浅い作業ブロックエラー（4-A対応）**
- **[SCENARIO-01] の修正要求**: 事後条件に「最低1時間の `[W]` ブロックが配置されること」を明記。
