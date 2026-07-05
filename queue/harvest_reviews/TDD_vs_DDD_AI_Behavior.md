# Harvest Report: TDDとDDDの乖離とAIの挙動特性

## 事象の概要
Epic 03の開発において、TDD（テスト駆動開発）のプロトコルを敷いていたにも関わらず、最終チェックで「ドメインモデル貧血症（Anemic Domain Model）」や「Application層へのロジック漏出」という重大なアーキテクチャ違反が発覚した。

## 原因分析（なぜTDDで防げなかったのか？）

1. **TDDは「振る舞い（Behavior）」を保証するが「構造（Structure）」は保証しない**
   - TDDの第一目的は「テストをパスさせること（Green）」である。
   - LLM（AIエージェント）に「このテストをパスさせよ」と指示した場合、最もコンテキスト消費が少なく手っ取り早い手段として、**「Application Serviceの中にすべての `if/for` ロジックをベタ書きする」**というアプローチを取りがちである。

2. **「Refactor（リファクタリング）」フェーズのシステム的欠落**
   - TDD本来のサイクルは「Red ➔ Green ➔ **Refactor**」であるが、我々の定義した `testing_strategy.md` では、Greenになった時点でImplementerの役割が終了し、Refactorを自発的に行う動機付けが欠落していた。
   - その結果、リファクタリング（DDDの適用）が、事後検閲である Reviewer Agent に丸投げされる開発フローとなっていた。

3. **抽象化と依存性逆転（DIP）への認識の甘さ**
   - Implementer Agentは具体的な実装（iPhone出力、Calendar同期）を急ぐあまり、Port and Adapters パターンにおける「抽象への依存」を軽視した。

## 運用改善案 (Actionable Items)

1. **AI Pair Programming Protocol の改修 (`testing_strategy.md`)**
   - 現状の `[Tester] ➔ [Implementer] ➔ [Reviewer]` という直線的なフローを改め、Implementerのプロンプト内に **「Green（テスト通過）後、必ず自身でDDDとSOLIDの観点からリファクタリングを行ってからコミットすること」** という指示を強制する。
2. **Domain Service 先行実装ルールの追加**
   - Application層を書く前に、必ず「ビジネスロジックだけをカプセル化した Domain Service / Policy クラスから先に実装する」という制約を設ける。
