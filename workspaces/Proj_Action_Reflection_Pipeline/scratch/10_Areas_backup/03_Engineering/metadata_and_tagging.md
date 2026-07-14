# Metadata and Tagging Policy

## メタデータとタグの三層構造 (Data Lake / Data Warehouse)
「システム制御（AI用）」と「文脈（人間用）」を分離し、検索性とセレンディピティを両立させる。

1. **System Tags (制御用)**: YAMLフロントマターに配置。`domain`, `date` 等、RAG検索のインデックスとして利用。
2. **Topic/Concept Tags (分類用)**: YAMLまたは本文末尾に配置。`#concept/xxx` 形式で、ドメインを跨いだ構造的共通性を表現する（例：`#concept/asymmetry`）。**名詞（#Python 等）のタグ化は禁止**し、リンク（`[[...]]`）を使用する。
3. **Context Tags (文脈・熱量用)**: 本文末尾に配置。**英語（スネークケース）**で統一。
   - **When/Whyの原則**: 「何（What）」ではなく「状況・理由（When/Why）」を記述（例：`#when/market_overheating`, `#why/abstraction_leak`）。
