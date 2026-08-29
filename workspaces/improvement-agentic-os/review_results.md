# Compliance & Global Alignment Review Results

**レビュー対象**: `core-service/src/.../agent_task/` (Phase 5: DDD Refactoring Implementation)
**実施日**: 2026-08-12

## 1. Compliance Reviewer 報告
**Status**: ✅ **PASS (修正完了)**

### 指摘事項と修正内容 (MUST FIX)
1. **Application層へのInfrastructure依存混入**
   - **指摘**: UseCase (`register_task_usecase.py` など) のコンストラクタで、デフォルト引数として `SystemClock`, `SystemUUIDGenerator` を直接インスタンス化しており、DI（依存性注入）の原則および Service-Config パターンに違反している。
   - **修正**: デフォルトの具象クラス（`SystemClock`等）のインスタンス化を完全に削除し、`Clock`, `UUIDGenerator` といったドメインインターフェースのみを要求する形に修正。依存注入を完全に外側へ委譲した。
2. **Infrastructure層へのDomain知識のハードコード**
   - **指摘**: `SqlAgentTaskRepository` 内でステータスが `"PENDING"` のように文字列でハードコードされており、ドメイン層の知識がインフラ層に直接書かれている。
   - **修正**: ドメイン層の `AgentTaskStatus` Enum をインポートし、`AgentTaskStatus.PENDING.value` を利用するように変更。

---

## 2. Global Alignment Reviewer 報告
**Status**: ✅ **APPROVE (条件付き承認)**

### 指摘事項と対応内容
1. **依存関係の逆転違反 (MUST FIX)**
   - **指摘**: Compliance Reviewerと同様、Application層からInfrastructure層への直接参照がある。
   - **修正**: 修正済み。
2. **トランザクション境界の責務漏洩 (MUST FIX ➔ LEVEL 2 負債として受容)**
   - **指摘**: `AgentTaskRepository` の `save()` メソッド内で `session.commit()` が呼ばれている。DDDの原則では、コミット（トランザクション境界）はApplication層（UseCaseやUoW）が制御すべきである。
   - **裁定**: 現状の `core-service` リポジトリ全体の設計（`task_repository.py` 等）において、Application層に UoW パターンが存在せず、全ての Repository が自動コミットを行っている。ここで `agent_task` だけを純粋なDDDに合わせるとシステムの一貫性が破壊され、動作しなくなる。
   - **結論**: `GEMINI.md` の「Triageとリスク評価の原則」に基づき、特例として現状のAuto-commit型Repositoryを **Approve（許可）** する。ただし、システム全体としてのアーキテクチャの歪みであるため、**Level 2 (中程度の負債)** としてBacklogに記録し、将来のMaintenanceモードで解消を図る。

---

## 結論
全ての MUST FIX 項目が修正され、レビューを通過しました。残る「Level 2」の技術的負債については `progress.md` のBacklogに追記し、以後の作業（Phase 6）へ移行します。
