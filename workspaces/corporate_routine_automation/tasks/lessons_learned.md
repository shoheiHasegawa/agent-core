# Lessons Learned: Corporate Routine Automation

## 🧠 学びと反省（Failure Patterns & Insights）
- **定常業務自動化のROI**: 社長が毎月行う「月末勤怠表提出」「Udemy受講レポート送信」「ABC目標提出」といった定常作業は、小粒に見えて社長のコンテキストスイッチコストを大きく奪う。これを1コマンドまたは自動バッチ化することのROIは極めて高い。
- **SoRの境界**: 個人のタスク・リマインダー（Google Calendar/Tasks）と、会社の業務CLIツール（`core-service`）の責務を混同せず、ツールはステートレスに実行できるCLIとして構築する。
