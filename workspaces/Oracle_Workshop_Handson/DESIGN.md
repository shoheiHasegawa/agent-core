# 勉強会用 EC2 自動構築の仕組み (DESIGN.md)

本ドキュメントでは、Oracle 勉強会で使用する受講者用 EC2 インスタンスを自動構築する仕組み、およびそのアーキテクチャについて解説します。

## 1. アーキテクチャ概要

本システムは **AWS Image Builder** による AMI の定期自動生成と、**CloudFormation (CFn) + Lambda** による EC2 インスタンスの一括作成によって構成されています。

```mermaid
graph TD
    subgraph "Phase 1: AMI Creation (Scheduled)"
        IB[AWS Image Builder] -->|Schedule: Jan 1st / Jul 1st| UpdatedAMI[Windows Update Applied AMI]
        UpdatedAMI -->|Named| AMIName[HandsOnBase-Win-YYYY-MM-DD]
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

Windows Update を手動で適用する工数を削減するため、AWS Image Builder を使用して定期的に「最新の Windows Update が適用された AMI」を自動生成します。

*   **役割**: ベースとなる Windows Server AMI に `update-windows` コンポーネントおよび**日本語化設定（タイムゾーン、キーボード配列、ロケール用 `unattend.xml`）**を適用し、新しい AMI を作成する。
*   **実行スケジュール**: 毎年 **1月1日** および **7月1日** の 00:00 (JST) に自動実行されます。
*   **成果物 (AMI)**: 生成された AMI は `HandsOnBase-Win-{{imagebuilder:buildDate}}` という命名規則で保存されます。
*   **構成ファイル**: `imagebuilder-windows-update-ami-pipeline.yaml`
*   **適用される設定 (OOBE適用)**:
    *   **TimeZone**: UTC+9:00 (Tokyo Standard Time)
    *   **Keyboard**: Japanese (106/109 Key)
    *   **Locale/Language**: ja-JP (Display Language: Japanese)
    *   ※ `unattend.xml` を使用して Sysprep 後の初期セットアップ時に自動適用されます。

### 2.2 CloudFormation + Lambda (EC2 一括起動)

通常の CloudFormation の `AWS::EC2::Instance` リソースでは、「動的な回数の繰り返し作成」や「CSV リストに基づく一意な Name タグ付け」が難しいため、Custom Resource として Lambda 関数を使用しています。

*   **役割**: 指定された AMI とパラメータを使用して、参加者人数分の EC2 インスタンスを一括で起動する。
*   **ロジック**:
    1.  CFn パラメータとして `TagList` (参加者リスト) と `CommonPassword` (共通パスワード) を受け取る。
    2.  Lambda 内で `TagList` を解析し、インスタンス数を決定する。
    3.  **UserData (起動スクリプト)** を生成し、起動時に `net user Administrator "パスワード"` を実行させることで、全インスタンスのパスワードを統一する。
    4.  保険としてキーペア (`Oracle-workshop-common-key-pair`) も付与して起動する。
    5.  起動した InstanceId のリストを CloudFormation の Outputs に返却する。
*   **構成ファイル**: `ec2-auto-deploy.yaml`

### 2.3 制限事項 (Limits)

本システムには一度に作成できるインスタンス数に以下の制限があります。

*   **Lambda タイムアウト**:
    *   カスタムリソース Lambda のタイムアウトは **60秒** に設定されています。
    *   API 実行時間を考慮すると、**約 50 台** 程度までが安全圏です。これを超える場合は、複数回に分けてスタックを作成するか、テンプレートのタイムアウト値を変更してください。
*   **パラメータサイズ制限**:
    *   CloudFormation のパラメータ (`TagList`) は最大 **4096 バイト** です。
    *   日本語文字を含むタグ名の場合、**約 100 行** 程度が上限となります。
*   **AWS vCPU サービスクォータ**:
    *   AWS アカウントごとのリージョン別 vCPU 上限に依存します（t系インスタンスなど）。不足時は上限緩和申請が必要です。

## 3. 採用理由とメリット

*   **省力化**: Windows Update の適用時間は長く、手動で行うと数時間かかります。これを自動化することで準備時間を大幅に削減しています。
*   **ミス防止**: 数十台のインスタンスを手動で起動し、一つ一つにタグを付ける作業はミスが発生しやすいですが、スクリプト化することで正確に展開できます。
*   **コスト管理**: 勉強会ごとに環境を使い捨てる（Create & Delete）運用を前提としており、不要なリソースの課金を防ぎます。

## 4. 技術的な考慮事項とハマりどころ (Technical Insights)

### UserData のエンコーディング問題 (Double Encoding)
`boto3` (Python SDK) を使用して `run_instances` API を呼び出す際、`UserData` パラメータの挙動には注意が必要です。

*   **現象**: Lambda 内でスクリプトを手動で Base64 エンコードしてから API に渡すと、AWS SDK またはサービス側でさらに自動エンコードが行われ、インスタンスには **Base64 文字列そのもの** が渡されてしまう（二重エンコード状態）。
*   **結果**: Windows は受け取ったデータを PowerShell スクリプト (`<powershell>...`) ではなく単なる文字列として認識し、実行をスキップする（ログには `<powershell> tag was not provided` と記録される）。
*   **対策**: `ec2-auto-deploy.yaml` 内の Lambda コードでは、**UserData を生の文字列（PlainText）のまま** `run_instances` に渡しています。

### Windows EC2Launch の仕様 (v1 vs v2)
Windows Server AMI に含まれる起動エージェント (EC2Launch) は、バージョンによって挙動が異なります。

### Windows の日本語化とキーボード設定の自動化
Windows Server の英語 AMI を日本語化し、かつキーボード配列を正しく認識させるためには、以下の設定変更が**全て**必要です。

*   **タイムゾーン (TimeZone)**: PowerShell の `Set-TimeZone -Id "Tokyo Standard Time"` で変更可能です。
*   **ロケーションと入力言語 (Location & Language List)**: 【重要】レジストリ設定だけでは、IME が「英語 (米国)」キーボードを保持し続ける場合があります。以下のコマンドで日本設定を強制する必要があります。
    *   `Set-WinHomeLocation -GeoId 122` (日本)
    *   `Set-WinUserLanguageList -LanguageList ja-JP -Force` (日本語のみをリストに設定)
*   **キーボード配列 (Keyboard Layout)**: ハードウェアドライバレベルで日本語配列 (106/109) を強制するため、レジストリ (`HKLM:\SYSTEM\CurrentControlSet\Services\i8042prt\Parameters`) を変更します。英語配列 (101/102) から日本語配列 (106/109) に強制するためには、以下の値を設定します。
    *   `LayerDriver JPN`: `kbd106.dll`
    *   `OverrideKeyboardIdentifier`: `PCAT_106KEY`
    *   `OverrideKeyboardType`: `7`
    *   `OverrideKeyboardSubtype`: `2`
*   **表示言語 (Display Language)**: 言語パックのインストールが必要です。AWS Image Builder コンポーネント内で言語パックをインストールします。


### 日本語環境の永続化と System Locale (ACP) 問題 (2025/01 Updated)
Windows の Sysprep (一般化) 処理は、インスタンス固有情報を削除する過程で、タイムゾーンやシステムロケールの一部設定をデフォルトに戻す仕様があります。
特に **Active Code Page (ACP)** が `932` (Shift-JIS) から `1252` (Latin-1) に戻ってしまうと、Oracle Database インストーラが正常に動作しません。

*   **旧仕様 (Legacy)**: 起動時に UserData でロケールを変更し、再起動する方式をとっていました。しかし、これは起動時間の遅延と不安定さの原因となっていました。
*   **新仕様 (Current)**: **`unattend.xml` (応答ファイル)** を Image Builder 内で生成し、`C:\Windows\Panther\` に配置しています。これにより、Sysprep 後の OOBE フェーズで Windows が自動的に日本語設定（ACP 932含む）を読み込むため、**起動時の再起動は不要**となりました。

### 大規模展開時のリソース競合と起動の高速化 (2025/01 Update)
`t3.small` インスタンスで一度に多数（40台以上）のインスタンスを起動すると、Windows Update後の初回起動処理やSysprep明けの初期化がCPUリソースを奪い合い、UserDataスクリプトの実行が不安定になる（タイムアウトや失敗が発生する）現象が確認されました。

**対策:**
1.  **日本語化の「焼き込み」 (Bake-in)**: 上記の通り `unattend.xml` を活用し、起動時の処理負荷を排除しました。
2.  **UserData の極小化**: 起動時スクリプトは「パスワード設定」「ユーザー作成」のみに限定し、起動直後から安定してログイン可能な状態を実現しています。


