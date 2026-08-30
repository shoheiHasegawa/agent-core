# Reporting Contract (完了報告の型)

ワーカー（子Agent）は、自身のタスクを完了して親（オーケストレーター）に処理を返す際、必ず以下のフォーマット（Markdown）に従って結果を報告しなければならない。
自然言語のみの散文的な報告は禁止される。

## 報告フォーマット

```markdown
### 📝 Worker Execution Report

**1. 実行ステータス (Status)**
- `[ SUCCESS | FAILED ]`
- (FAILEDの場合、端的な理由をここに記載)

**2. 変更・作成したファイル (Modified Files)**
- `file/path/to/modified.py`
- `file/path/to/new_test.py`
*(※絶対パスまたはワークスペース相対パスで正確に記載すること)*

**3. 実行した品質Gateコマンド (Executed Gates)**
- `コマンド`: 例 `uv run pytest tests/integration/...`
- `結果`: 例 `3 passed, 1 failed`

**4. ブロッカー / 申し送り事項 (Blockers / Insights)**
- (エラーで失敗した場合のログの抜粋や、親へエスカレーションしたい問題、ルールの曖昧さに対するフィードバックがあれば記載)
- なければ `None`
```
