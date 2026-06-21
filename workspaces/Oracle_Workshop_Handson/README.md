# Oracle Workshop — EC2 ハンズオン環境自動構築

勉強会向けに EC2 ハンズオン環境を自動構築・管理するためのツールセット。
Image Builder による AMI の定期更新と、CloudFormation による一括 EC2 起動を組み合わせて運用工数を削減。

## ドキュメント

| ドキュメント | 内容 |
| :--- | :--- |
| [DESIGN.md](DESIGN.md) | アーキテクチャ、Image Builder / CloudFormation の構成 |
| [OPERATION.md](OPERATION.md) | 当日の環境構築手順 |
| [delete_ec2.md](delete_ec2.md) | 終了後の EC2 削除手順 |

## 構成ファイル

- `ec2-auto-deploy.yaml` — EC2 一括起動用 CloudFormation テンプレート
- `imagebuilder-windows-update-ami-pipeline.yaml` — AMI 自動生成パイプライン

> **プロジェクトノート**: [second-brain/Oracle_Workshop_Infra](../../second-brain/10_Projects/Development/Oracle_Workshop_Infra/)
