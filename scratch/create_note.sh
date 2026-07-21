#!/bin/bash
export PYTHONPATH=/Users/shoheihasegawa/you_inc/core-service/src:/Users/shoheihasegawa/you_inc/agent-core

CLAIM=$(cat << 'EOF'
自己成長の主軸（目的）を「所属する組織のため」と外部に置いた瞬間、すべての行動は「仕事だからやる」という受動的な我慢に転落する。自律的なウェルビーイングを維持するためには、成長の主軸を常に「自分（You, Inc.）」に置き、組織のルールはそのプロセスを満たすための制約（ハックの対象）として扱うべきである。
EOF
)

CONTEXT=$(cat << 'EOF'
組織に属する以上、ルールの遵守や評価基準の達成は不可避である。しかし、ここで「組織に求められる価値」と「個人の価値向上」を混同してはならない。

会社のために自分を成長させようとすると、自分の本意ではない行動に対しても「仕事だから」という理由で耐え忍ぶ比重が大きくなり、心理的な摩耗を引き起こす。理想的な状態は、両者が同時に発生すること（交差点）であり、あくまで起点・軸足は「自分が目指す方向」になければならない。

この「自分軸」を組織内で貫徹するためには、正面衝突を避けるための高度なハック（防衛的戦術）が必要になる。自分軸の目標を、会社側のルールや評価レイヤーに合わせたフォーマットへと「翻訳」し、合意（契約化）しておくことで、初めて「自分のためにやっていることが会社からも評価される」という健全なエコシステムが成立する。
EOF
)

CONNECTIONS=$(cat << 'EOF'
- [Support] [[評価レイヤーの転換：同一成果に多次元の価値を与える「目的」の主従関係]]
- [Support] [[評価基準の先行定義は成果の客観的証明を担保する]]
- [Related] [[結果は常にあり方の影であり主体変容がすべての起点となる]]
EOF
)

python3 /Users/shoheihasegawa/you_inc/agent-core/tools/register_zettelkasten_note.py \
  --type permanent \
  --title "成長の主軸の外部化は我慢を生み出しウェルビーイングを破壊する" \
  --tags "concept/well_being,domain/career_strategy,concept/autonomy" \
  --claim "$CLAIM" \
  --context "$CONTEXT" \
  --connections "$CONNECTIONS" < /dev/null
