# 勉強会環境 構築手順書 (OPERATION.md)

本ドキュメントでは、勉強会開催時に受講者用 EC2 インスタンス環境を構築・配布・撤収する際の手順について説明します。

## 1. 事前準備 (Prerequisites)

作業を行う端末 (CloudShell 推奨) で以下の準備が整っていることを確認してください。

*   AWS マネジメントコンソールへのアクセス権限
*   `AdministratorAccess` または CloudFormation および EC2 フル操作権限を持つ IAM ユーザー/ロール
*   AWS CLI が実行可能であること
*   **(推奨) 保険用キーペア (`Oracle-workshop-common-key-pair`) の秘密鍵 (.pem) を所持していること**
    *   通常運用では使用しませんが、トラブル時の調査用として重要です。

## 2. 構築フロー

### Step 1: 最新 AMI の確認・変数セット

以下のコマンドを実行して、最新の AMI ID を環境変数 `AMI_ID` にセットします。

```bash
# AMI名を "HandsOnBase-Lin-" で検索し、作成日順にソートして最新の1つを取得
export AMI_ID=$(aws ec2 describe-images \
  --owners self \
  --filters "Name=name,Values=HandsOnBase-Lin-*" \
  --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
  --output text)

# 確認
echo "使用するAMI ID: $AMI_ID"
```

出力された ID が正しいか（空欄でないか）確認してください。

### Step 2: パラメータ準備 (参加者リスト & 共通パスワード)

CloudFormation スタックに渡す参加者リスト (`TagList`) と、**全インスタンス共通の管理者パスワード** (`COMMON_PASS`) を準備します。

```bash
# 参加者リスト (スプレッドシートから貼り付けOK)
TAG_LIST="24下期_1742_長谷川
24下期_1833_鈴木
24下期_1201_加藤"

# 共通パスワード (複雑なパスワードを設定してください)
# 例: Oracle_Workshop_2026!
COMMON_PASS="Oracle_Workshop_2026!"

# 確認
echo "$TAG_LIST"
echo "Password: $COMMON_PASS"
```

### Step 3: 環境構築（CloudFormation スタック作成）

準備した変数を使ってスタックを作成します。
**インスタンス台数はリストの行数から自動判定されます。**

```bash
# スタック作成 (デプロイ)
# KeyName はデフォルトで 'Oracle-workshop-common-key-pair' が使用されます
aws cloudformation deploy \
  --template-file ec2-auto-deploy.yaml \
  --stack-name hands-on-ec2-stack \
  --parameter-overrides \
      AmiId=$AMI_ID \
      TagList="$TAG_LIST" \
      CommonPassword="$COMMON_PASS" \
  --capabilities CAPABILITY_IAM
```

実行後、`Successfully created/updated stack - hands-on-ec2-stack` と表示されれば完了です。

### Step 4: 動作確認

起動したインスタンスが正常に稼働しているか確認します。
(最適化により再起動が不要になったため、**約1〜2分** でログイン可能になります)

```bash
# 起動したインスタンスとNameタグの一覧を表示
aws ec2 describe-instances \
  --filters "Name=tag:aws:cloudformation:stack-name,Values=hands-on-ec2-stack" \
  --query "Reservations[].Instances[].{InstanceId:InstanceId, Name:Tags[?Key=='Name'].Value|[0], State:State.Name, PublicIP:PublicIpAddress}" \
  --output table
  --output table
```




### Step 5: SSH接続 & Oracle インストール

各受講者に割り当てられた Public IP アドレスと、**Step 2 で設定した共通パスワード**を伝えます。

*   **ユーザー名**: `ec2-user`
*   **パスワード**: (設定した共通パスワード)

受講者はこの情報を使って SSH 接続し、Oracle Database のインストール作業を実施します。

> [!NOTE]
> もし共通パスワードでログインできない場合は、数分待ってから再試行してください。
> それでもログインできない場合は、保険用キーペア (`Oracle-workshop-common-key-pair`) を使用して標準のランダムパスワードを取得してログインしてください。

### Step 6: インスタンスの一括停止 (受講開始前の待機)

