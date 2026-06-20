# Harvest Report: Agent-Driven Architecture & Trading System Design
**Date**: 2026-05-29
**Tags**: #Architecture #UX #Trading #AgentOS

## 🧠 抽出された教訓 (Wisdom & Insights)

1. **入力摩擦ゼロの原則（Mobile Obsidianのリードオンリー化）**
   出先での入力にObsidianアプリを使うと「どのテンプレートか？どのフォルダか？」というDecision Fatigue（決断疲れ）が生じる。スマホからの入力はすべて「iOSショートカット等によるテキスト/音声の単一Inboxへの放り込み」に限定し、整理と構造化の責務はすべてPC側のAI（Agent）に委譲するアーキテクチャが最も持続性が高い。
2. **Dumb TransporterとAgentの分離（関心の分離）**
   `mobile_sync` のような同期スクリプトの中にAI処理を組み込んではならない。同期は「単にファイルをPCのDrop Zoneに運ぶだけ（Dumb Transporter）」に徹し、AI（Agent）は独立した常駐プロセスとしてDrop Zoneを監視・処理する構成にすることで、システムが堅牢になる。
3. **トレードにおけるAIの真価（客観的指標 vs 主観的リスク）**
   RCIやBBなどの「客観的指標」の監視はTradingViewのアラートに任せるべきであり、AI（Gemini）に行わせるのはナンセンスである。トレード日誌におけるAIの真価は、ユーザーが入力した「エントリーの根拠（裁量的な背景）」や「リスク・感情」のテキストとチャート画像を照らし合わせ、**「ルール外の感情的エントリーになっていないか」「見落としている上位足のレジスタンスラインはないか」を客観的に指摘するメンター**としての役割にある。

## ⚠️ 認識された技術的負債と未決事項 (Tech Debt / Open Issues)

- **タスクの逆同期問題 (PC ➔ Mobile)**
  PC側のAgentが生成した「今日のタスク」を、スマホ側でどう「完了（チェック）」させるか。iOSリマインダー連携（双方向同期の難易度高）か、スマホ版Obsidianでの閲覧（ワンタップの手間）かの設計が未了。
- **トレードの分割決済（建玉操作）への対応**
  トレード日誌の統合において、単純な「エントリーと決済の1対1」ではなく、「追玉（ピラミッディング）」や「分割決済」に対応できる柔軟な `Trade_ID` とファイル追記・統合の仕組み（DB化）の設計が必要。

## 🚀 次のアクション (Next Actions)

本セッションでの「全体のメタ設計（マスタープラン）」合意を受け、以下の個別プロジェクトを専用セッション（Agent Manager）で立ち上げ、詳細設計と実装に移行する。

1. `Task_and_Calendar_Automation` の立ち上げ（逆同期の検証と実装）
2. `trading-strategy` の立ち上げ（TradingView Pine Scriptの作成と検証、Gemini API自動連携スクリプトの構築）
