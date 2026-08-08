# 02: Cluster 2 - Model Matrix & Loop Engineering (確定仕様)

本ドキュメントは、You_Inc システムにおける「モデル選択・サブエージェント協調・ループエンジニアリング」の最適化仕様（Timeless SSOT）である。

---

## 1. 職能別モデル配置マトリクス (Model Matrix)

```mermaid
graph TD
    subgraph 1. 対話・壁打ち系 (Interactive)
        D[親 Agent Pro / Role Switching<br>sdd-spec-writer, socratic-interviewer, night-routine, inbox-triage]
    end

    subgraph 2. 密結合・深層実装系 (Heavy Worker)
        H[Subagent: Model 'pro'<br>tdd-green-refactorer, tool-architect, skill-architect, skill-reviewer]
    end

    subgraph 3. 疎結合・定型・高速系 (Lightweight Worker)
        L[Subagent: Model 'flash'<br>tdd-red-coder, compliance-reviewer, zk-formatter-qa, workspace-architect]
    end
```

| 職能区分 | 実行形態 | 採用モデル | 対象スキル | 役割と理由 |
| :--- | :---: | :---: | :--- | :--- |
| **① 対話・壁打ち系** | **親自身** (Role Switching) | **Pro** (UI選択) | `sdd-spec-writer`<br>`socratic-interviewer`<br>`night-routine`<br>`inbox-triage`<br>`johari-profiler`<br>`journaling-counselor`<br>`priority-planner` | ユーザーとの直接対話。伝言ゲームの排除と深い思考・共創。 |
| **② 密結合・高度実装・設計レビュー** | **Subagent** | **`pro`** | `tdd-green-refactorer`<br>`tool-architect`<br>`skill-architect`<br>`skill-reviewer` | クリーンアーキテクチャ、DDD、SOLID原則の遵守、構造的レビュー。 |
| **③ 定型・テスト生成・照合** | **Subagent** | **`flash`** | `tdd-red-coder`<br>`zk-formatter-qa`<br>`compliance-reviewer`<br>`workspace-architect` | 機械的テスト雛形作成、フォーマット整形、ルール照合（高速・低コスト）。 |
| **④ 広範囲リサーチ** | **Subagent** | **`flash`** | `research` サブエージェント | 大量ファイルのスキャンと要約。 |

---

## 2. 通信インフラと実行アーキテクチャ

1. **インメモリ・メッセージング**:
   - 指示・完了報告・差し戻しは、Antigravity 組み込みのメッセージング（`invoke_subagent` / `send_message`）により完全インメモリで完結させる。
   - 一時ファイル（キューなど）をディスクに書き出して通信することは厳禁。
2. **成果物の共有（SSOT）**:
   - 変更コード（`src/`, `tests/`）および設計書（`workspaces/<epic>/docs/`）の実体ファイルを通じて共有する。

---

## 3. 「Pro 1体」 vs 「Multi-Flash 並列」の使い分け指針

- **Pro 1体集中（密結合タスク）**:
  - 複数ファイルにまたがるリファクタリング、深層バグのデバッグ、アーキテクチャ設計。
  - すり合わせコストを排除し、1体の Pro に全体像を持たせて一気に解決させる。
- **Multi-Flash 並列（疎結合・独立タスク）**:
  - 独立した複数ファイルのテスト生成、多面的レビュー（セキュリティ/命名/品質の同時並列チェック）。
  - `invoke_subagent` の配列で複数体同時起動し、所要時間を大幅短縮する。

---

## 4. 契約型プロンプト（呼び出し＆報告テンプレート）

Flash の作業品質を Pro 相当に引き上げるため、入出力のインターフェースを型定義する。

### (1) 呼び出しテンプレート（Task Prompt Contract）
```markdown
【Role】あなたは [専門役割名] です。
【Goal】[達成すべき単一の目的]
【Target Files】
- 入力: `[ファイルパス]`
- 出力先: `[ファイルパス]`
【Constraints (絶対制約)】
- 1. [制約事項1]
- 2. [制約事項2]
【Reporting Format】
標準ワーカー報告フォーマットで結果を通知せよ。
```

### (2) 報告テンプレート（Worker Report Contract）
```markdown
## 🎯 実行完了レポート
- **担当タスク**: `[スキル名]`
- **変更/生成ファイル**: `[NEW/MOD] [パス]`
- **検証ステータス**: `[PASS / FAIL / RED_VERIFIED]`
- **テスト/コマンド実行結果**: `[Exit Code / サマリ]`

### 📝 主な実施内容
1. [実施内容1]
2. [実施内容2]
```
