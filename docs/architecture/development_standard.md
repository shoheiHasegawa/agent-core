# You_Inc Standard Development Framework (開発標準規約)

You_Inc におけるすべてのソフトウェア開発行為（新規機能開発、機能改修、バグ修正）は、本規約に定義された **「3-Tier Architecture ✕ 2大ループ ✕ 2大関所」** の標準レールに従って実行されなければならない。

---

## 1. 3層構造 (3-Tier Architecture)

```
╔═════════════════════════════════════════════════════════════════════════════╗
║  【Tier 0: プロジェクト・現在地管理層 (Epic Workspace / progress.md)】       ║
║   ・管理場所: workspaces/<epic_name>/tasks/progress.md                   ║
║   ・責務: 全体進捗の可視化、セッション中断・再開時の現在地復元、マイルストーン管理║
║   ・オーケストレーター: session-manager / workspace-architect              ║
╚═════════════════════════════════════════════════════════════════════════════╝
                                  │
          ┌───────────────────────┴───────────────────────┐
          ▼                                               ▼
╔═══════════════════════════════╗               ╔═══════════════════════════════╗
║ 【Tier 1A: 協働仕様策定ループ】║ ──(Human Gate)─>║ 【Tier 1B: 自律TDDループ】    ║
║ (Co-Creation Discovery Loop)  ║               ║ (Autonomous Double-Loop TDD)  ║
║                               ║               ║                               ║
║ ・スキル: sdd-spec-builder     ║               ║ ・スキル: sdd-loop-orchestrator║
║ ・参加者: ユーザー ✕ AI       ║               ║ ・参加者: AIワーカー群 (自律) ║
║ ・出力: 確定した spec.md      ║               ║ ・出力: 完全テスト済コード    ║
╚═══════════════════════════════╝               ╚═══════════════════════════════╝
```

---

## 2. 2大ループと2大関所

### 🗣️ Loop 1: 協働仕様策定ループ (Co-Creation Discovery Loop)
- **担当**: `sdd-spec-builder` (Role Switching による対話型)
- **目的**: What to Build の具体化と「仕様の穴」の実装前炙り出し。
- **実行手順**:
  1. **Socratic Discovery**: 要求のヒアリングと業務シナリオの言語化。
  2. **6大観点ストレステスト**: エッジケース（主系, 冪等性, 境界値, 外部調停, 異常系, 不変条件）に関する意図的な問いかけ。
  3. **spec.md 生成**: 合意内容を Timeless SSOT として契約（I/O型, 例外型, シナリオ）に記述。
- **🚪【関所 1: Human Gate (仕様承認)】**:
  - ユーザーから明示的な「Approve（承認）」を得るまで、テスト・実装コードの作成には絶対に進まない。

---

### ⚙️ Loop 2: 自律ダブルループTDD (Autonomous Double-Loop TDD)
- **担当**: `sdd-loop-orchestrator` (Subagent Delegation による自律型)
- **入力**: ユーザー承認済みの `spec.md`
- **実行手順**:
  1. **Outer Red**: `tests/integration/` に失敗する結合テストを作成（バグ修正時はバグ再現テスト）。`verify_loop_state.py --phase outer-red` で物理検証。
  2. **Inner Green**: `tdd-green-refactorer` が最小限の実装を行い、`tests/unit/` を補強（Green確認）。
  3. **Quality Gate**: `make check-all`（カバレッジ >= 90%, Ruff lint/format, AST双方向トレーサビリティ）の物理合格。
- **🚪【関所 2: Compliance Gate (司法承認と多重防衛線)】**:
  - 実装前に「どのコードとドキュメント（SSOT）に影響が及ぶか」を事前分析（**Impact Analysis**）させる。
  - `global-alignment-reviewer` サブエージェントが「Why（大局の方針）との整合性」を独立審査する。
  - `compliance-reviewer` サブエージェントが「How（法律）の遵守」と、特に**「コードと関連ドキュメントの同時更新（Atomic Update）」**が行われているかを独立審査する。
- **Commit & Handoff**: 全自動検証合格後のアトミックコミットと `progress.md` 完了記録。

---

## 3. 開発種別ごとの適用方針

| 開発種別 | Loop 1: 仕様策定 (spec.md) | Loop 2: Outer Red (Integration Test) | Loop 2: Inner Green (Impl) |
| :--- | :--- | :--- | :--- |
| **✨ 新規機能開発** | 新規ユースケースと6大観点シナリオを新規作成 | 新規シナリオを満たす結合テストを作成（Red） | ドメイン・UseCase・リポジトリを新規実装 |
| **🔧 既存機能改修** | 既存 `spec.md` の入出力型や変更シナリオを更新 | 変更された仕様に対するテストを更新・追加（Red） | 差分ロジックを修正・リファクタリング |
| **🐛 バグ修正** | **見落とされていたエッジケース（仕様の穴）を `spec.md` に追記** | **バグを100%再現するテストを作成（Red / Proof of Red）** | 原因箇所を修正して Green にする |

---

## 4. エラーハンドリング・例外設計規約 (Error Handling Principles)

システム全体におけるエラーハンドリング（標準例外の活用、Fail-Fastの原則、独自例外の定義基準など）に関する具体的な実装制約は、以下の「法律（Rules）」インデックスを参照してJITロードすること。

- 👉 **[`core-service/docs/rules/_index.md`](file:///Users/shoheihasegawa/you_inc/core-service/docs/rules/_index.md)** (Error Handling セクション)
