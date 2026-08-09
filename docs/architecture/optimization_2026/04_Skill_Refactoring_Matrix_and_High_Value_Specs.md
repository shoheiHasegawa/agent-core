# 04: Skill Refactoring Matrix & High-Value Specs (全18スキル刷新仕様)

本ドキュメントは、You_Inc システム内の全18スキルに対する「低付加価値ルールの削減」と「高付加価値要素（思考ヒューリスティクス・Few-Shot・エスカレーション境界・SRP厳格化）」を定義した完全な改修仕様書（Timeless SSOT）である。

---

## 1. 全18スキルの洗練版改修マトリクス一覧

| # | スキル名 | 実行形態 / モデル | 削減・移譲する低付加価値要素 | 💡 注入する高付加価値要素 (知能・ヒューリスティクス) |
|---|---|---|---|---|
| 1 | `night-routine` | 親 (Role Switching) / Pro | 重複ヘッダ、Subagent委譲の矛盾記述、Phase 1内のカウンセリング記述 (SRP是正) | **純粋な進行役 (Orchestration)**: 5段階の対話遷移管理、Phase 2 (`journaling-counselor`) への確実な文脈引き継ぎ |
| 2 | `inbox-triage` | 親 (Role Switching) / Pro | 一時ファイル操作、構文ルール | **2分トリアージ・二者択一Few-Shot**: 「行動(Task)か？知見(Idea)か？」の二者択一、曖昧メモのラダーリング |
| 3 | `journaling-counselor` | 親 (Role Switching) / Pro | 感情記録の定型ルール | **エネルギー感応型カウンセリング**: 疲労度に応じたトーン切り替え、Should未完タスクの心理的摩耗要因の特定 |
| 4 | `priority-planner` | 親 (Role Switching) / Pro | パスハック (`PYTHONPATH=src`), DB禁止警告 | **Eat That Frog & 先送り検知**: 3日連続先送りタスクの粒度半減提案、FocusとMUSTの二者択一提示 |
| 5 | `johari-profiler` | 親 (Role Switching) / Pro | 盲点分析の定型文 | **盲点（Blind Spot）発掘**: 無意識に避けている前提や思い込みを浮き彫りにする深掘り質問構造 |
| 6 | `socratic-interviewer` | 親 (Role Switching) / Pro | 手動フォーマット指示 | **弁証法的止揚（アウフヘーベン）**: 矛盾する主張から一段高い共通解を導く対話フレームワーク |
| 7 | `sdd-spec-writer` | 親 (Role Switching) / Pro | Mock禁止などの機械的規約 | **6大観点ストレステスト Good/Bad**: 競合・並行性・異常系の反証可能・テスト可能な具体的仕様対比 |
| 8 | `session-manager` | 親 (Orchestrator) / Pro | `queue/` 参照、旧パス構造 | **3-Step Lazy Bootstrapping**: `context.md` (≤50行) 最速起動、Handoffクリーンネスの物理保証 |
| 9 | `sdd-loop-orchestrator` | 親 (Orchestrator) / Pro | Model未指定、中間ファイル通信 | **ダブルループTDD指揮 & リトライ追跡**: `[Retry Count: 1/3]` 記録による忘却防止、3回失敗時の中断境界 |
| 10 | `zk-distillation-orchestrator` | 親 (Orchestrator) / Pro | `socratic-interviewer` Subagent呼出 | **アトミックノート蒸留境界**: 一過性のメモから普遍的法則（Permanent Note）を抽出するフィルタリング |
| 11 | `tdd-green-refactorer` | Subagent / **`pro`** | 重複するDocstring規則 | **DIP(依存の逆転) Few-Shot & リファクタリング3大チェック**: インフラ直書き排除、DRY/SRP/意図的命名 |
| 12 | `tool-architect` | Subagent / **`pro`** | `sys.path.insert` パスハック | **JSON-First Protocol 実装**: CLIの入出力完全JSON化、`app_context.py` 自己解決の完全保証 |
| 13 | `skill-architect` | Subagent / **`pro`** | 構文チェックの長文指示 | **SOLIDスキル設計 & 3層ルール配置**: 推論プロンプトとLinterの住み分け設計、Role Switching vs Subagent 裁定 |
| 14 | `skill-reviewer` | Subagent / **`pro`** | 単純な文字数カウント記述 | **多面的スキル品質ゲート**: プロンプト純度、職務分離、Few-Shotの具体性を多面的に審査・合否判定 |
| 15 | `tdd-red-coder` | Subagent / **`flash`** | Mock禁止（Linter移譲） | **怠惰バイアス防止 & 異常系強制抽出**: Null/0件/境界値/文字数超過の隠れたテストケース導出 |
| 16 | `compliance-reviewer` | Subagent / **`flash`** | ルールファイルの一括全読み | **論理的アーキテクチャ境界検知**: インフラ層へのドメインステータス漏出検知、ピンポイント差分提示 |
| 17 | `zk-formatter-qa` | Subagent / **`flash`** | 不要な説明文 | **Zettelkasten厳格フォーマット**: 双方向リンク（`[[...]]`）、タグ、YAMLメタデータの自動正規化 |
| 18 | `workspace-architect` | Subagent / **`flash`** | 手動チェックリストの長文 | **自己完結型ワークスペース構築**: `_index.md`, `tasks/progress.md`, `tasks/context.md` のテンプレート展開 |

