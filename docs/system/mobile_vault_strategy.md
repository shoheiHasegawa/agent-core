# Mobile Vault Strategy

You_Incのアーキテクチャにおいて、Gitで管理される `second-brain` とは別に、人間（社長）が日常的にアクセスするエンドポイントとして「Mobile Vault（Obsidian等）」が存在します。

## 存在意義
- **即時キャプチャ**: 外出先やベッドルームなど、PC（ターミナルやVSCode）が開けない状況でも、思いついたアイデアやタスクを即座に記録（Inboxへ投入）するため。
- **閲覧性**: 蓄積された知識（Permanent Notes）をモバイルデバイスで快適に検索・閲覧するためのUIとして機能します。

## 同期と役割分担
Mobile Vault は人間がアイデアを素早くシステム（You_Inc）に投入するための外部バッファとして機能します。純粋な知識庫である `second-brain` とは直接同期せず、以下のフローを経由します。

- **Write**: 人間は Mobile Vault (出先機関) に未整形のメモやアイデアを書き込みます。
- **Peek & Triage**: `agent-core` (AI) が Mobile Vault の内容を直接 Peek (一覧取得) し、ユーザーと壁打ちを行って「回収するもの」と「Mobileに残すもの」を仕分けます。
- **Process & Format**: 合意されたパケットのみが選択的に回収され、タスクは `Task Registry` へ、アイデアや画像は `second-brain/00_Inbox` や `Attachments` へ適切にフォーマット・移動されます。
- **Read**: 最終的に蒸留された知識（Permanent Notes）は Mobile Vault 側へ同期され、人間が快適に閲覧できるようになります。
