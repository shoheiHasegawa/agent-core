# Mobile Vault Strategy

You_Incのアーキテクチャにおいて、Gitで管理される `second-brain` とは別に、人間（社長）が日常的にアクセスするエンドポイントとして「Mobile Vault（Obsidian等）」が存在します。

## 存在意義
- **即時キャプチャ**: 外出先やベッドルームなど、PC（ターミナルやVSCode）が開けない状況でも、思いついたアイデアやタスクを即座に記録（Inboxへ投入）するため。
- **閲覧性**: 蓄積された知識（Permanent Notes）をモバイルデバイスで快適に検索・閲覧するためのUIとして機能します。

## 同期と役割分担
Mobile Vault は原則として `second-brain` のサブセット、あるいは完全なクローンとして振る舞います。

- **Write**: 人間はMobile Vaultの `00_Inbox` にメモを書き込みます。
- **Sync**: （※同期ツールやGitの自動Push/Pullの仕組みを通じて）Mobile Vaultの内容は `second-brain` にマージされます。
- **Process**: `agent-core`（AI）は、同期された `00_Inbox` の内容を検知し、自律的に蒸留（Sense-Making）やタスク化を行います。
- **Read**: AIが生成・整理した成果物は再びMobile Vaultへ同期され、人間が閲覧します。
