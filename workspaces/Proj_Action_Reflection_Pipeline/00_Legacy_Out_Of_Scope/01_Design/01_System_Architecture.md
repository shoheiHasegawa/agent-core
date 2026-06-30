# System Architecture & ADR (Architecture Decision Records)

本ドキュメントは「Task and Calendar Automation」プロジェクトのシステム全体のアーキテクチャ設計と、その根拠（インライン・ラショナール）を記録する。

## 1. 全体アーキテクチャ図（概念）

```mermaid
graph TD
    %% Mobile Layer
    subgraph Mobile[iOS (Presentation & Input)]
        iOS_Cal[iOS Calendar<br>時間・MUST把握]
        iOS_Obsidian[Obsidian Mobile<br>詳細・リスト把握]
        iOS_Shortcut[iOS Shortcuts<br>タスク/メモ入力]
    end

    %% Data Transport
    subgraph Transport[Transport Layer]
        mobile_sync[mobile_sync<br>Dumb Transporter]
    end

    %% Hub Layer
    subgraph DataHub[Data Hub (SSOT)]
        GCal[Google Calendar<br>時間軸SSOT]
    end

    %% Second Brain (PC)
    subgraph PC[Second Brain / PM Agent]
        DropZone[00_Inbox/Drop_Zone]
        CoachAgent[Coach Agent<br>Antigravity Chat]
        Launchd((launchd<br>夜間自動バッチ))
        AgentQueue[[AgentQueue<br>直列化・競合防止]]
        Agent[PM Agent<br>LLM Parsing & Scheduling]
        Vault[(Obsidian Vault<br>Markdown)]
    end

    %% Data Flows
    iOS_Shortcut -- "Text Files" --> Transport
    Transport -- "Move" --> DropZone
    iOS_Cal -- "Native Sync" --> GCal
    
    Launchd -. "Trigger (Job)" .-> AgentQueue
    CoachAgent -. "Trigger (Job)" .-> AgentQueue
    AgentQueue -- "Execute Seq." --> Agent
    CoachAgent -- "Interact (Manual/Skill)" --> Vault
    Agent -- "Read/Parse" --> DropZone
    Agent -- "Fetch/Update" <--> GCal
    Agent -- "Write/Structure" --> Vault
    
    Vault -- "Sync" --> iOS_Obsidian
```

---

## 2. アーキテクチャ決定事項とラショナール（インラインADR）

### ADR 1: Google CalendarのSSOT化とiOSカレンダーのUI利用
*   **決定事項**: システム全体において「時間」と「やるべきタスクの枠（MUST）」の唯一の正本（SSOT）はGoogleカレンダーとする。ユーザーが閲覧するUIとしては、純正の「iOSカレンダー」を使用し、アカウント連携機能でGoogleカレンダーを表示させる。
*   **Why (根拠と背景)**:
    *   **UIとバックエンドの分離**: モバイルアプリを自作することなく、iOSの洗練されたウィジェット機能や通知機能を無料で享受するため。
    *   **双方向同期の恩恵**: ユーザーがiOSカレンダーから（フォーマットを気にせず）雑に入力した予定も、OSのネイティブ機能で即座にGoogleに同期される。これにより、システム側（Agent）から容易にデータを吸い上げ、後からLLMで正規化（フォーマットを整えて上書き）することが可能になる。

### ADR 2: PM Agentの同期頻度と実行基盤（launchd）
*   **決定事項**: 高頻度なリアルタイム同期は行わず、Mac標準のデーモン管理ツール `launchd` を用いて、夜間（例：22:00）またはMacのスリープ解除時をトリガーとする「日次バッチ処理」を基本とする。
*   **Why (根拠と背景)**:
    *   **実行環境の制約**: ユーザーは平日昼間の仕事中、本システムが稼働するMacの電源をオフ（またはスリープ）にしている。そのため、リアルタイム同期システムを組んでも実質的に動作しない。
    *   **行動心理学の観点**: 予定やタスクは「毎晩、翌日の計画を立てる」運用とし、朝起きた時にはすでに計画がセットされている状態が望ましい。

### ADR 3: 入力フォーマットの「緩いルール」化
*   **決定事項**: iOSからの入力（テキスト）において、厳密なYAMLやJSONフォーマットは強制しない。ただし、Agentの解析精度を上げるため、「ショートカットを分ける」「先頭に `[Task]` などのキーワードをつける」といった緩い制約を設ける。
*   **Why (根拠と背景)**:
    *   **UXの優先**: スマホからの入力時に厳密なフォーマットを要求すると「摩擦」が生じ、入力そのものをやめてしまうリスクがある。
    *   **LLMの強み**: 雑な自然言語のメモであっても、背後でLLMが文脈から「タスク」「アイデア」「期限」を抽出し、正規化して処理できるため。

