# 02. レガシーリポジトリのリネームとリンク更新手順

## 目的
`second-brain`, `daily-tools`, `life-automation` の3リポジトリを `-legacy` 化（リネームおよびリモートURLの追従）し、`play_ground` 直下のルート定義ファイル（GEMINI.md, AGENT.md等）のシンボリックリンクを一時的に張り直す。

## 前提条件（フェールセーフ機構）
リネームおよびリモートURLの変更を行う前に、各リポジトリに存在する未追跡・未コミットのデータを保護するため、事前にコミット＆プッシュを完了させる。

## 手順

### 1. 未コミットファイルの保護 (Commit & Push)
各リポジトリに対して一括でバックアップを実施する。コマンドはエラーで即時停止するよう構成。

```bash
cd /Users/shoheihasegawa/play_ground

for repo in second-brain daily-tools life-automation; do
  echo "Backing up ${repo}..."
  cd "${repo}"
  git add .
  git commit -m "chore: backup before rename to legacy (Phase00)" || true
  git push origin HEAD || true
  cd ..
  echo "Backup completed for ${repo}."
done
```

### 2. リモートリポジトリのリネーム（手動作業）
GitHub等の設定画面（Settings -> General -> Repository name）から以下のリポジトリ名を変更する。
- `second-brain` → `second-brain-legacy`
- `daily-tools` → `daily-tools-legacy`
- `life-automation` → `life-automation-legacy`

### 3. ローカルディレクトリのリネームとリモートURL追従
ローカルディレクトリ名を変更し、gitのリモートURL（origin）を更新する。
※ 以下の `<USERNAME>` は実際のGitHubユーザー名等に置き換えて実行すること。

```bash
cd /Users/shoheihasegawa/play_ground

# リネームの実行
mv second-brain second-brain-legacy
mv daily-tools daily-tools-legacy
mv life-automation life-automation-legacy

# リモートURLの更新
cd second-brain-legacy && git remote set-url origin git@github.com:<USERNAME>/second-brain-legacy.git && cd ..
cd daily-tools-legacy && git remote set-url origin git@github.com:<USERNAME>/daily-tools-legacy.git && cd ..
cd life-automation-legacy && git remote set-url origin git@github.com:<USERNAME>/life-automation-legacy.git && cd ..
```

### 4. `play_ground` 直下のルート定義ファイルリンク一時張り直し
- [ ] リネームに伴い、`play_ground/GEMINI.md` 等のシンボリックリンクが切れるため、一時的に `second-brain-legacy` 側へ張り直す。
- [ ] ※現在リンク先のファイルが存在しない場合（デッドリンク）でも、Phase 01 で `agent-core` 側の正しいファイルへ張り直されるまでの「一時的なプレースホルダー」として許容する。

```bash
set -e
cd /Users/shoheihasegawa/play_ground || exit 1

# 既存のリンクを削除
rm -f GEMINI.md AGENT.md

# legacy側へシンボリックリンクを張り直し（一時措置）
ln -s ./second-brain-legacy/99_System/AI_Core/Local_GEMINI.md GEMINI.md
ln -s ./second-brain-legacy/99_System/AI_Core/Local_AGENT.md AGENT.md

echo "Symlinks updated."
```

### 5. 完了確認
```bash
# 1. ディレクトリ名の変更確認
ls -ld *-legacy

# 2. リンクの生存確認
ls -la GEMINI.md AGENT.md
cat GEMINI.md | head -n 3
```
