# Decision 0001: プロジェクト立ち上げと情報整理の構成

> [!WARNING]
> **Status: Deprecated** (この決定事項は最新の `to-be/` アーキテクチャに統合・置換されました)

## 背景
`second-brain` と `life-automation` の密結合を解消し、アーキテクチャを再編するための作業を、安全かつ計画的に進める必要がある。
議論が大きくなることが予想されるため、情報を体系的に整理しながら進める方針とした。

## 決定事項
- `10_Projects` 配下に `Proj_Playground_Reconstruction` を設立。
- 以下のディレクトリおよびファイル構成を採用する。
  - `README.md`
  - `as-is/`
  - `to-be/`
  - `decision/`
  - `progress.md`
  - `open-item.md`

これにより、現状の課題整理、未来の設計、未決事項の議論、決定の記録 (ADR) を明確に分離してプロジェクトを進行する。
