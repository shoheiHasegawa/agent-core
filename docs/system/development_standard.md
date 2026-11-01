# You_Inc Standard Development Framework (開発標準規約)

You_Inc におけるすべてのソフトウェア開発行為（新規機能開発、機能改修、バグ修正）は、本規約に定義された **「3-Tier Architecture ✕ 2大ループ ✕ 2大関所」** の標準レールに従って実行されなければならない。

---

## 1. 開発フローと分離アーキテクチャ (Playbook & Harness)

```
╔═════════════════════════════════════════════════════════════════════════════╗
║  【Tier 0: プロジェクト・現在地管理層 (Playbook & Tracker)】                  ║
║   ・管理場所: workspaces/<epic_name>/tasks/progress.md                   ║
║   ・責務: 全体進捗の可視化、セッション中断・再開時の現在地復元、ループの表現       ║
║   ・オーケストレーター: session-manager (専任で書き込み、子は読めない)            ║
╚═════════════════════════════════════════════════════════════════════════════╝
                                  │
          ┌───────────────────────┴───────────────────────┐
          ▼                                               ▼
╔═══════════════════════════════╗               ╔═══════════════════════════════╗
║ 【Tier 1A: 協働仕様策定フェーズ】║ ──(Human Gate)─>║ 【Tier 1B: 自律TDD実装フェーズ】 ║
║ (Co-Creation Discovery)       ║               ║ (Double-Loop TDD Harness)     ║
║                               ║               ║                               ║
║ ・担当: 人間 ＋ /grill-me     ║               ║ ・統括: session-manager        ║
║ ・出力: 確定した spec.md      ║               ║ ・実働: 隔離されたワーカー群   ║
╚═══════════════════════════════╝               ╚═══════════════════════════════╝
```

---

## 2. 2大ループと2大関所

### 🗣️ Loop 1: 協働仕様策定フェーズ (Co-Creation Discovery)
- **担当**: 人間 ＋ ネイティブコマンド（`/grill-me` 等）
- **目的**: What to Build の具体化と「仕様の穴」の実装前炙り出し。
- **実行手順**:
  1. **Socratic Discovery**: 要求のヒアリングと業務シナリオの言語化。
  2. **6大観点ストレステスト**: エッジケース（主系, 冪等性, 境界値, 外部調停, 異常系, 不変条件）に関する意図的な問いかけ。
  3. **spec.md 生成**: 合意内容を Timeless SSOT として記述。
- **🚪【関所 1: Human Gate (仕様承認)】**:
  - `session-manager` は `spec.md` が論理破綻していないか品質Gateで検証し、承認（Approve）を得るまで実装ループには進まない。

---

### ⚙️ Loop 2: 自律ダブルループTDD (Double-Loop TDD Harness)
- **統括**: `session-manager` (ルーター)
- **実働**: 物理隔離された `tdd-red-worker` と `tdd-green-worker`
- **入力**: ユーザー承認済みの `spec.md`
- **実行手順**:
  1. **Outer Red (テスト作成)**: 親が `tdd-red-worker` を起動。ワーカーは `spec.md` だけを見て失敗する結合テスト（Proofs of Red）を作成。
  2. **Inner Green (実装)**: 親が `tdd-green-worker` を起動。ワーカーはテストを絶対の防波堤として実装し、ドメイン意図を汲んでリファクタリング。
  3. **Quality Gate**: ワーカーからの Reporting Contract を受け取り、親が `make check-all` を機械的に検証。
- **🚪【関所 2: Compliance Gate (非常ベルと多重防衛線)】**:
  - `session-manager` はループ回数を Tracker に記録し、「3周以上同じエラー」や未決事項が発生した場合は直ちに非常ベルを鳴らし（Check-out）、人間にエスカレーションする。
  - 実装前後に `global-alignment-reviewer`（Whyの整合性）や `compliance-reviewer`（Howの遵守）を独立審査させる。
- **Commit & Handoff (Epicの永続化)**: 全自動検証合格後、KNOWLEDGE_SYNC（ドキュメントの矛盾解消と永続化）とSENSE_MAKING（教訓抽出）を経てアトミックコミット。

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