### ADR 4: フェールセーフ（2段構え）の同期・計画実行
*   **決定事項**: 「Drop_Zoneからの吸い上げと翌日のスケジューリング」処理は、ユーザーが能動的に実行する（Skill経由）フローと、`launchd` による裏側の自動実行（深夜帯やMac起動時）の**2段構え**とする。
*   **Why (根拠と背景)**:
    *   **疲労時のセーフティネット**: ユーザーが疲れ果ててジャーナリングを忘れて寝てしまった場合でも、最低限「メモの吸い上げ」と「翌日のMUSTタスクの見える化」が完了している状態を担保し、翌朝のスタートダッシュを阻害しないため。

### ADR 5: ディープリンク（Obsidian URI）を用いたコンテキスト統合
*   **決定事項**: カレンダー（時間情報）とObsidian（詳細情報）を明確に役割分担し、両者を繋ぐブリッジとして「カレンダーの予定詳細欄にObsidian URI（`obsidian://...`）を埋め込む」設計を採用する。
*   **Why (根拠と背景)**:
    *   **役割の分離**: カレンダーには「買い物リスト」や「筋トレメニュー」の詳細までは書ききれない。しかし、実行時にはそれらの情報が必須である。
    *   **シームレスなUX**: モバイル端末において、カレンダーの予定からワンタップで関連するObsidianのメモ（リストやメニュー）に直接飛べることは、圧倒的な摩擦の少なさを実現する。

### ADR 6: タスク完了ステータスの管理とジャーナリングの導入
*   **決定事項**: カレンダーUIはあくまで「見える化」に徹し、タスクの完了・未完了状態はカレンダー上では管理しない。進捗や完了状態の管理は、Obsidian上で行うか、毎晩の「Coach Agent（原田メソッド・社会構成主義ベース）」とのジャーナリング対話を通じて記録・分析する。
*   **Why (根拠と背景)**:
    *   **カレンダーの限界**: 予定は時間がくれば消えてしまうため、タスク管理ツールとしてのDoneの管理には向かない。
    *   **認識の世界観構築とアライメント**: 単なる振り返りではなく、「未来に向かって迷子になっていないか」「作業すること自体が目的になっていないか」を確認し、アクションと理想を一致させるため。

### ADR 7: Agentの自律的成長ループと「休息」のスケジューリング
*   **決定事項**: PM Agentは「いかにタスクを詰め込むか（生産性）」ではなく、「いかに持続可能か（Well-Being）」を重視する。ユーザーの性質（ストイックすぎて休むのが苦手）を考慮し、Agentには**自律的な成長機構（フィードバックループ）**と**休息の強制提案**を実装する。
*   **Why (根拠と背景)**:
    *   **バーンアウトの防止**: 土日も勉強し続けてしまうユーザーに対し、Agentが客観的なストッパーとなり、適切な粒度へのタスク分解やリフレッシュ時間をカレンダーに「予定」として組み込む。
    *   **自律的成長の仕組み**: Globalルールの【自律的成長】に則り、Agentは毎晩の計画時に「予定と実績の乖離（タスク粒度が大きすぎた等）」を分析する。得た教訓は自身のプロファイルファイル（例: `PM_Agent_Wisdom.md`）の `Accumulated Wisdom` に追記（自己更新）する。翌日の計画時は必ずこのWisdomを読み込むことで、日を追うごとに「ユーザーのペースに合わせた完璧なスケジュール提案」ができるように成長する。

### ADR 8: すべての固定予定・ルーティンのSecond Brain（Obsidian）への集約
*   **決定事項**: 「毎週月曜の会議」のような固定のスケジュールも、「毎月25日の支払い」のようなルーティンタスクも、**すべてSecond Brain（Obsidian）内のマスターファイル（例: `Routines.md`）に集約して定義する。** Googleカレンダーのネイティブな「繰り返し予定」機能は原則として使用しない。
*   **Why (根拠と背景)**:
    *   **情報の完全な一元化**: ユーザーの生活のルール（OS）をすべてMarkdownとしてSecond Brainに記述することで、管理場所が分散するのを防ぐ。
    *   **Agentによる柔軟なオーケストレーション**: Agentが毎晩 `Routines.md` を読み込むことで、「明日は月曜だから10時に会議ブロックを入れよう」「明日は25日だから支払いをMUSTタスクに入れよう」と一括で知能的に判断し、Googleカレンダーという「出力先（UI）」を綺麗に構築できる。これにより、Googleカレンダーは完全に「Agentが描画するだけのキャンバス」となる。