---

## 2. カテゴリ別 詳細改修仕様（Few-Shot / ヒューリスティクス実例）

### 🅰️ Category A: 対話・共創スキル（親 Role Switching / Pro）

#### 1. `night-routine` (進行役 Orchestrator)
- **SRPの徹底**: Phase 1 では日報実績の回収と挨拶のみを行い、カウンセリングは行わない。
- **引き継ぎ**: 未完了タスク情報は Phase 2 の `journaling-counselor` への入力としてそのまま渡す。

#### 2. `inbox-triage` (仕分け)
- **思考ヒューリスティクス**: 曖昧なメモに対して認知負荷を下げる二者択一を提示。
- **Few-Shot**:
  > 「このメモ『〇〇の件』について：これは**『いつかやりたい具体的な行動（Task）』**ですか？ それとも**『覚えておきたい概念・アイデア（Idea）』**ですか？ 行動であれば完了条件を、アイデアであればどのカテゴリに紐付けるか決めましょう。」

#### 3. `priority-planner` (優先度計画)
- **先送り検知ヒューリスティクス**:
  > 「タスク『〇〇』は3日連続で未着手のまま先送りされています。心理的ハードルが高い可能性があるため、タスクの粒度を半分（例: 30分以内で終わる第1ステップ）に分割しますか？」
- **地図提示 & Eat That Frog**:
  > 「現在、MUSTタスクが2件滞留しています。明日は朝一番にこの Frog（最重要タスク）を片付けますか？ それとも現在の方針通り進めますか？」

#### 4. `sdd-spec-writer` (仕様策定)
- **反証可能なEdge Case Few-Shot**:
  - *Bad*: `[SPEC-001]` エラー発生時は適切にエラーハンドリングすること。
  - *Good*: `[SPEC-001]` 同一ユーザーが別端末から同時に状態変更（競合）を行った場合、後勝ちとせず `OptimisticLockError` を送出してリクエストを拒否すること。

---

### 🅱️ Category B & 🅲 Category C: 実装・テスト・レビュー系（Subagent）

#### 1. `tdd-red-coder` (テスト雛形生成 / Flash)
- **怠惰バイアス防止思考フォーマット**:
  - 仕様書 `[SPEC-XXX]` から、正常系に加えて以下の4大隠れ異常系を必ず抽出せよ。
    1. 暗黙の None/Null
    2. 0件・空配列
    3. 境界値（最大値+1, 最小値-1）
    4. 不正なフォーマット・型不一致

#### 2. `tdd-green-refactorer` (実装 / Pro)
- **DIP (依存の逆転) Few-Shot**:
  - *Bad*: インフラ層（SQLAlchemyセッションや外部API）をユースケース内に直書きする。
  - *Good*: ドメイン層に `IEventRepository` インターフェースを定義し、コンストラクタ経由で注入（DI）して依存を逆転させる。

#### 3. `compliance-reviewer` (ルール照合 / Flash)
- **論理境界検知**:
  - 構文エラーは `make check-all` に任せ、「インフラ層がドメイン固有のステータス文字列を知ってしまっていないか」等の依存漏出を検知・差分提示する。

---

### 🅳 Category D: オーケストレーター（Tier 1 Orchestrator）

#### 1. `sdd-loop-orchestrator` (Double-Loop TDD)
- **リトライ状態の追跡**:
  - ループ実行時は `tasks/progress.md` に `[Retry Count: N/3]` を物理記録し、3回失敗時は自律修復を中断して人間にエスカレーションする。
