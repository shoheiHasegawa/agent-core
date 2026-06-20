# Harvest Report: COO Module Code Review (2026-06-07)

## 📌 Context
- **Target**: `src/modules/coo/daily_planner.py`, `src/modules/coo/factory.py`, `src/modules/coo/entry_point.py`
- **Session Type**: Code Review & Quality Assurance

## 🧠 Wisdom (得られた教訓)
1. **Exit Code & Robustness**: ファサード層（Orchestrator）でのエラーハンドリングでは、例外を単にログに出すだけでなく、エントリーポイント（CLI/API層）にエラー状態を伝達し、適切なシステム終了コード（Exit Code != 0）を発行できる設計を維持すること。例外を握りつぶすとCLIでは「成功」と誤認される。
2. **Fail-Fast in Factory**: DI Factory（Assembler）では、必須の設定ファイル（`credentials.json` など）や環境変数が欠損している場合、単に警告を出して後続の処理に委ねるのではなく、Factory の初期化フェーズで早期に Fail Fast（例外送出）させること。

## ⚠️ Tech Debt (技術的負債)
- **パラメーター型の不統一**: `infrastructure/` へのパス渡しにおいて、`str` 型と `Path` オブジェクトが混在している（例: `RoutineRepository` と `MarkdownTaskRepository`）。統一が必要。
- **デッドコードの存在**: `factory.py` 内で宣言された `inbox_task_file` が使用されておらず、ハードコードされたパスに依存している。
- **argparseの型検査不備**: `--date` のパースが文字列ベースで行われており、実行時の `fromisoformat()` で初めて例外が出る。`argparse` 側の機能を使って事前バリデーションを行うべき。

## 🚀 Actionable Improvements (システム改善案)
1. **例外の再送出**: `daily_planner.py` の `run()` メソッドの例外処理で `raise` を追加するか、戻り値（Result型など）で失敗を返すようにリファクタリングする。
2. **Fail Fast実装**: `factory.py` で `credentials.json` が無い場合、`logger.warning` だけでなく `raise FileNotFoundError("credentials.json is missing.")` を追加する。
3. **コマンドライン引数の堅牢化**: `entry_point.py` にて `parser.add_argument("--date", type=date.fromisoformat, ...)` に修正し、CLIの型検査を強化する。
