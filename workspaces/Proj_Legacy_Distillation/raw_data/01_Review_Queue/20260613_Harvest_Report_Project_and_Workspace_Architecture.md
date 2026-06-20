# Harvest Report: Projectのライフサイクル再定義とコンテキストエンジニアリング

**Date**: 2026-06-13
**Context**: 新アーキテクチャ「You, Inc.」における `10_Projects` のあり方に関する議論。DDD/SOLID原則およびLLMのコンテキストエンジニアリングの観点から、アーキテクチャの抜本的なピアレビューを実施し、セッションをクローズした。

## 1. Wisdom (セッションから得られた普遍的教訓)
*   **状態と知識の分離 (Decoupling State and Knowledge)**: 「実行のトランザクション（状態）」と「普遍的な教訓（知識）」を同一のリポジトリに置くことはGod Object化を招く。プロジェクトという「一時作業場」は実行層（HQ）へ、抽出された知識だけを保管庫（Vault）へ分離することがAgent駆動設計の基本である。
*   **Teardownの不可逆性とGrace Period**: 不要なログを削除することはコンテキスト最適化に必須だが、「直後の完全削除」はFact-Grounding（事実の検証）を不可能にするアンチパターンである。Sense-Makingが完了するまでの「Cold Storage（Grace Period）」というフェールセーフ機構が不可欠である。
*   **Amnesia Loop（健忘症ループ）の抑止**: Agentのコンテキスト節約のために過去ログを上書き消去させる場合、必ず「なぜ失敗したか（Why NOT）」を別のコンテキストファイル（`decisions.md`）に移譲させないと、別のAgentが同じ失敗を繰り返す。

## 2. Tech Debt (解消すべき技術的負債)
*   **既存 `10_Projects` の解体**: 現在 `knowledge-vault` (旧 second-brain) 内に残存している既存プロジェクト群を、新ルールに基づく `you-inc-hq` 側の一時Workspaceへとマイグレーション（トリアージ・移行）する必要がある。

## 3. System Improvement Proposals (システム改善案)
1.  **Sense-Makingの独立**: レビュー待ちキューを単なる Inbox の一部ではなく、`knowledge-vault` トップレベルの `01_Sense_Making/`（醸造室）として新設する。
2.  **WIP制限の導入**: ユーザーのレビュー（Sense-Making）が追いつかないことによる破綻を防ぐため、未処理キューが一定数を超えたら新規Workspaceの立ち上げをブロックするAgentルールを実装する。

---
*Generated autonomously by AntiGravity Agent based on Global Constitution Rule 8.*
