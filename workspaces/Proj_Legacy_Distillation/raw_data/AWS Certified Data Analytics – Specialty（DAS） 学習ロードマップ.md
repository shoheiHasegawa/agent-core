# AWS Certified Data Analytics – Specialty（DAS） 学習ロードマップ

---

## 🎯 資格の目的と価値

| 項目 | 内容 |
|------|------|
| 対象資格 | AWS Certified Data Analytics – Specialty（DAS-C01） |
| 専門領域 | データ統合、ETL、DWH、BI分析基盤、データレイク設計 |
| 関連キャリア | データエンジニア / 分析基盤エンジニア / BIエンジニア |
| 活かせるあなたの強み | DBスペシャリスト・SQL Silver → Athena/Redshiftで大きな強み |
| 試験の傾向 | データ設計とサービス選定が中心、理論よりアーキテクチャ重視 |
| 位置付け | MLSと並ぶ最難関 AWS Specialty資格 |

---

## 🗂 学習ステップ全体像

| ステップ | 学習内容 | 期間目安 | 主教材 |
|----------|----------|----------|--------|
| Step 1 | AWSデータ分析の主要サービス理解 | 2週間 | 書籍・BlackBelt |
| Step 2 | ETL設計・データレイク・Glue/Athena実践 | 2週間 | Udemy / AWS Hands-on |
| Step 3 | DWH設計・Redshift・BI可視化 | 2週間 | Redshift実践 / QuickSight |
| Step 4 | 運用・セキュリティ・コスト最適化 | 1週間 | AWS Docs / Hands-on |
| Step 5 | 模擬試験・シナリオ分析訓練 | 2週間 | Udemy模試 / WhizLabs |
| 合計 | 約8〜9週間 |  |

---

## 📚 有効な書籍（試験・実務対応）

| 優先度 | 書籍名 | 特徴 |
|--------|--------|------|
| ★★★ | AWSデータ分析入門（技術評論社） | Glue/Athena/Redshift中心、試験範囲を網羅 |
| ★★★ | いちばんやさしいAWSデータ分析の教本 | 用語・基礎サービス理解に最適 |
| ★★★ | 実践データ基盤構築 AWSで学ぶETL/可視化/分析 | 実務で即使える構成例 |
| ★★☆ | AWS Certified Data Analytics Study Guide | 英語。試験向け構成で整理されている |
| ★★☆ | コスト最適化 & セキュリティ本各種 | 後半のアーキテクチャ対策用 |

---

## 💻 Udemy講座（実務＆試験対策に強い）

| 講座名 | 学習内容 | 試験との関連 |
|--------|----------|--------------|
| AWS Certified Data Analytics Specialty 2024 | 全サービス・模試・図解 | ★★★★★ |
| AWS Glue & Athena 実践データ分析講座 | ETL・分析基盤構築 | ★★★★ |
| Redshift / QuickSight データ基盤構築講座 | DWH・BI分析 | ★★★★ |
| AWS Lake Formation & ETL構築実践 | データレイク設計 | ★★★ |
| Tutorial Dojo（模試） | 試験の問題形式対策 | ★★★★★ |

---

## 🗓 学習スケジュールモデル（9週間）

| 週数 | 学習テーマ | 主教材 |
|------|------------|--------|
| 1 | AWS分析サービス概要（Athena, Glue, Redshift, Kinesis） | BlackBelt / 書籍 |
| 2 | Glue ETL / Crawler / Data Catalog実践 | Udemy |
| 3 | Athena構文・最適化・SQLとBig Data処理 | Udemy / Hands-on |
| 4 | Data Lake設計（S3, LakeFormation） | AWS Docs / 実践 |
| 5 | Redshift DWH構築と分散設計 | Udemy / Reinvent動画 |
| 6 | QuickSightによるBIダッシュボード設計 | Udemy |
| 7 | セキュリティ・コスト・運用・監視 | 書籍 / AWS公式 |
| 8〜9 | 模擬試験・弱点克服・再演習 | WhizLabs / Udemy模試 |

---

## 📊 試験で頻出のサービスと出題比率

| 分野 | 比率 | 対象サービス |
|------|------|--------------|
| データ収集 | 18% | Kinesis, DMS, Firehose |
| データ保存 | 22% | S3, Glue, LakeFormation, Redshift |
| データ処理 | 24% | Glue, EMR, Athena, Lambda |
| 分析・可視化 | 18% | Athena, QuickSight, Redshift |
| セキュリティ運用 | 18% | IAM, KMS, CloudTrail |

---

## 🤖 AI活用方法（効率学習のポイント）

| 学習目的 | AIにする質問例 |
|----------|----------------|
| サービス比較 | 「AthenaとRedshiftの違いを、利用ケース別に表でまとめて」 |
| アーキ設計 | 「S3とGlueとAthenaを使ったデータレイク構成図をMermaidで作って」 |
| 模擬試験 | 「DASの模擬問題を4問作成して、難易度高めでお願い」 |
| コスト最適化 | 「Redshiftのコスト削減方法を、運用観点で箇条書きにして」 |
| ベストプラクティス | 「DASで頻出するWell-Architectedの観点を整理して」 |

---

## 🎯 合格戦略

| 項目 | 内容 |
|------|------|
| 合格ライン | 約75％（65問中49問） |
| 問題傾向 | 長文シナリオ型（サービス選択問題） |
| 難易度 | ★★★★☆（MLSと同等） |
| 時間配分 | 180分 ／ AWS試験では最も長い |
| 勝ち筋 | SQL経験 × 分析基盤構築経験を最大限活かす |

---

## 🔗 MLSとの違い（比較表）

| 領域 | MLS | DAS |
|------|-----|-----|
| 中心領域 | モデリング / MLOps | ETL / DWH / BI分析基盤 |
| 使用サービス | SageMaker中心 | Glue / Athena / Redshift |
| 試験比率 | 機械学習・評価が高 | アーキ設計・実装が高 |
| 難易度 | ★★★★★ | ★★★★☆ |
| あなたとの親和性 | Python経験◎ | SQL・DBスペシャリスト経験◎ |

---

## 🚀 次のステップ
- この後に学習するなら➡ **DEA（データエンジニア）** を繋げると学習効率◎  
- MLSと並行する場合➡ 理論はG検定で補強可能  
- Hands-on中心で進めたい？➡ SageMaker＋Glue連携実践もサポート可能  

---

