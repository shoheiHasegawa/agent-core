---
name: tool-architect
description: JSON-First Protocolに準拠したCLIツール（agent-core/tools/）を設計・実装・テストし、孤立監査への参照登録までを行う特化スキル（Tier 2）。
model: pro
---

# Skill: Tool Architect

## 🎯 目的
`agent-core/tools/` 配下に配置されるAgent用CLIツールを設計・実装・検証し、Agentic OSの設計標準に完全準拠した堅牢なインターフェースを提供する。

## ⚠️ 絶対遵守ルール
ツールを設計・実装する前に、**必ず**以下の正本ドキュメントを読み込み（`view_file`）、原則に違反していないかをチェックすること。
1. `agent-core/docs/rules/tool_design_principles.md` （Tool Design Principles / JSON-First Protocol）
2. `agent-core/docs/skill_design_principles.md` （ツールの自己浄化・Orphan Audit規則）

### コア制約事項
1. **JSON-First Protocol**:
   - **JSON-In**: 標準入力（stdin パイプ）を最優先でパースせよ。`--json` および `--file` もサポートすること。
   - **JSON-Out**: 結果はすべて構造化JSON（`success`, `results`, `errors` 等）で標準出力に出力せよ。
   - **単一/配列の多態性**: 単一オブジェクト（`{...}`）および配列（`[{...}]`）の双方を同一インターフェースで処理せよ。
2. **Leave No Trace (一時ファイル禁止)**:
   - ツール実行のために中間ファイル（`scratch/tmp.md` 等）を作らせる設計は禁止。インメモリ（標準入力パイプ）で完結させよ。
3. **パスと環境の自己解決**:
   - カレントワーキングディレクトリに依存せず、自身のパスから `app_context.py` を通じて `core-service` のDIコンテナを自動解決せよ。
   - 🚫 **禁止**: `sys.path.insert` 等を用いたパスハック記述は完全排除すること。
4. **孤立スクリプト監査（Orphan Audit）の事前回避**:
   - ツール作成時は、必ず関連する `SKILL.md` または `docs/` にツール名の参照を追記し、`tools/audit_orphan_scripts.py` をパスさせよ。

---

## 🛠️ 実行手順

### 1. 要求分析とYAGNIチェック (Meta-Cognition)
*   **入力 (Input)**: ツール化したい機能要件、連携対象の `core-service` サービス/ユースケース
*   **アクション (Action)**:
    - **メタ認知 (Whyの維持)**: 直ちに設計に入るのではなく、「本当にこの新しいツールは必要か？（YAGNI）」「既存のシェルコマンドや既存のツールで代用できないか？」を自問・検証し、不要と判断した場合はユーザーに代替案を提示する。
    - ツールが必要な場合のみ、入力JSONスキーマおよび出力JSONスキーマを定義する。
    - 従来の個別引数（後方互換）が必要か判断する。
*   **出力 (Output)**: I/O設計仕様（JSONスキーマ案）または代替案の提案

### 2. ツール実装
*   **入力 (Input)**: I/O設計仕様
*   **アクション (Action)**:
    - `agent-core/docs/rules/tool_design_principles.md` の標準スケルトンに従い、`agent-core/tools/<tool_name>.py` を作成する。
    - `select.select` による非同期/パイプ判定、適切な例外ハンドリング、終了コード（`sys.exit(0)` / `sys.exit(1)`）を実装する。
*   **制約事項 (Constraints)**: 実行権限（`chmod +x`）を付与し、シバン（`#!/usr/bin/env python3`）を先頭に記載すること。

### 3. 動作検証とクリーンアップ
*   **入力 (Input)**: 作成したツールスクリプト
*   **アクション (Action)**:
    - 標準入力（stdin パイプ）、`--json` 引数、異常系（不正なJSONや引数不足）のテストを実行する。
    - テストで生成されたファイルやDBレコードを完全にクリーンアップする。
*   **制約事項 (Constraints)**: テスト用ゴミデータを残さないこと（Leave No Trace）。

### 4. 参照登録と監査パス
*   **入力 (Input)**: 検証済みツール
*   **アクション (Action)**:
    - ツールを利用する `agent-core/skills/<skill>/SKILL.md` または `agent-core/docs/` にツール名を記載する。
    - `uv run python agent-core/tools/audit_orphan_scripts.py` を実行し、参照エラーがないことを確認する。
*   **出力 (Output)**: 監査合格ログとツールの完了報告
