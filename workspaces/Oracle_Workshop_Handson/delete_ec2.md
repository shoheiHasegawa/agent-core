不要になった EC2 インスタンスの確認・削除 手順書

1. 目的

不要になった EC2 インスタンスを 誤削除なく安全に確認・削除 するための標準手順を示す。
本手順は AWS CloudShell + AWS CLI を前提とする。

2. 前提条件

AWS マネジメントコンソールにログイン可能であること

CloudShell を利用できる IAM 権限があること

以下の IAM 権限を保有していること

ec2:DescribeInstances

ec2:ModifyInstanceAttribute

ec2:TerminateInstances

3. 削除前の重要注意事項（必読）

terminated 状態のインスタンスは削除対象外（操作不可）

Auto Scaling Group 配下の EC2 は削除しても再作成される可能性あり

本番環境（prod）は原則削除禁止

削除後は元に戻せない

4. 作業全体の流れ

削除候補インスタンスの一覧確認

InstanceId の取得

終了保護の無効化

インスタンス削除（terminate）

削除結果の確認

5. 削除候補インスタンスの確認

5.1 停止中インスタンス一覧を表示（確認用）

aws ec2 describe-instances \
  --query "Reservations[].Instances[?State.Name=='stopped'].join(': ', [Tags[?Key=='Name'].Value | [0], InstanceId])" \
  --output text

確認ポイント：

Name タグが想定通りか

本番・重要インスタンスが含まれていないか

5.2 Name タグで絞り込み（例：241st を含む）

aws ec2 describe-instances \
  --query "Reservations[].Instances[?State.Name=='stopped' && contains(Tags[?Key=='Name'].Value | [0], '241st')].join(': ', [Tags[?Key=='Name'].Value | [0], InstanceId])" \
  --output text

6. InstanceId の取得

INSTANCE_IDS=$(aws ec2 describe-instances \
  --query "Reservations[].Instances[?State.Name=='stopped' && contains(Tags[?Key=='Name'].Value | [0], '241st')].InstanceId" \
  --output text)

echo "$INSTANCE_IDS"

InstanceId が想定通りであることを再確認する。

7. 終了保護の無効化

for id in $INSTANCE_IDS
do
  echo "Disable termination protection: $id"
  aws ec2 modify-instance-attribute \
    --instance-id $id \
    --no-disable-api-termination
done

8. インスタンス削除（terminate）

⚠️ 本手順以降は取り消し不可

aws ec2 terminate-instances --instance-ids $INSTANCE_IDS

9. 削除結果の確認

aws ec2 describe-instances \
  --instance-ids $INSTANCE_IDS \
  --query "Reservations[].Instances[].State.Name" \
  --output text

以下の状態になっていれば削除完了：

shutting-down

terminated

10. よくあるエラーと対処

エラー

原因

対処

IncorrectInstanceState

terminated を含めている

状態で絞り込む

UnauthorizedOperation

IAM 権限不足

権限付与

再作成される

ASG 配下

ASG 側を確認

11. 推奨運用ルール

削除前に必ず 一覧表示 → 目視確認 を行う

タグ（Env / Name）で必ず絞り込む

本番環境は二重承認とする

12. 参考

AWS EC2 CLI Documentation

社内 AWS 運用ルール