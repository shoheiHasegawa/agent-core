# Phase 04: Root Workspace Finalization (You_Incルートディレクトリへの階層整理)

## 概要
本タスクは、`You_Inc` をワークスペースの絶対的なルートディレクトリとして確立し、各ドメインをその配下に統合・整理する最終作業である。

## ⚠️ 前提条件 (フェールセーフ厳守)
大規模なファイル移動・ディレクトリ再構築を行うため、現在の状態がすべてGitで復元可能な状態であることを前提とする。

## 作業手順（チェックリスト）

- [ ] **1. You_Inc 環境の初期化・設定**
  （※ You_Inc自体のクローンと agent-core 化は Phase 01 で完了している想定）
  ```bash
  cd You_Inc
  # ルートドキュメントの配置
  echo "# You_Inc Workspace" > README.md
  
  # グローバルな .gitignore の統合設定
  echo ".DS_Store" > .gitignore
  echo "archives/" >> .gitignore
  ```
- [ ] **2. 古いルートファイル（play_ground直下）の破棄**
  Phase 01で作成したリンクや、古いメタファイルを削除する。
- [ ] **3. 一発切り替え前の安全検証 (Diff/Tree Check)**
  旧リポジトリを完全に削除する前に、`second-brain` 等の重要なファイル群が `You_Inc` 側に欠損なく移行できているか、`diff` コマンドや `tree` コマンドで機械的に検証を行う。

- [ ] **4. Gitリポジトリ履歴の全破棄と再初期化 (グランドゼロ)**
  旧 `second-brain` 等が持っていた過去のコミット履歴はすべて破棄し、`You_Inc` 全体を単一のクリーンなリポジトリとして再スタートする。
  **ただし、知識ベースの文脈喪失を防ぐため、事前にベアリポジトリとして完全なGit履歴をアーカイブ退避する。**
  ```bash
  set -e
  cd /Users/shoheihasegawa/play_ground/You_Inc || exit 1
  
  # 旧リポジトリの .git をベアアーカイブとして退避 (参照専用)
  mkdir -p ./40_Archives/git_backups
  tar -czvf ./40_Archives/git_backups/second-brain_git_history.tar.gz -C ./second-brain .git
  
  # サブディレクトリ内に残っている .git フォルダをすべて削除
  find . -name ".git" -type d -exec rm -rf {} +
  
  # You_Inc をルートとして新たにGitリポジトリを初期化
  git init
  git add .
  git commit -m "feat: initialize You_Inc root workspace (Grand Zero)"
  ```
