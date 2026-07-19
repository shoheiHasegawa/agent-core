# 勉強会用 EC2 自動構築の仕組み (DESIGN.md)

本ドキュメントでは、Oracle 勉強会で使用する受講者用 EC2 インスタンスを自動構築する仕組み、およびそのアーキテクチャについて解説します。

## 1. アーキテクチャ概要

本システムは **AWS Image Builder** による AMI の定期自動生成と、**CloudFormation (CFn) + Lambda** による EC2 インスタンスの一括作成によって構成されています。

```mermaid
graph TD
    subgraph "Phase 1: AMI Creation (Scheduled)"
        IB[AWS Image Builder] -->|Schedule: Jan 1st / Jul 1st| UpdatedAMI[Linux Update Applied AMI]
        UpdatedAMI -->|Named| AMIName[HandsOnBase-Lin-YYYY-MM-DD]
    end

    subgraph "Phase 2: EC2 Deployment (On Demand)"
        User[Operator] -->|Deploy Stack| CFn[CloudFormation Stack]
        CFn -->|Invoke| Lambda[Custom Resource Lambda]
        Lambda -->|Read| CSV[Participant List (CSV)]
        Lambda -->|RunInstances| EC2_1[EC2 Instance 1]
        Lambda -->|RunInstances| EC2_2[EC2 Instance 2]
        Lambda -->|RunInstances| EC2_N[EC2 Instance N...]
        
        UpdatedAMI -.->|Base Image| EC2_1
        UpdatedAMI -.->|Base Image| EC2_2
        UpdatedAMI -.->|Base Image| EC2_N
    end
```

## 2. コンポーネント詳細

### 2.1 AWS Image Builder (AMI 自動生成)

OSのパッチ適用工数を削減するため、AWS Image Builder を使用して定期的に「最新のパッケージが適用された Linux AMI」を自動生成します。

*   **役割**: ベースとなる Linux AMI に `update-linux` コンポーネントを適用し、新しい AMI を作成する。
*   **実行スケジュール**: 毎年 **1月1日** および **7月1日** の 00:00 (JST) に自動実行されます。
*   **成果物 (AMI)**: 生成された AMI は `HandsOnBase-Lin-{{imagebuilder:buildDate}}` という命名規則で保存されます。
*   **構成ファイル**: `imagebuilder-linux-update-ami-pipeline.yaml`

### 2.2 CloudFormation + Lambda (EC2 一括起動)

通常の CloudFormation の `AWS::EC2::Instance` リソースでは、「動的な回数の繰り返し作成」や「CSV リストに基づく一意な Name タグ付け」が難しいため、Custom Resource として Lambda 関数を使用しています。

*   **役割**: 指定された AMI とパラメータを使用して、参加者人数分の EC2 インスタンスを一括で起動する。
*   **ロジック**:
    1.  CFn パラメータとして `TagList` (参加者リスト) と `CommonPassword` (共通パスワード) を受け取る。
    2.  Lambda 内で `TagList` を解析し、インスタンス数を決定する。
    3.  **UserData (起動スクリプト)** を生成し、起動時に `sshd_config` の `PasswordAuthentication` を有効化し、`chpasswd` を用いて全インスタンスの `ec2-user` パスワードを統一する。
    4.  保険としてキーペア (`Oracle-workshop-common-key-pair`) も付与して起動する。
    5.  起動した InstanceId のリストを CloudFormation の Outputs に返却する。
*   **構成ファイル**: `ec2-auto-deploy.yaml`

### 2.3 制限事項 (Limits)

本システムには一度に作成できるインスタンス数に以下の制限があります。

*   **Lambda タイムアウト**:
    *   カスタムリソース Lambda のタイムアウトは **60秒** に設定されています。
    *   API 実行時間を考慮すると、**約 50 台** 程度までが安全圏です。
*   **パラメータサイズ制限**:
    *   CloudFormation のパラメータ (`TagList`) は最大 **4096 バイト** です。
*   **AWS vCPU サービスクォータ**:
    *   AWS アカウントごとのリージョン別 vCPU 上限に依存します（t系インスタンスなど）。不足時は上限緩和申請が必要です。

## 3. 採用理由とメリット

*   **省力化**: パッチ適用作業を自動化することで準備時間を大幅に削減しています。
*   **ミス防止**: 数十台のインスタンスを手動で起動し、一つ一つにタグを付ける作業はミスが発生しやすいですが、スクリプト化することで正確に展開できます。
*   **コスト管理**: 勉強会ごとに環境を使い捨てる（Create & Delete）運用を前提としており、不要なリソースの課金を防ぎます。

## 4. 技術的な考慮事項とハマりどころ (Technical Insights)

### 大規模展開時のリソース競合と起動の高速化
`t3.small` インスタンスで一度に多数（40台以上）のインスタンスを起動すると、初回起動処理やCloud-initの初期化がCPUリソースを奪い合い、UserDataスクリプトの実行が遅延する現象が過去にありました。

**対策:**
1.  **UserData の極小化**: 起動時スクリプトは「パスワード認証許可」「ユーザーパスワード設定」のみに限定し、起動直後から安定してログイン可能な状態を実現しています。
