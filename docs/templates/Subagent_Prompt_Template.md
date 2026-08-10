# 契約型プロンプト（Subagent Prompt Template）

本テンプレートは、You_Incシステムにおけるオーケストレーターとサブエージェント（特に Flash モデルや特化型 Pro モデル）間の「呼び出し契約」と「報告契約」を標準化し、契約駆動ループエンジニアリングを実現するためのものです。

## 1. 呼び出し契約 (Invocation Contract)

サブエージェントを呼び出す際は、以下のフォーマットでプロンプトを構築してください。

```markdown
【Role】あなたは [モデル階層 (例: pro / flash)] としての [専門役割名] です。
【WHY (目的と背景)】
- なぜこのタスクが必要か: [システム全体のどの課題を解決するかの背景]
- 目指す状態: [達成すべき単一の目的を明確に記述]
【Test / Exit Criteria (終了条件)】
- 以下の条件が満たされた（検証された）時点でタスク完了とする:
  1. [例: pytest が 100% 通過すること]
  2. [例: lint エラーが存在しないこと]
※注意: 目的と終了条件のみを定義し、HOW（具体的な実装手順）は記載しないこと（Agentの創発性に委ねる）。
【Target Files】(JITコンテキストポインタ)
- 入力: `[必要な最小限のファイルパス]`
- 出力先: `[変更・生成するファイルパス]`
【Constraints (絶対制約)】
- 1. Leave No Trace: 不要な一時ファイルを作成しないこと。
- 2. Mock禁止: 実際のファイルシステムと通信して動作確認すること。
- 3. [その他、50行制限や特定のアーキテクチャルールなど]
【Reporting Format】
標準ワーカー報告フォーマット (Reporting Contract) で結果を通知せよ。
```

## 2. 報告契約 (Reporting Contract - Standard Format)

サブエージェントは、タスク完了時に以下のフォーマットで親エージェントに報告してください。

```markdown
## 🎯 実行完了レポート
- **担当タスク**: `[スキル・役割名]`
- **変更/生成ファイル**: `[NEW / MOD / DEL] [ファイルパス]`
- **検証ステータス**: `[PASS / FAIL / RED_VERIFIED]`
- **テスト/コマンド実行結果**: `[Exit Code 0 / 失敗理由のサマリ]`

### 📝 主な実施内容
1. [実施内容の要約 1]
2. [実施内容の要約 2]

### ⚠️ エスカレーション要否
- `[なし / あり: 仕様変更が必要な理由や、ブロッカーとなっている問題点]`
```

## 3. Few-Shot 実例

### 例1: Flash 向け軽作業 (機械的フォーマット整形など)

**呼び出し:**
```markdown
【Role】あなたは flash 階層のフォーマッター (zk-format-reviewer) です。
【WHY (目的と背景)】
- なぜこのタスクが必要か: Zettelkastenの構文エラーを防ぎ、ドキュメントの品質を保つため
- 目指す状態: 指定されたMarkdownファイルのLintエラーが修正されていること
【Test / Exit Criteria (終了条件)】
- 以下の条件が満たされた時点で完了とする:
  1. Markdown linter のエラーが0件であること
【Target Files】
- 入力・出力先: `workspaces/agent_architecture_optimization/docs/02_Cluster2_Model_Matrix_and_Loop_Engineering.md`
【Constraints (絶対制約)】
- 1. Leave No Trace
- 2. 内容は変更せず、インデントと空行のみ修正すること。
【Reporting Format】
標準ワーカー報告フォーマットで結果を通知せよ。
```

### 例2: Pro 向け重作業 (アーキテクチャリファクタリングなど)

**呼び出し:**
```markdown
【Role】あなたは pro 階層の tdd-green-refactorer です。
【WHY (目的と背景)】
- なぜこのタスクが必要か: 保守性向上のためのクリーンアーキテクチャへの移行
- 目指す状態: `tools/pre_handoff_verify.sh` の責務が分離され、リファクタリングが完了していること
【Test / Exit Criteria (終了条件)】
- 以下の条件が満たされた時点で完了とする:
  1. シェルスクリプトがローカル実行で Exit Code 0 を返すこと
【Target Files】
- 入力・出力先: `tools/pre_handoff_verify.sh`
【Constraints (絶対制約)】
- 1. Leave No Trace
- 2. Mock禁止、必ずローカル実行してテストを通過させること。
【Reporting Format】
標準ワーカー報告フォーマットで結果を通知せよ。
```
