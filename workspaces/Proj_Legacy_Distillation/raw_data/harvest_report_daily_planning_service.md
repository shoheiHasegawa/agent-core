# Harvest Report - Daily Planning Service 仕様と実装の乖離レビュー

## 1. 概要
- **対象**: `DailyPlanningService` (COO Module) の仕様 (`spec.md`) と実装の比較レビュー
- **日時**: 2026-06-06

## 2. 教訓 (Wisdom)
- **暗黙のフェールセーフ**: 実装者が気を利かせて追加したエラーハンドリング（外部API障害時のフォールバックや例外のキャッチ）は、往々にして仕様書には書かれていない「暗黙の仕様」となりがちである。これらを逆反映させることで、システムの堅牢性が明文化される。
- **Portパターンの有効性**: Pythonにおける `Protocol` を用いたPortの実装は、「インフラの隠蔽」というアーキテクチャ制約をコード上で強力に保証し、クリーンなFacade実装を実現するのに非常に役立つ。

## 3. 技術的負債 (Tech Debt)
- **仕様と実装の不整合**: 
  - `spec.md` の入力インターフェース定義に `RoutineExecutionHistory` が漏れている。
  - `spec.md` 側のアダプタ名（`GoogleCalendarRepository` 等）と実装側のPort名（`GoogleCalendarPort` 等）に表記揺れが存在する。

## 4. 改善案 (Action Items)
- [x] `src/application/coo/daily_planning/spec.md` の「入出力仕様 > 入力」に `RoutineExecutionHistory` を追記する。（対応済）
- [x] 同 `spec.md` に、エラー発生時のフォールバック方針（フェールセーフ）を明記する。（対応済）
- [x] 同 `spec.md` の外部連携インターフェースの名称を、実装に合わせて `Port` サフィックスに変更する。（対応済）
