# Harvest Report: 20_Areas as Governance Engine

## 1. 概要 (Context)
Agent-Centric アーキテクチャの再構築セッションにおいて、PARAメソッドの「Area」をどのように再定義し、機能させるかについての設計とドキュメント詳細化を行った。
動的な「Projects」と普遍的な「Zettelkasten」が分離された中で、`20_Areas` が果たす役割は「組織（You, Inc.）のガバナンスと、Agentのペルソナ定義（宣言的制約）」であることが明確になった。

## 2. 得られた教訓 (Wisdom)
* **ドメイン層とアプリケーション層の分離 (DDD)**: 
  `20_Areas` はビジネスルール（制約・方針）を管理するドメイン層であり、ここには実行の手順（SOPやスクリプト）を含めてはならない。実行はOS側の `workflows/`（オーケストレーション層）や `skills/`（インフラ層）が担うべきである。
* **Agent駆動アーキテクチャにおけるAreaの役割 (Context Harnessing)**:
  `20_Areas` に記述される内容は単なる読み物ではなく、「AgentのSystem Promptを動的にコンパイルするためのソースコード」である。ルールを書き換えるだけでシステム全体の振る舞いが変わる「宣言的インフラ」としての機能を持つ。
* **コンテキストエンジニアリングの徹底**:
  ハルシネーションやContext Pollutionを防ぐため、`20_Areas` には「過去の決定履歴（ADR）」を残さず、常に「最新の真実（SSOT）」と「直下のインライン・ラショナール（なぜそのルールが必要か）」のみを配置することが極めて有効である。

## 3. 認識された技術的負債・未決事項 (Tech Debt / Open Items)
* **`.agent` ディレクトリの物理的混在**:
  実質的な実行エンジンである `.agent/workflows/` 等が、いまだに静的知識のVaultである `second-brain/` の中に残存している。これを `play_ground/.agent`（OS側）へ移行しなければならない。
* **Agent Memory の所在 (課題D)**:
  Agentの一時的な記憶（episodic logs等）をVault側で保持すべきか、OS側で持つべきかの思想的な決定が保留となっている。
* **テンプレート定義の不足 (課題E)**:
  Agentにプロンプトとしてインジェクトするための、各Policyファイルの厳密なYAMLフロントマターや記述フォーマットが未確定である。
* **ポリシー間の依存関係解決 (課題F)**:
  他部門のポリシーへの依存（Wikiリンク等）を許容する場合、それをAgent OS側でどう再帰的に読み込ませるかの実装方針が未定である。

## 4. システム改善案 (System Improvements)
* 上記の未決事項について決定を下し、`20_Areas` のための標準Policyテンプレートを作成・適用する。
* OS側（`you-inc-hq` 等）に、特定のAgentが起動した際に自動で `20_Areas` 内の該当Markdownを収集しSystem Promptをビルドする「Context Harnessing」の機能を実装する。
