# 💡 Lessons Learned: agent_company_architecture

## 🤖 ルートA：Agent・仕組みの学び（`docs/experiences/`・`docs/rules/`・`SKILL.md`・Linter へ還流済み）
1. **`[EXP-07]` チームリーダーの自己実装バイアスと対策**:
   - 初回試運転（`Flash` リーダー）ではリーダー自身がテストと実装を直接書き、`invoke_subagent` が0回となった。
   - `team-leader/SKILL.md` を `Model="pro"` に引き上げ、「ドメイン実装・TDD対象ではリーダーによる `.py` 直接編集を禁じ、必ず `tdd-red-worker` / `tdd-green-worker` / `compliance-reviewer` を別サブエージェントとして起動せよ」と明文化。本番試運転（`2f05ff1a`）にて4回のサブエージェント起動と2-Pass引き算修正が完走することを実証した。
2. **`[EXP-02]` / Pass 2 引き算レビューの実効性検証**:
   - Pass 1 で `tdd-green-worker` が CLI を通すために既存の `RegisterPermanentNoteDto` / `RegisterSenseMakingNoteDto` に不要な互換フィールドや `__post_init__` を足し算していたが、`compliance-reviewer (pro)` が 🔴 `MUST [F-01]`・🟡 `SHOULD [F-02, F-03]` として正確に検知し、Pass 2 で DTO の足し算パッチをすべて削ぎ落として CLI 側の引数マッピングへ純化させた。
3. **Worktree 内での Linter 相対パス解決**:
   - `audit_skills.py` と `pre_handoff_verify.sh` が親ディレクトリ構造をハードコードしていたため、Worktree 内で自身のルート（`Path(__file__).resolve().parent.parent`）を基準にするよう修正した。

## 🧠 ルートB：社長自身の気づき・内省（`second-brain` 永続化完了）
1. **権限委譲とはHOWを手放し、WHYとWHATと仕組みの設計を握り続けることである**:
   - `40_Permanent_Notes/権限委譲とはHOWを手放し、WHYとWHATと仕組みの設計を握り続けることである.md` として登録。
   - 作業の流れやソース1行1行の精査（HOW）は現場へ徹底して手放すが、目的（WHY）、成果物境界（WHAT）、失敗要因（WHY NOT）、そして組織設計は絶対に手放さない。
2. **本質は引き算ではなく目的への純化であり、WHYが明確であればHOWはいくらでも代替可能である**:
   - `40_Permanent_Notes/本質は引き算ではなく目的への純化であり、WHYが明確であればHOWはいくらでも代替可能である.md` として登録。
   - 安易な足し算パッチは「指摘解消というHOWの目的化」から生じる。「引き算」は目的ではなく、目的に立ち返った結果現れる純化の現象である。WHYがロックされていればHOWは柔軟に代替可能。
