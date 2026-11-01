# 🧩 You_Inc Core Skills Catalog

本ディレクトリは、4大業務フローから逆算して設計された「薄いSKILL（入出力の契約・手順・停止条件）」を格納する。
判断基準の詳細は [`docs/agent_rules/`](../docs/agent_rules/thinking_os_and_loop_principles.md)（思考原則）および [`docs/experiences/`](../docs/experiences/README.md)（経験・前例ストック）を参照せよ。

## ⚙️ サブエージェント起動時の `Model` 指定仕様
Antigravity の `invoke_subagent` ツールにおける `Model` 引数は `["inherit", "pro", "flash", "flash_lite"]` の4種類である（※Effortの `High/Medium/Low` は親チャットのUI設定であり、サブエージェント呼び出し時は以下の `Model` 値で制御する）：
- **親セッション（秘書・日常の壁打ち）**: チャットUIで基本は **`Flash (High)`** を使用し、ゼロからの重いアーキテクチャ設計時のみ **`Gemini 4 Argon (Medium)`** に切り替える（週次固定枠である `Argon` を温存し、5時間回復枠の `Gemini Models` を主軸にする）。
- **チームリーダー / 独立レビュアー / 知識蒸留**: `invoke_subagent` で **`Model="pro"`** を明示指定（`Gemini Models` の5時間回復枠内で最高精度の統率・監査を行う）。
- **TDD実装ワーカー (`tdd-red` / `tdd-green`)**: `invoke_subagent` で **`Model="flash"`** を明示指定。
- **単純な非破壊調査 (`research-worker`)**: `invoke_subagent` で **`Model="flash_lite"`** を明示指定。

| カテゴリ | スキル名 | `invoke_subagent` Model | 役割（4大フロー対応） |
| :--- | :--- | :---: | :--- |
| **Orchestrators** | [`executive-secretary`](orchestrators/executive-secretary/SKILL.md) | *(親: `Flash High` / 重設計: `Argon`)* | **フロー1 & 3（本社窓口）**: 作戦会議、前例3段階トリアージ、Issue起票、Worktree起動、3点内省ブリーフィング |
| **Orchestrators** | [`team-leader`](orchestrators/team-leader/SKILL.md) | `pro` | **フロー2 & 3（現場監督）**: `spec.md` 分母固定、経験JIT注入、2-Passスパイラルループ指揮、ルートA還流とPR作成 |
| **Orchestrators** | [`zk-distiller`](orchestrators/zk-distiller/SKILL.md) | `pro` / `inherit` | **フロー4（知識蒸留）**: ソクラテス式壁打ちによる社長の思考深掘りと、熱量を保つ Permanent Note 蒸留 |
| **Workers** | [`tdd-red-worker`](workers/tdd-red-worker/SKILL.md) | `flash` | **フロー2（テスト作成）**: 情報隔離（実装コード閲覧禁止）で `spec.md` から失敗テスト（Outer/Inner Red）を作成 |
| **Workers** | [`tdd-green-worker`](workers/tdd-green-worker/SKILL.md) | `flash` | **フロー2（実装＆引き算）**: 最小Green実装と、Pass 2 での引き算ファースト・DDD/SOLIDリファクタリング |
| **Workers** | [`research-worker`](workers/research-worker/SKILL.md) | `flash_lite` | **フロー1 & 2（調査）**: 非破壊でのコードベース・過去前例の調査と `scratch/research_report.md` 出力 |
| **Reviewers** | [`compliance-reviewer`](reviewers/compliance-reviewer/SKILL.md) | `pro` | **フロー2（独立監査）**: `{spec.md分母} - {テストID} = 0` の引き算レビューと 🔴`MUST` / 🟡`SHOULD` / 🟢`IMO` 判定 |
