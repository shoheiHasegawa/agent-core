---
name: tool-architect
description: JSON-First Protocolに準拠したCLIツール（agent-core/tools/）を設計・実装・テストし、孤立監査への参照登録までを行う特化スキル（Tier 2）。
model: pro
type: Worker
---

# SKILL: Tool Architect

このファイルは、特定のタスクを実行するための具体的な手法（Layer 3）を定義する。

## 🎯 目的 (ミクロな WHY)
なぜこのスキル（手順）が存在するのか。
- エージェント間で確実なパースが行えるように、JSON-First Protocolに準拠したCLIツールを設計するため。
- ツールの自己浄化・孤立スクリプト化（Orphan Audit）を防ぎ、システム全体の健全性を保つため。
- 中間ファイルを残さない（Leave No Trace）インメモリ完結の設計を徹底するため。

## 📥 入力と出力 (ミクロな WHAT)
※ ここでのWHATはシステム大局の目的ではなく、このスキル（関数）が受け取るべき「前提条件・インターフェースの制約」である。
- **Input**: ツール化したい機能要件、連携対象の `core-service` サービス/ユースケース
- **Output**: 設計・実装・検証され、孤立監査をパスしたCLIツールスクリプト (`agent-core/tools/` 配下)

## 🛠️ 実行手順 (HOW)
具体的にどうやってタスクを達成するか。
1. `agent-core/docs/rules/tool_design_principles.md` および `agent-core/docs/architecture/skill_design_principles.md` をJITロードし、それに準拠しているかをチェックする。
2. ツール化の要否（YAGNI）を検証し、必要な場合のみI/O設計仕様（JSONスキーマ案）を定義する。
3. JITロードした標準スケルトンに従い、`agent-core/tools/<tool_name>.py` を作成し、実行権限（`chmod +x`）を付与する。
4. 標準入力（stdin パイプ）、`--json` 引数、異常系テストを実行し、生成されたファイルがあれば完全にクリーンアップする（Leave No Trace）。
5. ツールを利用する `agent-core/skills/<skill>/SKILL.md` または `agent-core/docs/` にツール名を記載する。
6. `uv run python agent-core/tools/audit_orphan_scripts.py` を実行し、参照エラーがないことを確認する。
7. [完了条件 / Exit Criteria] 監査合格後、標準の報告フォーマット（Reporting Contract）にて親エージェントへ報告し終了する。
