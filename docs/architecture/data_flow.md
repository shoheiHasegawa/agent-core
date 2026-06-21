# Data Flow Architecture

You_Inc エコシステムにおける、主要な情報の流れ（データフロー）を定義します。

## メモの作成から知識化（蒸留）までのフロー

人間がモバイルでメモを作成し、それがAIによって処理され永続的な知識になるまでの流れです。

```mermaid
sequenceDiagram
    actor User as 社長 (人間)
    participant Mobile as Mobile Vault
    participant SB_Inbox as second-brain/00_Inbox
    participant Agent as agent-core (AI)
    participant SB_Perm as second-brain/40_Permanent_Notes
    
    User->>Mobile: アイデア・メモを素早く書き込む
    note over Mobile,SB_Inbox: Git等による自動同期
    Mobile->>SB_Inbox: ファイルが同期される
    
    loop 定期実行 / トリガー実行
        Agent->>SB_Inbox: Inboxに未処理のメモがないかスキャン
        opt 未処理メモあり
            Agent->>Agent: 文脈の理解・要約・蒸留 (Sense-Making)
            Agent->>SB_Perm: Zettelkastenフォーマットで知識として保存
            Agent->>SB_Inbox: 処理済みの元メモを削除/アーカイブ
            note over Agent: Harvest Reportで処理完了を記録
        end
    end
    
    note over SB_Perm,Mobile: Git等による自動同期
    SB_Perm->>Mobile: 整理された知識がMobileへ同期
    User->>Mobile: 完成した知識を閲覧
```

このフローにより、人間は「書く」ことに集中し、AIが「整理・構造化」を自律的に引き受けるオーケストレーションが成立します。
