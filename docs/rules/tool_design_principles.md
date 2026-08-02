# Tool Design Principles (JSON-First Protocol)

本ドキュメントは、`agent-core/tools/` 配下に配置されるすべてのAgent用CLIツールの設計・実装原則を定める正本仕様（Timeless SSOT）である。

---

## 1. コア原則: JSON-First Protocol

LLM（Agent）がコマンドラインを通じてツールを実行する際の摩擦（シェルエスケープ事故、一時ファイル生成、引数のパース不整合）をゼロにするため、すべてのツールは以下の規格に準拠せよ。

### (1) JSON-In（標準入力および引数からの構造化データ受取）
- **パイプ/標準入力の最優先**: すべての作成・更新系ツールは、標準入力（stdin）から渡されたJSON文字列を直接パースしてインメモリ処理できなければならない。
- **ファイル/引数のフォールバック**: `--json '{"..."}'` 引数、または `--file input.json` によるファイル指定もサポートする。
- **バッチ対応（単一/配列の多態性）**: 入力JSONは単一のオブジェクト（`{...}`）およびオブジェクトの配列（`[{...}, {...}]`）の両方を受け付け、単一実行も一括実行も同一インターフェースで処理せよ。

### (2) JSON-Out（構造化された実行結果の返却）
- **機械可読な出力**: 参照系ツール（Read）および更新系ツール（Write）は、結果を標準出力にJSONフォーマットで出力せよ。
- **標準スキーマ**:
  ```json
  {
    "success": true,
    "count": 2,
    "data": [
      { "id": "note-1", "title": "Note Title", "status": "created" }
    ],
    "errors": []
  }
  ```
- **エラー時の挙動**: 失敗時は `success: false` とエラー詳細をJSONで返し、適切な終了コード（`sys.exit(1)`）で終了せよ。

### (3) Leave No Trace (一時ファイルフリー)
- 一時ファイル（`scratch/tmp.md` 等）を作成して引数に渡す方式（`--body_file` 等）は廃止し、すべてインメモリ（標準入力ストリーム）で完結させよ。

### (4) 環境の自己解決 (Self-Contained Execution)
- ツールは実行時のカレントワーキングディレクトリに依存せず、自身のパスから `app_context.py` を通じて `core-service` のDIコンテナおよび依存ライブラリを自動解決せよ。

---

## 2. ツール実装テンプレート (Standard Skeleton)

すべてのCLIツールは以下の標準スケルトンに従って実装せよ。

```python
#!/usr/bin/env python3
import json
import sys
from pathlib import Path

# パス解決（agent-core / core-service）
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "agent-core"))
sys.path.insert(0, str(REPO_ROOT / "core-service" / "src"))

from app_context import get_core_service_container

def parse_input() -> list[dict]:
    """標準入力、--json引数、またはファイルからJSON入力を受け取ってリストで返す"""
    # 1. stdin (パイプ)
    if not sys.stdin.isatty():
        content = sys.stdin.read().strip()
        if content:
            data = json.loads(content)
            return [data] if isinstance(data, dict) else data
    
    # 2. 引数解析（省略）...
    return []

def main():
    items = parse_input()
    # 処理ロジック...
    result = {"success": True, "count": len(items)}
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
```
