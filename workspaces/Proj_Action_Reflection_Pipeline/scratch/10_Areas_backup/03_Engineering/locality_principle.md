# Locality Principle Policy

## コードとドキュメントの「Locality（局所性）」原則
AIが最も効率的に、かつ正確に稼働するための「情報の物理的配置」に関する鉄則。

1. **三位一体の集約**: 仕様(Spec)・実装(Code)・設定(Config)を同一ディレクトリに集約する（Locality Principle）。
2. **コンテキスト最小化**: そのディレクトリを読めば修正が完結する状態（Self-contained）を維持する。
3. **二重管理の廃止**: `second-brain`（思想）と `実装リポジトリ`（手順）の境界を明確にし、実装の詳細はコードの隣にある `spec.md` を SSOT とする。
