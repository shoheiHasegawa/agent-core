# Repository Migration Plan (同名リポジトリ衝突の解消と移行手順)

最新のアーキテクチャ設計により、新たな知識体系の器となるリポジトリ名称が **`second-brain`** と決定した。これにより、現在稼働している旧リポジトリ（`play_ground/second-brain`）と**名前が完全に衝突**している。
本ドキュメントは、この問題を解決し、安全かつ段階的に新アーキテクチャ（You, Inc. のオーケストレーション層）へと移行するための具体的な手順を定義する。

## 1. 移行戦略：Legacy退避とParallel Build

名前の衝突を回避するため、現在の `second-brain` を「過去の遺産（Legacy）」として隔離し、新たなオーケストレーション層の元で新しい `second-brain`（新知識ベース）を立ち上げる。

### Step 1: 旧リポジトリの「退避・リネーム」 (Pre-Migration)
1. **GitHub上でのリネーム**: GitHubの画面から旧 `second-brain` リポジトリを `second-brain-legacy` にリネームする。
2. **ローカルでのリネームと追従**:
   - 現在のディレクトリ `/Users/shoheihasegawa/play_ground/second-brain` を `/Users/shoheihasegawa/play_ground/second-brain-legacy` に名称変更する。
   - リポジトリの `git remote set-url origin` を実行し、新しいURLに追従させる。

### Step 2: 3つの新コンポーネントリポジトリの作成
GitHub上で、決定した3本柱の空リポジトリを新規作成する。
- `agent-core` (旧 you-inc-hq)
- `second-brain` (新知識ベース、旧 knowledge-vault)
- `core-service` (旧 you-inc-core)

### Step 3: オーケストレーション層（会社）の初期化とクローン
`play_ground/` 直下（または `You_Inc/`）に「会社」の論理ディレクトリとして、3つのリポジトリをフラットに配置（クローン）する。

```text
/Users/shoheihasegawa/play_ground/You_Inc/ (または play_ground/ トップディレクトリ)
├── agent-core/       <-- [Clone: agent-core]
├── second-brain/     <-- [Clone: 新 second-brain]
└── core-service/     <-- [Clone: core-service]
```

### Step 4: データ移行とクレンジング (Parallel Build)
旧環境（`second-brain-legacy`）をReadOnlyの参照元とし、新環境へデータを移行していく。
- 進行中のプロジェクトは、`agent-core/workspaces/` 配下に移動して継続する。
- Zettelkastenやルール、決定事項などの「残すべき知識」は、フォーマットをクレンジングしながら新 `second-brain` の適切なディレクトリ（`10_Areas/`, `40_Zettelkasten/` 等）にコピーする。

### Step 5: 旧リポジトリのアーカイブ (Decommission)
移行が完全に終わり、不要なデータだけが残った段階で、`second-brain-legacy` をGitHub上でArchive（読み取り専用）に設定し、ローカルから削除する。
