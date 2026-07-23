# Software Design Document: Inbox Triage Tools

## 概要 (Overview)
Agentic OS の「Inbox Triage」スキルにおいて、人間とAgent間の認知負荷（会話の往復回数）と一時ファイル作成のオーバーヘッドを削減するため、対象のCLIツール群（`agent-core/tools/`）を拡張する。

## 対象ツールと仕様変更

### 1. `read_inbox_queue.py`
未処理のInboxパケットを読み取り標準出力にダンプするツール。

*   **新規要件**: バッチ処理のサポート
*   **引数追加**: `--limit <int>`
    *   指定された場合、パケットの取得上限を `<int>` 件に制限する。
    *   デフォルトは `0` (制限なし: 後方互換性のため)。
*   **振る舞い**:
    *   `queue/` ディレクトリ内のパケットをアルファベット順（または更新順）で取得し、`limit` の数だけ処理して出力する。
    *   出力フォーマットは既存のまま維持する。

### 2. `register_zettelkasten_note.py`
DIコンテナを経由してZettelkastenにノートを登録するツール。

*   **新規要件**: 標準入力（stdin）からの本文（Body）読み取りサポート
*   **引数変更**: `--body_file` は引き続きサポートするが、オプショナルな扱いとする。
*   **振る舞い**:
    *   `--body_file` が指定されており、かつファイルが存在する場合はファイルから読み取る（既存仕様）。
    *   `--body_file` が指定されていない、またはファイルが存在しない場合で、**標準入力（stdin）にデータがパイプされている場合 (`not sys.stdin.isatty()`)** は、標準入力からテキストを読み取って `body_content` とする。
    *   どちらも無い場合は空文字として扱う（既存仕様）。

## テスト要件 (TDD)
本実装はTDDの原則に従い、`agent-core/tests/tools/` ディレクトリ配下にテストを配置する。
CLIツールのテストであるため、`subprocess` や `unittest.mock.patch` 等を用いて、引数パースと標準入出力の振る舞いを検証すること。
