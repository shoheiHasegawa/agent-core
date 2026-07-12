# Oracle_Workshop_Handson 進行状況

## 2026-07-12
### 完了した作業 (Linux AMI `251st_LinBase` への移行)
1. **CloudFormation (`ec2-auto-deploy.yaml`) の改修**
   - UserData の PowerShell を Bash に書き換え。
   - `sshd_config` にて PasswordAuthentication を有効化し、`chpasswd` で `ec2-user` に対して共通パスワード（CloudFormation パラメータ `CommonPassword`）をセットする仕組みを実装。
   - AWS EventBridge Scheduler の自動起動時間を `19:00`、自動停止時間を `22:20` に変更。
   - `KeyName` のデフォルト値を `251st_oracle` に更新。
2. **Image Builder パイプラインの移行**
   - Windows用のパイプラインを削除し、Linux用のパッチ適用パイプライン (`imagebuilder-linux-update-ami-pipeline.yaml`) を新規作成。
   - ベースAMIを `251st_LinBase` に設定し、`update-linux/x.x.x` コンポーネントを使用するよう修正（非推奨エラー対応済）。
3. **運用ドキュメントの改修**
   - `DESIGN.md`, `OPERATION.md`, `README.md` を全面的にリライト。Windows・RDPに関する記述を削除し、Linux・SSH接続・共通パスワード運用に関する記述に統一。

### 次のステップ・保留事項
- 次回の勉強会前に、手動でのデプロイテスト（CFnでのテストインスタンス作成）および受講者PCからのSSH接続・共通パスワードログインが想定通りに行えるか最終確認を実施する。
