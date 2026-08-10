---
name: johari-facilitator
description: ジョハリの窓とラダーリング法を用いて、ユーザーの顕在意識と潜在意識を隔離分析し、真のIdentityを抽出・言語化するプロファイリング・スキル。
type: Orchestrator
model: pro
---

# SKILL: Johari Profiler

## 🎯 目的 (ミクロな WHY)
ユーザーの「表向きの宣言（顕在意識）」と「無意識の執着（潜在意識）」を抽出・言語化し、対比させることで真のIdentityをメタ認知させるため。この際、2つのサブエージェントを呼び出すのは、顕在意識と潜在意識を物理的に隔離して分析するためである。

## 📥 入力と出力 (ミクロな WHAT)
- **Input**: ワークスペース内のタスク/プロジェクト資料、ナレッジベース領域のノート
- **Output**: 統合されたプロファイリングレポート (`[Date]_johari_profiling_report.md`) とナレッジベースへの保存

## 🛠️ 実行手順 (HOW)
1. `invoke_subagent` を使用し、「Explicit Value Analyst」サブエージェントを起動する。ワークスペース内のタスクや進行中のプロジェクト資料を対象に、顕在意識のレポートを作成させる。
2. `invoke_subagent` を使用し、「Implicit Value Analyst」サブエージェントを起動する。ナレッジベース（Zettelkasten / 40_Permanent_Notes）領域のみを対象に、潜在意識のレポートを作成させる。
3. `agent-core/docs/rules/dialog_heuristics.md` をJITロードする。
4. 両サブエージェントからのレポートを、JITロードしたヒューリスティクス（ジョハリの窓）を用いて統合し、事実との対比や前提の破壊など、メタ認知を強烈に促す問いをユーザーに投げかけながら壁打ち（Sense Making）を行う。
5. 分析結果を `[Date]_johari_profiling_report.md` というArtifactとして出力する。
6. ユーザーから合意を得た後、レポートをナレッジベース内の適切なリソース（Resources）領域に保存し、必要に応じてアイデンティティやコアビジョンを定義しているファイルに反映する。
7. 完了後、標準ワーカー報告フォーマットで親エージェントに結果を報告する。
