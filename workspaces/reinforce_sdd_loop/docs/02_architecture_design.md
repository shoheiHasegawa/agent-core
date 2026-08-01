# SDD/TDDループ脆弱性解消のためのレイヤー別アーキテクチャ設計

ここまでの課題を「どのドキュメント（レイヤー）にどんな定義が足りなかったから発生したのか？」という視点で整理した設計書です。

## レイヤー別 不足定義と対策

### Layer 0: Global Constitution (`GEMINI.md`)
- **役割**: プロジェクトを超越した、システム全体の不動の憲法・哲学
- **足りない定義（原因）**:
  - 「Agentはタスクを一気に実装せず、アトミックに実行せよ（WIP制限/インクリメンタリズム）」という大原則がない。
  - 「正本（Timeless SSOT）と過程（時系列）を混同するな」というドキュメントの責務分離原則がない。
- **解決策（タスク）**: Agentの強烈な「一気書きバイアス」を戒めるため、上記2つの大原則を最高法規として明記する。

### Layer 1: Domain Router (`AGENT.md`)
- **役割**: そのドメイン（例: `core-service`）固有のコンテキストと、具体的な実行手段（How）へのルーティング
- **足りない定義（原因）**:
  - AgentがTDDプロセスを実行する際、「プロンプトの指示」に依存しており、システム的なハードゲート（コントローラースクリプト等）を通るルーティングが強制されていない。
- **解決策（タスク）**: 「TDDを行う際は必ず `tdd_controller.py` を通れ」といった、実行手段へのポインタ（ルーティング）を整備する。

### Layer 2: Meta-Rules & Harness (`docs/rules/`, `validate_sdd.py`)
- **役割**: ドキュメント作成のガイドラインや、コードの静的制約
- **足りない定義（原因）**:
  - 「どのファイルに何を書くべきか（責務と境界）」のルール（Document Architecture）が存在しないため、あらゆるファイルが継ぎ足しでFat化している。
  - 自然言語に頼りすぎ、命名規則などをLinter（`validate_sdd.py`）で物理的に弾く仕組みが足りていない。
- **解決策（タスク）**: `document_architecture_principles.md` の策定と、ルールの静的解析（Linter）への移譲・軽量化。

### Layer 3: Meta-Skills (`skill-architect`, `skill-reviewer`)
- **役割**: Agentの振る舞い（SKILL）を設計・審査するメタ層
- **足りない定義（原因）**:
  - 単一責任原則（SRP）の審査が甘く、複数の関心事を持つ「ファットスキル（God Prompt）」の作成を物理的にブロック（Fail）するルールが機能していない。
- **解決策（タスク）**: SKILLがFat化することを物理的に防げるように、レビュールールを極めて厳格に強化する。

### Layer 4: Execution Skills (`core-service-engineer` 等)
- **役割**: 具体的な実行手順
- **足りない定義（原因）**:
  - 「DDDの思想」「テスト手順」「制約」などが1つのファイルに密結合しており、Agentの認知限界（Lost in the middle）を超えている。
- **解決策（タスク）**: SKILLの解体と階層化（SRPの適用）。例：Orchestrator、Spec Writer、Implementerなどに責務を分離する。

### Layer 5: Templates (`spec_template.md` 等)
- **役割**: 出力物のフォーマット・型
- **足りない定義（原因）**:
  - 自然言語ベースのため、I/O型やエッジケースが曖昧（ハルシネーションの温床）。
  - 外部のZettelkastenに依存し、自己完結（Timeless SSOT）していないため、Why（Rationale）が揮発する。
- **解決策（タスク）**: 型定義（GraphQL/Dataclass風）の強制と、インラインRationaleの追加による完全自己完結化。
