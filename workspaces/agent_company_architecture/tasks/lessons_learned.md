# 💡 Lessons Learned: agent_company_architecture

## 🤖 ルートA：Agent・仕組みの学び（`docs/experiences/`・`docs/rules/`・`SKILL.md`・Linter へ還流済み）
1. **`[EXP-07]` チームリーダーの自己実装バイアスと対策**:
   - 初回試運転（`Flash` リーダー）ではリーダー自身がテストと実装を直接書き、`invoke_subagent` が0回となった。
   - `team-leader/SKILL.md` を `Model="pro"` に引き上げ、「ドメイン実装・TDD対象ではリーダーによる `.py` 直接編集を禁じ、必ず `tdd-red-worker` / `tdd-green-worker` / `compliance-reviewer` を別サブエージェントとして起動せよ」と明文化。本番試運転（`2f05ff1a`）にて4回のサブエージェント起動と2-Pass引き算修正が完走することを実証した。
2. **`[EXP-02]` / Pass 2 引き算レビューの実効性検証**:
   - Pass 1 で `tdd-green-worker` が CLI を通すために既存の `RegisterPermanentNoteDto` / `RegisterSenseMakingNoteDto` に不要な互換フィールドや `__post_init__` を足し算していたが、`compliance-reviewer (pro)` が 🔴 `MUST [F-01]`・🟡 `SHOULD [F-02, F-03]` として正確に検知し、Pass 2 で DTO の足し算パッチをすべて削ぎ落として CLI 側の引数マッピングへ純化させた。
3. **Worktree 内での Linter 相対パス解決**:
   - `audit_skills.py` と `pre_handoff_verify.sh` が親ディレクトリ構造をハードコードしていたため、Worktree 内で自身のルート（`Path(__file__).resolve().parent.parent`）を基準にするよう修正した。

## 🧠 ルートB：社長自身の気づき・内省候補（`second-brain` 蒸留候補）
1. **「ブラックボックス化（裸の王様化）」を防ぐ内省タッチポイント**:
   - 権限委譲を進めて人間が介入しなくなるほど、社長自身の成長が止まり社内構造を把握できなくなるパラドックス。クローズ時の「3点ブリーフィング」を成長の仕組みとして組み込む設計。
2. **上流の曖昧さのブルウィップ効果（Bullwhip Effect）と2-Passスパイラル**:
   - `spec.md` の些細な記述ミスを `IMO` として見逃すと、文脈を共有しない後続ワーカー間で解釈が分裂し手戻りが増幅する。また、1周目（貫通）と2周目（全体俯瞰からの引き算）でループの役割を分けることで「過品質の無限ループ」と「DDD崩壊」を同時に防ぐ構造。
