# 01. ai-learning リポジトリの削除手順

## 目的
不要となった `ai-learning` リポジトリをローカル環境から安全に削除し、必要に応じてリモート環境への対応を行う。

## 前提条件（フェールセーフ機構）
対象ディレクトリ: `/Users/shoheihasegawa/play_ground/ai-learning`
削除という破壊的変更を行う前に、未追跡・未コミットのファイルがないか確認し、すべてコミット＆プッシュして履歴を完全に復元できる状態にする。

## 手順

### 1. 未コミットファイルの保護 (Commit & Push)
```bash
cd /Users/shoheihasegawa/play_ground/ai-learning

# 変更状態の確認
git status

# 未コミットの変更があればすべて追加
git add .

# コミットの作成（変更がなければスキップ可能）
git commit -m "chore: backup before deletion (Phase00)" || true

# リモートへプッシュ（リモートブランチが存在する場合）
git push origin HEAD || true
```

### 2. リモートリポジトリの対応方針
GitHub等ホスティングサービス上で、`ai-learning` リポジトリの対応を行う。
- 削除を推奨: GitHubのリポジトリ設定 (Settings -> General -> Danger Zone) から「Delete this repository」を実行する。
- またはアーカイブ化 (Archive this repository) を行う。

### 3. ローカルリポジトリの削除
リモートでの対応とバックアップ完了を確認後、ローカルディレクトリを完全に削除する。

```bash
# play_ground ディレクトリへ移動
cd /Users/shoheihasegawa/play_ground

# 削除の実行
rm -rf ai-learning
```

### 4. 完了確認
```bash
# 削除されたことを確認する
ls -la | grep ai-learning
```
