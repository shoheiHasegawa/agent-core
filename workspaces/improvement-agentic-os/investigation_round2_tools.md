# Round 2: Tooling & Middleware Audit Report

## 概要
`you_inc/agent-core/tools/` 以下のスクリプトを監査した結果、LLMエージェントが使用する上でエラー回復を妨げる入力の脆さや、Gatekeeper（防波堤）としての機能不足など、複数のMUSTレベルの技術的負債・リスクが判明しました。

---

## 1. `update_task.py` における MUST レベルの脆弱性
### ① Enum デシリアライズの脆さ (KeyError の誘発)
LLMは時折、Typoや勝手なステータス（例: `INPROGRESS` や `DONE`）を生成します。
現在の実装では、`argparse` で `choices` を定義せずに直接 `TaskStatus[args.status.upper()]` のように呼び出しているため、無効な文字列が渡されると Python の組み込み `KeyError` が発生します。
**問題点:** エラーメッセージが単なる `KeyError: 'INPROGRESS'` となり、利用可能な選択肢（`TODO`, `IN_PROGRESS`など）がLLMに提示されないため、自己修正が困難になります。
**対策:** `argparse` レベルで `choices=...` を指定するか、パース時にキャッチして明確な利用可能リストを含む `ValueError` を返す必要があります。

### ② 境界値のバリデーション欠落
`--estimated_minutes` に対して引数の説明文では `(> 0)` と記載されていますが、スクリプト内では `type=int` としているのみで、負の値や 0 に対する防御（Gatekeeper機能）がありません。LLMが文脈を誤解して負の数を入れた場合、後続のドメインロジックで予期せぬエラーを引き起こす可能性があります。

---

## 2. `process_inbox_item.py` における MUST レベルの脆弱性
### ① Enum (選択肢) の不整合と不足
`update_task.py` では `energy_level` は `(High, Normal, Low)` と定義されていますが、`process_inbox_item.py` の `argparse` では `choices=["High", "Low"]` となっており `"Normal"` が欠落しています。
**問題点:** LLMが他のツールの経験から `--energy_level Normal` を指定した場合、パースエラーで弾かれます。システム全体でのドメイン語彙の不一致です。

### ② アクション依存の必須パラメータ検証漏れ
`--action task` または `--action idea` として処理する場合、論理的に `title` が必須になりますが、引数定義では `default=""` となっており、空文字列のままドメインサービスに渡されます。
**問題点:** LLMがタイトルを付け忘れた場合、無名のタスクやアイデアが永続化されてしまうか、ドメインサービス内部でわかりにくいエラーが発生します。ツール側で「`task` アクションの場合は `--title` を必ず指定せよ」というフィードバックを即座に返すGatekeeper機能が必要です。

---

## 3. `verify_loop_state.py` における MUST レベルの脆弱性
### ① エラー出力の切り捨てによるデバッグ妨害
Outer Red (テスト失敗) や Green (テスト成功) フェーズの検証において、エラー発生時に `combined[-1000:]` または `[-1500:]` のように末尾の固定文字数のみをスライスして返しています。
**問題点:** pytestのトレースバックが長い場合、最も重要なエラー原因（AssertionError の diff やスタックトレースの根本）が切り捨てられ、LLMが「なぜ落ちたのか」を読み取れず、修正不能な無限ループに陥る危険性が極めて高いです。
**対策:** 単なる末尾スライスではなく、pytestの出力から `FAILURES` セクションや `short test summary info` などの意味的なブロックを抽出して返すParserが必要です。

---

## 4. `register_zettelkasten_note.py` における MUST レベルの脆弱性
### ① STDIN パイプラインにおけるハング（Deadlock）リスク
`sys.stdin.isatty()` が False の場合に `select.select` を使って標準入力を読み取っていますが、CI環境や特定の非同期プロセスからの呼び出し時において、パイプが開いたまま EOF が送られない状態が発生すると、`sys.stdin.read()` で永続的にブロック（ハング）するリスクがあります。
**問題点:** ツールが応答しなくなり、エージェントのタイムアウト・リソース枯渇を引き起こします。
**対策:** 標準入力からのフォールバック読み取りは廃止し、明示的な `--json` 引数や `--file` 引数のみを正とすべきです。

### ② JSONスキーマのGatekeeper不足
`--json` でペイロードを受け取った後、最低限の辞書型チェックしかしておらず、必須フィールドの検証を `register_single_note` 関数内の手動 `if not` に依存しています。
**問題点:** 構造の誤りをLLMに指摘する際のエラーメッセージが場当たり的であり、「スキーマ定義（何を渡すべきか）」をシステムとして正しくLLMにフィードバックする機能が欠如しています。Pydantic等のスキーマ検証ライブラリを用いて、バリデーションエラーを構造化して返す必要があります。

---

## 5. `validate_sdd.py` (Linter) の限界
### ① AST 解析による Evasion (回避) 検知の脆さ
Integration Test での Mock 使用を禁止するため `ast.walk` で `unittest.mock` のインポートや `@patch` を検出していますが、静的解析に過ぎないため、LLMが別のモックライブラリ（`flexmock`, `responses`, `pytest-mock`を使わず直にパッチを当てる等）を使ったり、動的インポート (`importlib` や `sys.modules`) を行った場合には検知をすり抜けます。
**対策:** 完全な Anti-Cheat を実現するには、AST解析だけでなく、テスト実行時（`pytest` のコンフィグ等）で `sys.modules` や関数のモンキーパッチを動的にフック・監視する機構（Runtime Gatekeeper）が必要です。

---

## 結論
現在の Tools スクリプトは「正常系（Happy Path）」では動作するものの、LLMがフォーマットを間違えたり、意図しない入力をした際の「エラーフィードバックの質（Error UX）」が非常に悪いです（KeyErrorの発生、出力の切り捨て、不整合なEnum）。
これらは単なるバグではなく、**「LLMの自己回復（Self-Correction）ループを断ち切ってしまう」** という意味で、Agentic OS におけるMUSTレベルの技術的負債と言えます。
