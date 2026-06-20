---
type: "HarvestReport"
status: "requires_review"
created: 2026-06-14T16:45:00
tags: ["#harvest", "#architecture", "#agent-centric"]
requires_human: true
---

# Harvest Report: Playground Reconstruction (アーキテクチャ大改修)

## 1. Context (背景)
「You, Inc.」のアーキテクチャをAgent-Centric（3層分離モデル：agent-core, second-brain, core-service）に移行するため、`10_Projects/Proj_Playground_Reconstruction/` 配下で長大な設計の再構築、矛盾の解消、およびディレクトリ構成の定義を行った。
本レポートは、一連のセッション（複数Agentによるクロスチェックを含む）で得られた「知恵」と「技術的負債」を永続化するものである。

## 2. Wisdom / Learnings (得られた教訓)

### A. 「決定事項(ADR)」と「To-Be」の分離の難しさと同期の重要性
過去の遺物（古い仕様書の丸投げ）がADRディレクトリに混入すると、Agentは容易にハルシネーションを起こす。
**教訓**: ADRは必ず「Context / Decision / Consequences」の純粋なフォーマットを強制すること。そして、To-Be設計図がアップデートされた際は、関連するADRの名称（例: 50_Zettelkasten -> 40_Permanent_Notes）も確実に逆同期するか、あるいはDeprecatedラベルを付与して「腐った知識」を隔離しなければならない。

### B. Agentと人間のコミュニケーションには「型（Template）」が必須
「このディレクトリで作業する」という静的なルールだけでは、Agentは自律駆動できない。
**教訓**: 人間からAgentへの指示書（`Agent_Task_Request_Template`）、破壊的変更前の承認願い（`Proposal_Approval_Template`）、失敗時の記録（`Decision_Log_Template`）など、動的な状態遷移を伴うフローには**必ずYAMLフロントマター付きのTemplateをSSOTとして定義**しなければならない。

### C. 「消す前の猶予（Grace Period）」という防衛機構
Agentがタスクを終えた直後にワークスペースを即時消去（Teardown）すると、「なぜ失敗したか」の貴重なログが虚空に消える。
**教訓**: 削除の前には必ず「Harvest抽出」と「`archived/` への一時退避」を挟み、人間の承認（Human-in-the-loop）を得てから完全消去するフローが不可欠である。

## 3. Tech Debt / Next Actions (技術的負債と次やるべきこと)

1. **テンプレートファイルの実体作成**
   - 設計書（`to-be/10` や `to-be/20`）に「必要なテンプレート」のリストとYAML要件は定義したが、**それらの `.md` ファイルの実体はまだ作られていない**。
   - **Next Action**: Boilerplate Agent（初期構築Agent）を起動し、定義されたテンプレートの実体を `90_Meta/Templates/` および `agent-core/templates/` に自動生成させる。
2. **Mobile Vault（iCloud）との同期パイプラインの実装**
   - アーキテクチャ図に `Mobile Vault` を分離したが、実際にiCloud上のディレクトリを監視して `00_Inbox` に取り込む「清書Agent（InboxTriageAgent）」の実装スクリプトが必要。
3. **`core-service` のDocker/DI環境の構築**
   - 設計は完了したが、物理的な `core-service`（実行可能な道具箱）および `agent-core` での隔離環境（git worktree / Dockerマウント）を立ち上げるコード基盤が未着手。

## 4. 結び
アーキテクチャの「設計上の摩擦」は完全にゼロになった。
ここからはいよいよ「設計図」を「実体（コード・ディレクトリ）」に落とし込む実装フェーズへと移行する。
