---
title: "[Idea] 会員限定Webページの自律型スクレイパー構築"
date: "2026-04-20"
tags: ["idea", "automation", "python", "playwright"]
---

# 概要
`Mail_Content_Converter` プロジェクト（旧：Phase 3構想）から分離した、Webコンテンツの自動スクレイピング・要約パイプライン構想。

## 課題・背景
現在はテキストやメール本文などの情報を自動でMarkdown化できるが、本文中に「会員だけが読めるWebページのURL」と「パスワード」が記載されている場合、手動でページを開いて内容をコピーする手間が発生している。

## 次のアクション（アイデア）
メールを起点とするだけでなく、Second Brain内のURLリンクすべてを起点にできる汎用的なWeb抽出エンジンを構築する。

**技術スタック構想:**
*   `playwright` (Python)
*   `re` (正規表現によるURL・パスワード抽出)

**処理フロー案:**
1.  **抽出・解析**: テキスト内のURLとパスワード情報を正規表現で抽出。
2.  **自動アクセス・認証**: `playwright` のheadlessモードで該当URLを開き、DOM構造に合わせて認証やログイン情報（`page.fill()`, `page.click()`）を自動入力。
3.  **コンテンツ抽出と保存**: PDF化（`page.pdf`）もしくは本文抽出（`page.locator('body').inner_text()`）を行い、元のMarkdownファイルと同じ階層に併設する形（例：`[元ファイル名]_web_content.md`）でアウトプットを生成する。
