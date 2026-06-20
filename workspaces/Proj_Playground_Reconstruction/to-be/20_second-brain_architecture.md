# 20_second-brain アーキテクチャ設計書

## 1. 概要と責務
`second-brain` は、社長（人間）の思考や生き方を指針としつつ、Agentたちと共に育てていく「知識体系（企業内図書館）」である。
プログラムの実行状態やタスクの進行ログは一切含まず、純粋な情報・知識（テキストデータ）のみを永続化する。

## 2. ディレクトリ構成（Permanent Notes空間）
リポジトリ全体が、Permanent Notes（知識のネットワーク）として機能するフラットな構造を持つ。

```text
second-brain/
├── README.md               # [人間向け・ルーター] リポジトリの目的と全体像
├── GEMINI.md               # [AI向け・起点] 絶対ルールと各ディレクトリへのポインタ
├── INDEX.md                # [オンデマンド] 詳細なディレクトリマップ（地図）
├── 00_Inbox/               # Agentによって一次フォーマット(YAML等)が済んだSeed情報の待機キュー
├── 10_Areas/               # 会社のルール・戦略・指針 (各部門AgentのビジネスロジックSSOT)
├── 20_Sense_Making/        # 蒸留待ちのインキュベーション領域（WIP制限トリガー）
├── 30_Resources/           # 外部資料、参照用の元データ
├── 40_Permanent_Notes/     # 普遍的な知識・教訓群 (純粋なPermanent Notes)
└── 90_Meta/                # [RAG Exclusion Boundary] 非セマンティックデータの隔離領域
    ├── System_Rules/       # [機械的マニュアル] YAMLの書き方、PR基準などのシステム制約
    ├── Templates/          # 各種Markdownのテンプレート群
    └── Attachments/        # 画像やPDF等の孤立しがちな添付ファイル群
```
※上記以外のファイルも原則としてルート直下などにフラットに配置され、相互にリンクし合うネットワークの一部となる。

## 3. コア機能とルール

### 3.1 ルーティングとJITロード
1. **ルーティング（常時ロード）**: Agentがタスクを開始する際、必ずルートの `GEMINI.md` と `README.md` を読み込む。ここには「どの情報を探すにはどこへ行くべきか」のポインタだけが記述されている（FAT化防止）。
2. **ルールの抽象度分離とJITロード**: `GEMINI.md` のポインタに従い、**知的なビジネス制約は `10_Areas/`** から、YAMLの書き方やPR基準などの**機械的な運用マニュアルは `90_Meta/System_Rules/`** から、それぞれタスクに必要なもの**だけ**をピンポイントで遅延ロード（JIT）する。巨大な一枚岩のルールを読ませることは禁止する。

### 3.2 適応型PRガバナンス（Direct Pushの許可）
ナレッジの追加や修正は頻度が非常に高く、全てにPull Request（PR）を必須とすると運用負荷が破綻する。
そのため、`second-brain` においては以下のガバナンスルールを適用する。
- **Agentの直接Push（Direct Commit）を許可する。**
- ただし、CI（継続的インテグレーション）による **品質ゲート** を設ける。
- CIでは「Markdownフォーマットの妥当性（YAMLフロントマター等）」「内部リンク切れの有無」のみを機械的にチェックし、違反があれば即座にリジェクトする。

### 3.3 コンテキスト・エンジニアリング
Agentが迷子にならないよう、ルートディレクトリの `INDEX.md` を起点として、各フォルダの役割やタグの命名規則を定義した `CONTRIBUTING.md` または `RULES.md` を配置し、Agentに遵守させる。

### 3.4 テンプレートと共通YAMLフロントマターの強制
AgentがMarkdownファイルを確実かつ高速に処理（検索・フィルタ・遷移）できるよう、`second-brain` 内の**すべてのテンプレートに共通のYAMLスキーマを必須**とする。

**【必須YAMLスキーマ】**
```yaml
---
type: "PermanentNote | Resource | AreaRule | TaskRequest | Dashboard"
status: "raw | draft | active | archived | requires_review"
created: YYYY-MM-DDTHH:mm:ss
updated: YYYY-MM-DDTHH:mm:ss
tags: ["#tag1", "#tag2"]
requires_human: true/false  # 人間の承認・確認が必要かを示すフェールセーフフラグ
---
```

**【90_Meta/Templates/ に配置する必須テンプレート群】**
1. `Area_Governance_Template.md`: 部門の責務、基本ルール（WIP制限等）。
2. `Permanent_Note_Template.md`: 1Note=1Ideaの本文、関連リンク、ソース。
3. `Resource_Template.md`: 情報源URL、要約、信頼性スコア。
4. `Inbox_Raw_Template.md`: 生データ（清書AgentがYAMLを付与するためのベース）。
5. `Agent_Task_Request_Template.md`: 人間からAgentへの明確な指示書。
6. `Project_Charter_Template.md`: プロジェクトのゴールやスコープの定義。
7. `Dashboard_Briefing_Template.md`: Agentが毎朝生成し、Mobile Vaultへ出力する日報・予定表。
