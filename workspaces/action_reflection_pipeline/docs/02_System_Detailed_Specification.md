# Epic: System Detailed Specification (5W1H)

本ドキュメントは、Epic「Action & Reflection Pipeline」の具体的な動作仕様を、これまでの全合意事項（心理的要件・アーキテクチャ）に基づき、5W1H形式で詳細化したマスター仕様書です。

## 1. 概要 (The Big Picture)
*   **Who (誰が)**: ユーザー（CEO）と、自律型AIアシスタント（Agent）。
*   **What (何を)**: 「摩擦ゼロのキャプチャ」から「M/S/Wの自動分類とカレンダー配置」、そして「実績集計による免罪符（Safety Pass）発行」までの一連のパイプライン。
*   **Why (なぜ)**: ユーザーの「精神的摩耗」を防ぎ、進捗の安心感（免罪符）を与えることで良質な余暇（Want）を確保し、かつての「無敵感」を取り戻すため。

## 2. 処理フローの詳細仕様 (When, Where, How)

### Phase A: 摩擦ゼロのキャプチャ (Anytime)
*   **When**: 日中・いつでも。
*   **Where**: iPhone (iOS Shortcut) ➡️ iCloud (`Mobile_Vault/Inbox`)
*   **How**:
    *   ユーザーは自然言語でそのまま入力。
    *   LLMがパース失敗した場合や、日々の実績確認の摩擦を下げるため、修正入力は極力iPhoneの通知からのタップ等で完結する「実績報告特化のショートカット」を整備する。

### Phase B: 夜のパースと振り返り (Nightly)
*   **When**: 毎晩（ただしユーザーが疲労時はスキップ可能）。
*   **Where**: Mac (主体: `agent-core` の `night-routine` スキル, 計算・永続化委譲: `core-service`) ➡️ `second-brain` (Git)
*   **How**:
    1.  **壁打ちと選択的パース (Triage)**: `night-routine` スキル（`inbox-triage`）が、直接Mobile VaultをPeekして未処理InboxItemの一覧を取得し、Triage Planを作成する。ユーザーと壁打ちを行い、「回収するもの」と「モバイルに残すもの」を合意した上で、対象のみを分類してタスクDB（`TaskOperationsService`）へ格納、またはアイデアとして保存する。
    2.  **実績の集計（偽の免罪符防止）**:
        *   カレンダー上の予定をそのまま実績とは見なさない。夜の振り返り時、Agentが「今日の `[S]` は予定通り終わりましたか？」と確認し、ユーザーの「Yes/No」をもって初めて実績時間として集計する。
    3.  **ジャーナリング（エスケープハッチ）**:
        *   振り返り自体が新たな「Should」にならないよう、Agentは「今日は疲れていますか？疲れていればスキップして早く寝ましょう！」とユーザーを赦す選択肢を必ず提示する。

### Phase C: スケジューリングと免罪符発行 (Daily Pipeline)
*   **When**: 夜の対話終了時または早朝（`jobs/run_daily_pipeline.sh` 実行時）。
*   **Where**: Mac ➡️ iCloud (`Mobile_Vault/Dashboard/Briefing_YYYY-MM-DD.md`) & Google Calendar
*   **How**:
    1.  **トリアージとカレンダー生成**: `agent-core` がスケジュール生成バッチ（`generate_daily_briefing.py`）を実行し、`core-service`（`DailyPlanningService.plan_day()`）を通じて処理を行う。
        *   その日の `[M]`（必須タスク）が多すぎる場合、無理に `[S]` や「黄金ルーティン」を配置せず、リスケジュールを提案して破綻を防ぐ。
    2.  **免罪符の視覚的強調**:
        *   `[S]` を達成した際に配置される `[W]` の予定は、単なる色分けだけでなく、イベント名に `👑` や `🛡️` などの絵文字を付与し、カレンダー上で**「勝ち取った自由な時間（Safety Pass）」であることを強烈に視覚アピール**する。
    3.  **未消化Wantのストック**:
        *   確保した `[W]` の時間に突発的な用事が入り実行できなかった場合、その「ご褒美の権利」は消滅せず、週末などに繰り越される（ストックされる）仕様とする。

### Phase D: コンパスの見直し (Weekly)
*   **When**: 週に1回。
*   **Where**: `second-brain/10_Areas/`
*   **How**: Agentが「今週のFocus（注力領域）の変更はありますか？」と問いかけ、ユーザーの人生の優先順位（North Star）と同期させる。
