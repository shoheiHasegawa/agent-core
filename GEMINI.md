# 🌍 Global Constitution: GEMINI.md

ここは You_Inc システムの最上位ルート環境である。
Agentは以下の境界と絶対安全ルールを厳守し、適切なリポジトリへルーティングせよ。

## <global_rules_and_safety>
1. 【言語】思考・応答など全アウトプットにおいて日本語（Japanese）を徹底せよ。
2. 【Git安全装置】破壊的・大規模操作前は必ず事前に Commit し、復元可能にせよ。
3. 【Shell安全装置】シェル実行時は `set -e` や `&&` を用い、エラー時即時停止させよ。
4. 【Leave No Trace】一時ファイルは `.gitignore` された `scratch/` 等で使用し自律破棄せよ。
5. 【Harvest Report】セッション終了時、運用改善案やActionableな報告は `agent-core/queue/harvest_reviews/` へ出力せよ。普遍的な教訓（Wisdom）の原石は `second-brain/90_Meta/Templates/Sense_Making_Template.md` を用いて `second-brain/20_Sense_Making/` へ蒸留せよ。
</global_rules_and_safety>

## <jit_routing>
- 👉 `agent-core/`: AIの司令塔・運用層。システム構成図やタスク（Epic）の指示はここの `AGENT.md` を見よ。
- 👉 `core-service/`: ステートレスな機能工場。実際の機能実装・コーディングはここのローカルルールに従って行え。
- 👉 `second-brain/`: ナレッジベース。知識や過去の記録が必要な場合はここを探せ。
</jit_routing>
