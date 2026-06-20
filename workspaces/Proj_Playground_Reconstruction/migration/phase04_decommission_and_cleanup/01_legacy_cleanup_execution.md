# Phase 04: Legacy Cleanup Execution (旧環境のアーカイブとクリーンアップ)

## 概要
本タスクは、旧環境で不要となったデータ、ログ、テンポラリファイルを安全にアーカイブ・削除し、移行後のディスクスペースを確保すると共にシステムを最終形態に向けて身軽にすることを目的とする。

## ⚠️ 前提条件 (フェールセーフ厳守)
一括削除などの破壊的操作を行うため、**必ず事前に現在の変更をコミットし、可能であればプッシュした状態**にすること。未追跡（Untracked）データがないことを事前に確認する。

## 作業手順（チェックリスト）

- [ ] **1. 現在のGitステータス確認とバックアップコミット**
  ```bash
  git status
  git add .
  git commit -m "chore: backup before legacy cleanup" || true
  ```
- [ ] **2. `life-automation-legacy` および `daily-tools-legacy` の削除**
- [ ] 念のため完全なソースコードのバックアップ（アーカイブ）を作成した上で、削除を実行する。
- [ ] ※アーカイブファイルは `You_Inc/40_Archives/` などの安全な場所に保管する前提。
  ```bash
  set -e
  cd /Users/shoheihasegawa/play_ground || exit 1

  # アーカイブの作成に成功した場合のみ、ディレクトリを削除する (Fail-safe)
  tar -czvf ./migration_archives/life-automation-legacy_backup.tar.gz ./life-automation-legacy/ && \
  rm -rf ./life-automation-legacy/

  tar -czvf ./migration_archives/daily-tools-legacy_backup.tar.gz ./daily-tools-legacy/ && \
  rm -rf ./daily-tools-legacy/
  ```
- [ ] **3. 不要ログ・テンポラリファイルの削除**
  ```bash
  set -e
  cd /Users/shoheihasegawa/play_ground || exit 1
  find . -name "*.log" -type f -delete
  find . -name ".DS_Store" -type f -delete
  rm -rf ./tmp/* ./build/* ./.cache/* || true
  ```
- [ ] **4. アーカイブ化完了後の旧ファイル削除**
  ```bash
  # アーカイブの作成が確認できた場合のみ実行
  cd /Users/shoheihasegawa/play_ground || exit 1
  rm -rf ./second-brain-legacy/
  ```
- [ ] **5. クリーンアップ結果のコミット**
  ```bash
  git add .
  git commit -m "chore: complete legacy cleanup and archiving"
  ```
