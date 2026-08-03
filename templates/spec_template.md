# [Feature Name] 仕様書 (spec.md)

## 1. Design Decisions & Rationale (設計根拠)

- **なぜこの設計なのか**:
  - [設計判断とトレードオフの理由を記載]
- **なぜSoR分離/永続化構造なのか**:
  - [状態管理や外部連携の根拠を記載]

---

## 2. Contract (I/O Types & Stubs)

### Input (DTO / Command)
- **`[InputDtoName]`**:
  - `field_1: Type` (必須: 説明)
  - `field_2: Optional[Type]` (任意: 説明)

### Output (DTO / Entity / Event)
- **`[OutputDtoName]`**:
  - `field_1: Type`
  - `warning_flags: List[str]`

### Exceptions (エラー・例外設計)
- 原則として Python 標準例外（`ValueError`, `FileNotFoundError`, `FileExistsError` 等）を使用し、独自例外の乱立を避けること（詳細は `docs/rules/error_handling.md` 参照）。
- **`ValueError`**: [不正入力、未存在リソース、境界値違反、自己依存等の発生条件]
- **`[OtherStandardException]`**: [発生条件とハンドリング方針]

---

## 3. Scenarios (受入・テスト要求シナリオ - 6大観点マトリクス)

### ① 正常系 (Happy Path)
- `[TAG-01]`: [主要な入力に対する期待される正常な出力と状態変化]

### ② 冪等性・再実行 (Idempotency & Lifecycle)
- `[TAG-02]`: [同一操作・ジョブが複数回連続実行された場合でも、重複生成・副作用・時刻破壊が発生せず冪等であること]
- `[TAG-03]`: [途中中断・再起動後の再実行時に、完了済みデータが保全され未処理分のみ安全に進行すること]

### ③ 境界値・日跨ぎ (Boundary & Midnight)
- `[TAG-04]`: [日付境界（00:00跨ぎ）、上限/下限、空データ、最大件数時に破綻しないこと]

### ④ 外部同期・差分調停 (Reconciliation & External Drift)
- `[TAG-05]`: [外部SoR（カレンダー/外部ファイル）との双方向/一方向同期において、外部変更とローカル変更が正しく調停されること]

### ⑤ 異常系・耐障害性 (Fault Tolerance & Partial Failure)
- `[TAG-06]`: [一部のストレージ/APIが失敗した場合に安全にフォールバック/スキップされ、全体が破損しないこと]
- `[TAG-07]`: [不正フォーマット・破損データ（ID消失、型不一致）が混入した際に検知・隔離されること]

### ⑥ ドメイン不変条件 (Domain Invariants)
- `[TAG-08]`: [システムが常に満たすべき絶対原則（重複配置の完全排除、安全制約の死守など）が維持されること]
