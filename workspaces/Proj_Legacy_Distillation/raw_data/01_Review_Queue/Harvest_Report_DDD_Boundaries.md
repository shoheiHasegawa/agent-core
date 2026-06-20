# 🌾 Harvest Report: Agent アーキテクチャと DDD (Data vs Mechanism) の境界定義

**Date**: 2026-06-06
**Context**: COOモジュールの `DailySchedule` および `TaskPool` 設計フェーズにおける、システムの責務配置に関する深い対話からの抽出。

## 💡 抽出された教訓 (Wisdom & Insights)

### 1. 「知識（Data/Policy）」と「計算機構（Mechanism）」の完全分離
- **課題**: `life-automation`（Python）にスケジュール計算を任せる際、ユーザー個人の習慣やルール（例：第3金曜日はBOLDAY）といった「ドメイン知識」がシステム側にハードコードされ、密結合（知識の流出）に陥るリスクがあった。
- **解決策 (DDDの真髄)**:
  - **`second-brain` (Knowledge)**: 「自分が具体的に何をいつやっているか（What）」という事実と方針のみを管理するSSOT。
  - **`life-automation` (Mechanism)**: 「渡された抽象的な条件（RecurrenceRule）や時間枠（TimeBlock）を計算し、パズルを解く」という機能（How）のみを提供する計算エンジンに徹する。
  - これにより、ユーザーのライフスタイルが変わっても、修正するのは `second-brain` のデータのみとなり、システムのコードは不変に保たれる。

### 2. Agentをオーケストレーターとする「究極の疎結合化」
- **課題**: `life-automation` が直接 `second-brain` のMarkdownを読み書きすると、インフラ依存が発生しClean Architectureが破綻する。
- **解決策**:
  - `second-brain` のデータを読み取り、`life-automation` の機能（Service）を呼び出して計算させ、結果をカレンダーやObsidianへ書き戻す「糊（Glue）」の役割を **Agent自身（Skill）** が担う。
  - `life-automation` は「純粋なデータを受け取り、純粋なデータを返す」だけの独立したAPI/CLIツール（Agentの武器）へと昇華される。

## 🛠️ アーキテクチャ決定事項 (ADR Update Needed)

- **`second-brain` の責務**: マスタデータ・方針の永続化
- **`life-automation` の責務**: 汎用的なスケジュール・時間枠計算ロジック（ドメイン層）と、Google Calendar等外部APIへの通信代行（インフラ層）
- **Agent の責務**: 上記2つを繋ぎ合わせ、自然言語や状況判断を交えて自動化を完遂する脳。

## 📝 Next Actions
- [ ] 本レポートの内容（Data vs Mechanismの境界）を `01_System_Architecture.md` などのアーキテクチャドキュメントへ正式なADRとして追記する。
- [ ] 今後 `life-automation` 側でドメインを実装する際は、「このコードにユーザー固有の単語（知識）が混ざっていないか？」を常にコードレビューの基準とする。