デプロイと動作検証 (Step 4, 5) が完了し、本番まで期間が空く場合は、課金を抑えるためにインスタンスを一括停止します。
CloudShell で以下のコマンドを実行してください。

```bash
# ---------------------------------------------------------
# 1. 停止対象の検索パターンを指定 (★ここを都度変更する)
# ---------------------------------------------------------
# ワイルドカード(*)を使って、特定のプレフィックスを持つインスタンスを指定します
# 例: "24下期_1742_name" の形式なら "24下期_1742_*" と指定
TARGET_PATTERN="24下期_*"

# 2. 対象インスタンスのIDを取得 (Running状態のもの限定)
IDS=$(aws ec2 describe-instances \
    --filters "Name=tag:Name,Values=${TARGET_PATTERN}" "Name=instance-state-name,Values=running" \
    --query "Reservations[].Instances[].InstanceId" \
    --output text)

# 3. 停止コマンド実行
if [ -n "$IDS" ]; then
    echo "停止対象: $IDS"
    aws ec2 stop-instances --instance-ids $IDS
    echo "停止リクエストを送信しました。"
else
    echo "対象のインスタンスが見つかりません (既に停止済みか、名前が一致しません)"
fi
```

### Step 7: 受講開始時の起動
当日になったら、AWSコンソールから対象のインスタンスを選択して「インスタンスを開始」してください。

### Step 8: 後片付け (インスタンス削除)

勉強会終了後、不要になったインスタンスを削除します。
**重要**: 基本的に CloudFormation スタック (`hands-on-ec2-stack`) は **削除せず、次回開催時に再利用します。** ここでは **EC2 インスタンスのみ** をコマンドで削除します。

CloudShell で以下のコマンドを実行してください。

```bash
# ---------------------------------------------------------
# 1. 削除対象の検索パターンを指定 (★慎重に設定してください)
# ---------------------------------------------------------
TARGET_PATTERN="24下期_1742_*"

# 2. 対象インスタンスのIDを取得 (停止中・起動中 問わず全て)
# ※ 安全のため terminated 済みは除外
IDS=$(aws ec2 describe-instances \
    --filters "Name=tag:Name,Values=${TARGET_PATTERN}" "Name=instance-state-name,Values=running,stopped" \
    --query "Reservations[].Instances[].InstanceId" \
    --output text)

# 3. 削除コマンド実行 (Terminate)
if [ -n "$IDS" ]; then
    echo "削除対象: $IDS"
    echo "これらのインスタンスを削除(Terminate)します。よろしいですか？"
    read -p "Enter 'yes' to proceed: " CONFIRM
    if [ "$CONFIRM" = "yes" ]; then
        aws ec2 terminate-instances --instance-ids $IDS
        echo "削除リクエストを送信しました。"
    else
        echo "キャンセルしました。"
    fi
else
    echo "対象のインスタンスが見つかりません。"
fi
```

### Step 9: 次回開催時の手順 (環境の再デプロイ)

次回、別の参加者向けに環境を構築する場合は、以下の手順でスタックを **更新** します。

1.  **Step 2** の `TAG_LIST` 変数を、新しい参加者リストで上書き定義します。
    ```bash
    TAG_LIST="25上期_001_新しい参加者A
    25上期_002_新しい参加者B"
    ```
2.  **Step 3** の `aws cloudformation deploy` コマンドを再度実行します。
    *   CloudFormation が変更を検知し、Lambda が再実行され、**新しいリストの分のインスタンスだけが新規起動** します。

## 3. トラブルシューティング

#### Q. 秘密鍵 (pemファイル) を紛失してしまった / 取得できない
AWS の仕様上、**一度作成した・ダウンロードした秘密鍵 (.pem) を再ダウンロードすることはできません。**
もし秘密鍵が見つからない場合は、以下の手順で新しいキーペアを作成し、環境を再構築してください。

1.  **新しいキーペアの作成**:
    *   AWS コンソールの **EC2** -> **キーペア** -> **キーペアを作成** をクリック。
    *   名前を入力 (例: `oracle_workshop_2026`) し、形式は `.pem` を選択して作成。
    *   **自動的にダウンロードされる `.pem` ファイルを大切に保管してください。**

