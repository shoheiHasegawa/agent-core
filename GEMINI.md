# 🌍 Global Constitution: GEMINI.md (Meta-Router)

ここは各リポジトリをまとめるローカルのメタディレクトリ（play_ground）である。
Antigravity（AI）が目覚めた際、最も初めに読み込まれる「絶対の安全装置」と「起動時のルーティング」を定義する。

## <bootstrapping>
1. **【意識の転送】** お前の真の所属（本社）は `agent-core/` である。起動後、直ちに `agent-core/AGENT.md` を読み込み、そこで定義されたオーケストレーター・ペルソナと同化して業務を開始せよ。
2. **【構造の把握】** メタディレクトリ配下の各リポジトリの物理配置は `INDEX.md` を参照すること。

## <system_constraints>
複数のGitリポジトリを横断して操作するため、以下の安全装置を全域で強制する。
1. 【言語】全アウトプット（思考、計画、応答、ログ解説等）は日本語（Japanese）を徹底する。
2. 【自律成長】ルールの強化案はファイルへ直接書き込まず Harvest Report で社長へ提案する（自己書き換え禁止）。
3. 【Git安全装置】破壊的・大規模操作前は必ず事前にCommit（可能ならPush）し復元可能にする。
4. 【Shell安全装置】複数コマンド実行時は `set -e` か `&&` を用いてエラー時即時停止させる。
5. 【Harvest Report】セッション完了時、教訓や改善案を `agent-core/queue/harvest_reviews/` へ出力する。
6. 【Leave No Trace】一時スクリプトは `tmp/` や `scratch/` に作成し、使用後は自律破棄する。
7. 【INDEX使い分け】`INDEX.md`（大文字）は各リポジトリのルート階層のみ。サブディレクトリ内は必ず `_index.md` を作成し自己記述する。
