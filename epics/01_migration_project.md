---
type: epic
status: in_progress
created: "2026-06-20T14:00:00Z"
tags: [migration, you_inc]
---

# Epic: Playground Reconstruction (You_Inc 移行プロジェクト)

## コンテキスト
旧環境（`-legacy`）から、新アーキテクチャ3本柱（`agent-core`, `core-service`, `second-brain`）への完全移行を行う。
このエピックは、移行完了まで最優先で取り組むべきマスタープロジェクトである。

## マスタープラン（参照先）
移行の全体計画とフェーズ定義は、現在レガシー環境にある以下のファイルを参照すること。
👉 `second-brain-legacy/10_Projects/Proj_Playground_Reconstruction/migration/00_master_plan.md`

## 進行状況
- [x] **Phase 00: 移行前準備** (完了済: ai-learning削除, レガシーリネーム)
- [x] **Phase 01: TO-BE基盤の初期実装** (完了済: agent-core, core-service, second-brainのスケルトン構築とGit Push)
- [x] **Phase 01.5: 移行体制のブートストラップ** (完了済: 本エピックの登録とGEMINI/AGENT整備によるAgent-coreへの引き継ぎ)
- [ ] **Phase 02: 移行対象の分析と仕分け決定** (👈 Next)
- [ ] **Phase 03: 実装の移植と並行稼働**
- [ ] **Phase 04: 旧環境の廃止とクリーンアップ**
- [ ] **Phase 05: 稼働後の非同期クレンジング**

## 次のアクション (Next Action)
マスタープランの「Phase 02」を読み込み、対象コード群の分析やResearch Agentの起動などの具体的なステップをユーザーに提案・実行する。