2.  **スタックの更新 (新しいキーを使用)**:
    *   `ec2-auto-deploy.yaml` のデフォルト値を書き換えるか、デプロイコマンドのパラメータで新しいキー名を指定して実行します。

3.  **インスタンスの入れ替え**:
    *   スタック更新後、一度スタックを削除 (`aws cloudformation delete-stack ...`) してから、再度作成 (`deploy`) を行うことで、新しいキーペアを持ったインスタンスが起動します。

#### Q. 元のインスタンスではログインできたのに、Image Builder 経由だとログインできない
Image Builder は、AMI 作成の最終工程で **Sysprep** (システム準備ツール) を実行します。
これにより、**Administrator アカウントのパスワードはリセットされ、次回起動時にランダムなパスワードが生成されます。**
そのため、元のインスタンスと同じパスワードを使い続けることはできません。必ずキーペアを使用して、新しく生成されたランダムパスワードを取得してください。

**参考**: AWSコンソールから手動で「イメージを作成」した場合などは、Sysprepを行わない限りパスワードは維持されますが、Image Builderを使用する場合は、クリーンなイメージを作成するためにこのプロセスが必須となります。

#### Q. 共通パスワードが設定されない (UserData が動いていない気がする)
共通パスワードが反映されず、`C:\userdata_log.txt` も作成されていない場合、UserData 自体が実行されていない可能性があります。
以下の手順で「Windows が実際に何を受け取ったか」を確認してください。

1.  **SSH 接続**: 保険用キーペアを使って ec2-user でログインします。
2.  **コマンド実行**: 以下のコマンドで、インスタンスメタデータから UserData を取得します。
    ```bash
    curl http://169.254.169.254/latest/user-data
    ```
3.  **結果の診断**:
    *   **正常**: `<powershell>...</powershell>` で囲まれたスクリプトが表示される。
        *   → スクリプトの内容（コマンドミスなど）を疑ってください。実行ログ `C:\ProgramData\Amazon\EC2Launch\log\agent.log` (または `UserdataExecution.log`) を確認します。
    *   **異常 (二重エンコード)**: ランダムな英数字の羅列 (Base64文字列) が表示される。
        *   → CloudFormation テンプレート側で過剰なエンコードが行われている可能性があります。
    *   **異常 (空)**: 何も表示されない。
        *   → パラメータの渡し方が間違っています。



#### Q. コマンドプロンプト (sqlplus) で日本語が文字化けする
Windows のコマンドプロンプト環境では、文字コード (Shift-JIS) とフォント設定の組み合わせにより、頻繁に文字化けが発生します。
トラブル防止のため、**勉強会では英語メッセージ設定で統一することを推奨します。**

SQL*Plus を実行する前に、以下のコマンドを実行してください。

```cmd
set NLS_LANG=AMERICAN_AMERICA.JA16SJIS
sqlplus / as sysdba
```
```cmd
set NLS_LANG=AMERICAN_AMERICA.JA16SJIS
sqlplus / as sysdba
```
※ これによりメッセージが英語 (例: `Connected to an idle instance.`) になり、文字化けを確実に回避できます。

#### Q. インスタンス一覧 (Name, PublicIP) をCSV形式で取得したい
受講者に配布する際など、インスタンス情報をリスト化してダウンロードしたい場合は、以下のコマンドを実行してください。

```bash
# 1. 検索パターンを指定
TARGET_PATTERN="24下期_*"

# 2. CSVファイルに出力 (Name, PublicIp)
# ※ 停止中のインスタンスは PublicIp が None となります
# ※ 削除済み (terminated) のインスタンスは除外します
aws ec2 describe-instances \
    --filters "Name=tag:Name,Values=${TARGET_PATTERN}" "Name=instance-state-name,Values=running,stopped,pending,stopping" \
    --query "Reservations[].Instances[].[Tags[?Key=='Name'].Value|[0], PublicIpAddress]" \
    --output text | sed 's/\t/,/g' > instance_list.csv

# 3. 内容確認
cat instance_list.csv
```

**ファイルのダウンロード方法 (CloudShell):**
1.  画面右上の **「Actions」** メニューをクリック
2.  **「Download file」** を選択
3.  File path に `instance_list.csv` と入力して **「Download」** をクリック