### ADR 9: 「特定の知識 (Data)」と「汎用ロジック (Mechanism)」の完全分離
*   **決定事項**: ユーザーの関心事やルール（例：第3金曜日は帰社日）という**「特定の知識」**はすべて `second-brain` 側で保持する。`life-automation`（Python）側にはそういった固有の単語やIF文を一切ハードコードせず、渡されたルールを評価・計算するだけの**「汎用的なメカニズム（計算エンジン）」**に徹する。
*   **Why (根拠と背景)**:
    *   **知識の流出と密結合の防止**: ドメイン駆動設計（DDD）の観点から、`life-automation` にユーザー固有の知識を書き込んでしまうと、生活の変化に追従できない脆いシステムになるため。Agentが両者を繋ぐことで、計算エンジンを完全に独立・疎結合化させる。

### ADR 10: Application層のファサード化（orchestrate_daily_planning）とインフラ窓口
*   **決定事項**: Agentが `life-automation` を利用する際、スケジュール計算、既存予定の抽出、Google Calendarへの登録、Mobile View用Markdownファイルの出力といった一連の処理をすべて一つにまとめた `orchestrate_daily_planning()` などのApplication層メソッド（Service）を呼び出す。
*   **Why (根拠と背景)**:
    *   **インフラの隠蔽とAgentの負担軽減**: API通信やファイル出力といった煩雑なインフラ操作をすべて `life-automation` に押し付ける（委譲する）ことで、Agentは最高位の「推論とオーケストレーション」のみに専念できるため。

### ADR 11: AgentQueueの廃止と直列Nightly Batch Pipelineへのピボット
*   **決定事項**: 当初計画していた「SQLiteベースの非同期タスクキュー（AgentQueue）」の構築をオーバーエンジニアリングとして廃止し、代わりに `launchd` を起点とする単一の「Nightly Job-Net（夜間直列バッチパイプライン）」を構築する。
*   **Why (根拠と背景)**:
    *   **KISSの原則**: システムに対するトリガー（入力）が実質的に夜間の定期実行に限られる現状において、DBを用いたキューシステムは過剰である。
    *   **直列処理による競合排除**: キューでワーカーを管理しなくても、1つのPythonスクリプト（`nightly_batch.py`）の中で「回収 ➡️ 解析 ➡️ 計画」の順番で直列に処理を繋ぐだけで、ObsidianのMarkdownファイルに対する競合（コンフリクト）は物理的に発生しないため。

### ADR 12: Agent OS Inbox Pipeline と Life Portfolio による自律運用
*   **決定事項**: `second-brain/00_Inbox` を 00〜03の双方向パイプラインに再編し、タスクを `Work, Growth, Maintenance, Play` の4象限（Life Portfolio）に分類する運用を導入する。
*   **Why (根拠と背景)**: 
    *   **非同期の協働**: 人間とAgentが同じファイルシステム上でタスクを依頼し合う「Agent OS」としての機能を持たせるため。
    *   **予実分析とPDCA**: タスクをただこなすのではなく、Agentが「今週は休息（Play）が少なすぎた」といった分析（Weekly Review）を行い、次週の余白を強制確保するフィードバックループを回すため。
    *   **詳細設計**: 詳細は別紙 [04_Agent_OS_Inbox_and_Portfolio.md](./04_Agent_OS_Inbox_and_Portfolio.md) を参照のこと。

### ADR 13: iPhone ショートカットと LLM による「ルーティング（Triage）」設計
*   **決定事項**: iOSのショートカットからシステムにメモを投下する際、厳密なフォーマット制約は設けない。ただし、以下のインフラ制約（コントラクト）を設ける。
    1. **1思考=1ファイル**: ファイルの追記ではなく、1回の実行につき1つの `.md` ファイルを生成する。
    2. **日時の保持**: タイムスタンプをファイル名または本文に自動付与する。
    これらを条件とし、後続のPM Agent（Gemini Flash等の軽量モデル）が、ファイルの内容を要約・破壊することなく、文脈から判断して適切なフォルダ（Drop Zone ➡️ TaskPool または Idea_Backlog）へ**ルーティング（物理ファイルの移動）**のみを行う。
*   **Why (根拠と背景)**:
    *   **アイデア原液の保護**: 軽量モデルに要約まで任せると、ユーザーのポエムや生々しい感情などの「ニュアンス（アイデアの原液）」が消滅してしまうため。
    *   **UXの最大化**: ユーザーはフォーマットを気にせず自然言語で入力でき、システム側は「ファイル単位での移動」だけで安全にデータを仕分けられる。
