# Legacy COO Algorithm Reference
This document contains the legacy implementation of the Daily Planning and Scheduling algorithms extracted from `life-automation-legacy`.
These codes and specs serve as a reference for re-implementing the features in `core-service`.

## 1. Daily Planning Spec
```markdown
# 仕様書: Daily Planning Service (COO Module)

## 1. 概要
`DailyPlanningService` は、ユーザーの1日の計画（Daily Schedule）を生成し、外部システム（Google Calendar、Mobile Vault）に出力する Application 層のユースケース（ファサード）です。
「週末のCEO」が定義したルールやタスクを、「平日のWorker」が迷いなく実行できる形（スケジュール）に変換・配信する責務を持ちます。

## 2. 実行トリガー
このサービスは、PM Agent（Agent Core）によって以下のいずれかのタイミングで呼び出されます。
1. **能動的**: ユーザーが Coach Agent とのジャーナリングを完了した直後。
2. **受動的**: `launchd` 等のバッチ処理による深夜帯での自動実行（セーフティネット）。

## 3. 入出力仕様

### 入力 (依存インターフェースおよび引数)
- `target_date`: 計画対象となる日付（`datetime.date`）。通常は「明日」または「今日」。
- `task_pool`: 現在の未完了タスク一覧（`TaskPool`）。API/CLIの呼び出し元から注入される。
- `RoutineRepositoryPort`: ユーザーの定期的なルーティン定義を読み込む。
- `RoutineExecutionHistory`: 過去のルーティン実行履歴。ローテーション等の計算に用いる。
- `GoogleCalendarPort`: 対象日の既存予定を `TimeBlock` として取得する。また、生成されたスケジュールをカレンダーへ反映する。
- `MobileVaultPort`: 生成されたスケジュールをモバイル端末上で確認できるよう、Markdownとして出力・古いファイルの削除を行う。

### 処理フロー
1. **既存予定と休日の取得**: `GoogleCalendarPort.get_events(target_date)` を呼び出す。
   - 既存イベントのタイトルに `祝日`, `有給` 等が含まれている場合、その日を `is_holiday = True` としてマークする。
   - *【フェールセーフ】*: 通信エラー等で例外が発生した場合は、後続処理を止めないよう空リスト `[]` でフォールバックする。
2. **ルーティンの取得とLife Portfolioへのマッピング**: `RoutineRepositoryPort.load_all()` を呼び出す。
   - インフラ層でYAMLをパースする際、カテゴリを `work`, `growth`, `maintenance`, `play`, `buffer` の5つのLife Portfolioにマッピングする。
3. **スケジュールの計算**: `DailySchedule.generate_from_routines(target_date, routines, history, existing_events, is_holiday)` を呼び出し、衝突が回避された最適なブロック割り当てを生成する。休日の場合は `exclude_on_holidays` 指定のあるルーティンを除外する。
4. **Buffer (余白) の自動生成**: `schedule.fill_buffers()` を呼び出し、5:00〜23:59の空き時間を検索。前後15分(Soft Margin)を削り、30分以上(Threshold)の空きがあれば `Buffer` ブロックとして生成する。
5. **タスクの割り当て**: 生成された各 `TimeBlock` のカテゴリと残り時間を元に、引数で渡された `task_pool` からタスクを取り出し、ブロックにアサインする。
   - *【容量制限】*: `Buffer` ブロックへ引き当てる場合、ブロック総時間の **80% (Capacity Limit)** までしかタスクを割り当てない。
6. **スケジュールのパブリッシュ**:
   - `GoogleCalendarPort.sync_schedule(schedule)` で、Agentが作成した予定枠をカレンダーに書き込む。
   - `MobileVaultPort.export(schedule)` で、モバイル用Markdownファイルを出力する。
   - *【フェールセーフ】*: パブリッシュの各ステップで例外が発生した場合も、システムをクラッシュさせずに警告ログを出力し処理を続行する。
6. **TaskPoolの返却**: 割り当て後、未完了タスクが残った状態の `task_pool` を戻り値として返し、呼び出し元で永続化させる。

## 4. アーキテクチャ上の制約
- **知識の分離 (ADR 9)**: 本サービスは「特定の祝日」や「ユーザー特有の文字列」等の知識を持たない。すべて Domain モデルまたは Repository から提供される汎用データとして扱う。
- **インフラの隠蔽 (ADR 10)**: API通信やファイルI/Oの実装詳細はすべて Infrastructure 層に委譲し、本サービスは Port（Protocol）のみに依存すること。
```

## 2. Domain Implementation (coo/)
### src/domain/coo/time_interval.py
```python
from datetime import datetime
from typing import List

from pydantic import BaseModel


class TimeInterval(BaseModel):
    """
    具体的な日時の「区間」を表す値オブジェクト。
    時間枠の重なり判定や分割（引き算）などの幾何学的計算を担当する。
    """
    start: datetime
    end: datetime

    def subtract(self, other: 'TimeInterval') -> List['TimeInterval']:
        """
        自分自身(self)の区間から、指定された区間(other)を差し引いた残りの区間を返す。
        重なっていない場合は元の区間をそのまま返す。
        完全に飲み込まれる場合は空リストを返す。
        中を分断される場合は2つの区間に分割して返す。
        """
        # other が self と全く重なっていない場合
        if self.end <= other.start or self.start >= other.end:
            return [self]
        
        # other が self を完全に飲み込む場合
        if other.start <= self.start and other.end >= self.end:
            return []
        
        # 前方が削られる場合 (otherが前にかかっている)
        if other.start <= self.start and other.end < self.end:
            return [TimeInterval(start=other.end, end=self.end)]
        
        # 後方が削られる場合 (otherが後ろにかかっている)
        if other.start > self.start and other.end >= self.end:
            return [TimeInterval(start=self.start, end=other.start)]
        
        # 中間がくり抜かれる場合 (otherが完全にselfの内部にある)
        return [
            TimeInterval(start=self.start, end=other.start),
            TimeInterval(start=other.end, end=self.end)
        ]
```

### src/domain/coo/task.py
```python
from enum import Enum
from typing import List

from pydantic import BaseModel, Field

from domain.coo.value_objects import LifePortfolioCategory, TaskMetadata


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class Task(BaseModel):
    """
    具体的な1つの作業単位。
    """
    id: str
    name: str
    metadata: TaskMetadata = Field(default_factory=TaskMetadata)
    status: TaskStatus = TaskStatus.TODO
    category: LifePortfolioCategory = LifePortfolioCategory.GENERAL
    actual_minutes: int = 0

    def remaining_minutes(self) -> int:
        """
        見積もり時間から実働時間を引いた残り時間を計算する。
        0未満にはならない。
        """
        if self.status == TaskStatus.DONE:
            return 0
        remaining = self.metadata.estimated_minutes - self.actual_minutes
        return max(0, remaining)

    def update_status(self, new_status: TaskStatus, minutes_spent: int = 0):
        """
        タスクのステータスを更新し、実働時間を加算する。
        """
        self.status = new_status
        self.actual_minutes += minutes_spent


class TaskPool(BaseModel):
    """
    まだスケジュールされていない未完了タスクの集合（集約ルート）。
    """
    tasks: List[Task] = Field(default_factory=list)

    def add_task(self, task: Task):
        """タスクをプールに追加する"""
        self.tasks.append(task)

    def pop_tasks_by_category(self, category: LifePortfolioCategory, limit_minutes: int) -> List[Task]:
        """
        指定カテゴリのタスクを、優先順位が高い順に取り出す。
        取り出したタスクの合計見積もり時間が limit_minutes を超えない範囲で最大限抽出する。
        抽出されたタスクはプールから削除される。
        """
        # カテゴリに一致するタスクとそうでないタスクに分ける
        matching_tasks = [t for t in self.tasks if t.category == category]
        other_tasks = [t for t in self.tasks if t.category != category]

        # 優先度のマッピング（数字が小さいほど優先度が高いと定義してソート）
        priority_map = {"high": 1, "medium": 2, "low": 3}

        # 優先度順、期限(deadline)順でソート（期限がない場合は未来日として扱う）
        # deadline が None の場合は、比較でエラーにならないように遠い未来の日付にする
        from datetime import date
        far_future = date(2999, 12, 31)

        matching_tasks.sort(
            key=lambda t: (
                priority_map.get(t.metadata.priority, 99),
                t.metadata.deadline or far_future
            )
        )

        selected_tasks = []
        total_minutes = 0
        remaining_matching_tasks = []

        for task in matching_tasks:
            task_remaining = task.remaining_minutes()
            if task_remaining == 0:
                continue

            # 枠に収まるか判定
            if total_minutes + task_remaining <= limit_minutes:
                selected_tasks.append(task)
                total_minutes += task_remaining
            else:
                remaining_matching_tasks.append(task)

        # プールを更新（選ばれなかった同カテゴリのタスク + 他カテゴリのタスク）
        self.tasks = remaining_matching_tasks + other_tasks

        return selected_tasks
```

### src/domain/coo/protocols.py
```python
from typing import Protocol

from domain.coo.task import TaskPool


class TaskRepositoryPort(Protocol):
    def load(self) -> TaskPool:
        ...

    def save(self, pool: TaskPool) -> None:
        ...
```

### src/domain/coo/__init__.py
```python
```

### src/domain/coo/factories.py
```python
import uuid
from typing import Any, Dict

from domain.coo.entities import Routine
from domain.coo.task import Task, TaskStatus
from domain.coo.value_objects import LifePortfolioCategory, RecurrenceRule, TaskMetadata, TimeConfig


class RoutineFactory:
    """YAML等の生データからRoutineエンティティを生成するドメインファクトリ"""

    @staticmethod
    def create_from_raw(data: Dict[str, Any]) -> Routine:
        # カテゴリの変換処理をここに集約
        raw_category = data.get("category", "general")
        category_map = {
            "仕事": LifePortfolioCategory.WORK,
            "家事": LifePortfolioCategory.HOUSEWORK,
            "会社のイベント": LifePortfolioCategory.COMPANY_EVENT,
            "自己研鑽": LifePortfolioCategory.GROWTH,
            "健康": LifePortfolioCategory.HEALTH,
            "維持管理": LifePortfolioCategory.MAINTENANCE,
            "遊び": LifePortfolioCategory.PLAY,
            "財務": LifePortfolioCategory.FINANCE,
            "余白": LifePortfolioCategory.BUFFER,
            "company_event": LifePortfolioCategory.COMPANY_EVENT,
            "administrative": LifePortfolioCategory.WORK,
            "instructor_duty": LifePortfolioCategory.WORK,
            "work": LifePortfolioCategory.WORK,
            "focus_work": LifePortfolioCategory.GROWTH,
            "training": LifePortfolioCategory.GROWTH,
            "reading": LifePortfolioCategory.GROWTH,
            "growth": LifePortfolioCategory.GROWTH,
            "routine": LifePortfolioCategory.MAINTENANCE,
            "workout": LifePortfolioCategory.MAINTENANCE,
            "housework": LifePortfolioCategory.MAINTENANCE,
            "maintenance": LifePortfolioCategory.MAINTENANCE,
            "hobby": LifePortfolioCategory.PLAY,
            "play": LifePortfolioCategory.PLAY,
            "buffer": LifePortfolioCategory.BUFFER,
        }
        category = category_map.get(raw_category, LifePortfolioCategory(raw_category) if raw_category in [e.value for e in LifePortfolioCategory] else LifePortfolioCategory.GENERAL)

        return Routine(
            id=data.get("id", ""),
            name=data["name"],
            category=category,
            rule=RecurrenceRule(**data["rule"]),
            time=TimeConfig(**data.get("time", {})) if "time" in data else None
        )


class TaskFactory:
    """マークダウン文字列等からTaskエンティティを生成するドメインファクトリ"""

    @staticmethod
    def create_from_markdown(
        name: str,
        task_id: str = None,
        status: TaskStatus = TaskStatus.TODO,
        category_str: str = None,
        metadata: TaskMetadata = None
    ) -> Task:
        name = name.strip()
        metadata = metadata or TaskMetadata()
        
        # Determine category. Tag > category_str > default
        category = LifePortfolioCategory.GENERAL
        if category_str:
            try:
                category = LifePortfolioCategory(category_str)
            except ValueError:
                pass
                
        if "#CEO" in name:
            category = LifePortfolioCategory.GROWTH
        elif "#PM" in name:
            category = LifePortfolioCategory.GROWTH
        elif "#家事" in name:
            category = LifePortfolioCategory.HOUSEWORK
            
        return Task(
            id=task_id if task_id else uuid.uuid4().hex[:8],
            name=name,
            status=status,
            category=category,
            metadata=metadata
        )
```

### src/domain/coo/value_objects.py
```python
import datetime
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from domain.coo.time_interval import TimeInterval

from enum import Enum

from pydantic import BaseModel, Field


class LifePortfolioCategory(str, Enum):
    """Life Portfolioのカテゴリ定義"""
    GENERAL = "general"
    WORK = "work"
    HOUSEWORK = "housework"
    COMPANY_EVENT = "company_event"
    LEISURE = "leisure"
    FINANCE = "finance"
    HEALTH = "health"
    GROWTH = "growth"
    MAINTENANCE = "maintenance"
    PLAY = "play"
    BUFFER = "buffer"


class BufferGenerationPolicy(BaseModel):
    """バッファ生成ルールをカプセル化した値オブジェクト"""
    soft_margin_minutes: int = 15
    min_threshold_minutes: int = 30

class TimeConfig(BaseModel):
    """時間設定を表す値オブジェクト"""

    start: Optional[str] = None  # "HH:MM" format
    end: Optional[str] = None  # "HH:MM" format
    all_day: bool = False
    flexible: bool = False

    def to_interval(self, target_date: datetime.date) -> Optional['TimeInterval']:
        """自身の設定を具体的な日付の TimeInterval オブジェクトに変換する"""
        if not self.start or not self.end:
            return None
        
        # To avoid circular imports, import here or keep TimeInterval simple
        from datetime import timedelta

        from domain.coo.time_interval import TimeInterval
        
        fmt = "%H:%M"
        try:
            s_time = datetime.datetime.strptime(self.start, fmt).time()
            e_time = datetime.datetime.strptime(self.end, fmt).time()
            
            start_dt = datetime.datetime.combine(target_date, s_time)
            end_dt = datetime.datetime.combine(target_date, e_time)
            
            # 日またぎ考慮
            if end_dt < start_dt:
                end_dt += timedelta(days=1)
                
            return TimeInterval(start=start_dt, end=end_dt)
        except (ValueError, TypeError):
            return None

    def duration_minutes(self) -> int:
        """この設定の総時間を計算する"""
        if self.all_day or self.flexible:
            return 12 * 60
            
        interval = self.to_interval(datetime.date(2000, 1, 1))
        if interval:
            diff = interval.end - interval.start
            return int(diff.total_seconds() / 60)
        return 0



class RecurrenceRule(BaseModel):
    """繰り返しルールを表す値オブジェクト"""

    freq: str  # "daily", "weekly", "monthly", "monthly_rotation"
    byday: Optional[str] = None  # e.g., "MO,FR" or "3FR"
    bymonthday: Optional[int] = None
    until: Optional[datetime.date] = None

    exclude_on_company_events: bool = False
    exclude_on_holidays: bool = False
    include_on_company_event_days: List[str] = Field(default_factory=list)
    rotation_items: List[str] = Field(default_factory=list)


class TaskMetadata(BaseModel):
    """タスクのメタデータを表す値オブジェクト"""

    priority: str = "medium"
    estimated_minutes: int = 30
    deadline: Optional[datetime.date] = None
```

### src/domain/coo/schedule.py
```python
import uuid
from datetime import date as date_type
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

from domain.coo.task import Task
from domain.coo.value_objects import BufferGenerationPolicy, LifePortfolioCategory, TimeConfig


class TimeBlock(BaseModel):
    """
    1日のうちの特定の時間枠を表すエンティティ。
    """
    id: str
    name: str
    category: LifePortfolioCategory = LifePortfolioCategory.GENERAL
    time_config: TimeConfig
    assigned_tasks: List[Task] = Field(default_factory=list)

    def duration_minutes(self) -> int:
        """ブロックの総時間を計算する"""
        return self.time_config.duration_minutes()

    def remaining_minutes(self) -> int:
        """ブロックの残り容量を計算する (Bufferの場合は80%制限)"""
        assigned_duration = sum(task.remaining_minutes() for task in self.assigned_tasks)
        limit = self.duration_minutes()
        if self.category == LifePortfolioCategory.BUFFER:
            limit = int(limit * 0.8)
        return max(0, limit - assigned_duration)

    def assign_task(self, task: Task) -> bool:
        """
        タスクが枠に収まるなら割り当てて True を返す。
        収まらない場合は False を返す。
        """
        if task.remaining_minutes() <= self.remaining_minutes():
            self.assigned_tasks.append(task)
            return True
        return False

    def release_incomplete_tasks(self) -> List[Task]:
        """
        未完了のタスクをブロックから取り除き、返却する。
        これにより、次回の枠へ持ち越せるようにする。
        """
        incomplete = []
        completed = []
        for task in self.assigned_tasks:
            if task.remaining_minutes() > 0:
                incomplete.append(task)
            else:
                completed.append(task)
        
        self.assigned_tasks = completed
        return incomplete


class DailySchedule(BaseModel):
    """
    1日のスケジュール全体（集約ルート）。
    """
    date: date_type
    blocks: List[TimeBlock] = Field(default_factory=list)

    def fill_buffers(self, policy: BufferGenerationPolicy, day_start: str = "00:00", day_end: str = "24:00"):
        from datetime import timedelta

        from domain.coo.time_interval import TimeInterval

        fmt = "%H:%M"
        if day_end == "24:00":
            day_end = "23:59"
            
        try:
            start_dt = datetime.combine(self.date, datetime.strptime(day_start, fmt).time())
            end_dt = datetime.combine(self.date, datetime.strptime(day_end, fmt).time())
        except ValueError:
            return

        free_intervals = [TimeInterval(start=start_dt, end=end_dt)]
        
        # 既存の具体的な時間枠を持つブロックで free_intervals を削る
        for b in self.blocks:
            if not b.time_config or b.time_config.all_day or b.time_config.flexible:
                continue
            b_interval = b.time_config.to_interval(self.date)
            if not b_interval:
                continue
            
            new_free = []
            for f in free_intervals:
                new_free.extend(f.subtract(b_interval))
            free_intervals = new_free

        # 余白ルールを適用してBufferブロックを作成
        for f in free_intervals:
            # 1. Soft Margins
            f.start += timedelta(minutes=policy.soft_margin_minutes)
            f.end -= timedelta(minutes=policy.soft_margin_minutes)
            
            if f.end <= f.start:
                continue
            
            # 2. Minimum Threshold
            diff_mins = int((f.end - f.start).total_seconds() / 60)
            if diff_mins < policy.min_threshold_minutes:
                continue
            
            self.blocks.append(TimeBlock(
                id=f"buffer-{uuid.uuid4().hex[:8]}",
                name="Buffer",
                category=LifePortfolioCategory.BUFFER,
                time_config=TimeConfig(
                    start=f.start.strftime("%H:%M"),
                    end=f.end.strftime("%H:%M")
                )
            ))
```

### src/domain/coo/entities.py
```python
import datetime
from typing import List, Optional

from pydantic import BaseModel

from domain.coo.value_objects import LifePortfolioCategory, RecurrenceRule, TimeConfig

WEEKDAY_MAP = {0: "MO", 1: "TU", 2: "WE", 3: "TH", 4: "FR", 5: "SA", 6: "SU"}


def _is_nth_weekday(target_date: datetime.date, nth_weekday_str: str) -> bool:
    """
    '3FR' (第3金曜日) のような文字列を解析し、target_date がそれに該当するか判定する。
    """
    if len(nth_weekday_str) != 3:
        return False
    try:
        n = int(nth_weekday_str[0])
    except ValueError:
        return False

    target_wd_str = nth_weekday_str[1:]
    current_wd_str = WEEKDAY_MAP[target_date.weekday()]

    if current_wd_str != target_wd_str:
        return False

    # 第何曜日か計算
    # 1日からその日までの日数から、同じ曜日が何回あったかを計算
    # 1..7 -> 第1, 8..14 -> 第2, 15..21 -> 第3, 22..28 -> 第4, 29..31 -> 第5
    nth = (target_date.day - 1) // 7 + 1

    return nth == n


class Routine(BaseModel):
    """
    定例予定(Routine)を表現するエンティティ。
    自身の発生ルール(RecurrenceRule)を元に、指定された日付でアクティブか判定する振る舞いを持つ。
    """

    name: str
    category: LifePortfolioCategory
    rule: RecurrenceRule
    time: Optional[TimeConfig] = None

    def is_active_on(self, target_date: datetime.date, company_event_dates: List[datetime.date] = None, is_holiday: bool = False) -> bool:
        company_event_dates = company_event_dates or []

        # 1. until (期限切れ) 判定
        if self.rule.until and target_date > self.rule.until:
            return False

        is_company_event_day = target_date in company_event_dates
        current_wd_str = WEEKDAY_MAP[target_date.weekday()]

        # 2. 会社行事による除外判定 (exclude_on_company_events)
        if self.rule.exclude_on_company_events and is_company_event_day:
            return False

        # 2.5 祝日による除外判定 (exclude_on_holidays)
        if self.rule.exclude_on_holidays and is_holiday:
            return False

        # 3. 会社行事による強制包含判定 (include_on_company_event_days)
        if is_company_event_day and self.rule.include_on_company_event_days:
            for include_rule in self.rule.include_on_company_event_days:
                # "3FR" などのルールに合致しているならTrue
                if _is_nth_weekday(target_date, include_rule):
                    return True

        # 4. 基本的な byday 判定
        if self.rule.byday:
            days = [d.strip() for d in self.rule.byday.split(",")]
            # 単純な曜日指定 ("MO", "FR" など)
            if current_wd_str in days:
                return True
            # 第N曜日指定 ("3FR" など)
            for d in days:
                if len(d) == 3 and _is_nth_weekday(target_date, d):
                    return True

        # 5. 基本的な bymonthday 判定
        if self.rule.bymonthday:
            if self.rule.bymonthday == -1:
                # 月末日判定
                import calendar

                last_day = calendar.monthrange(target_date.year, target_date.month)[1]
                if target_date.day == last_day:
                    return True
            elif self.rule.bymonthday == target_date.day:
                return True

        # 6. daily 判定
        if self.rule.freq == "daily":
            return True

        return False
```

### src/domain/coo/services/schedule_generator.py
```python
import uuid
from datetime import date as date_type
from typing import List

from domain.coo.entities import Routine
from domain.coo.history import RoutineExecutionHistory
from domain.coo.schedule import DailySchedule, TimeBlock
from domain.coo.value_objects import TimeConfig


class ScheduleGenerator:
    """
    複雑な衝突回避・スケジュール生成ロジックを担うドメインサービス。
    """

    @staticmethod
    def generate(
        target_date: date_type,
        routines: List[Routine],
        history: RoutineExecutionHistory,
        existing_events: List[TimeBlock],
        is_holiday: bool
    ) -> DailySchedule:
        existing_events = existing_events or []
        blocks = list(existing_events)

        parsed_events = []
        for evt in existing_events:
            if evt.time_config:
                interval = evt.time_config.to_interval(target_date)
                if interval:
                    parsed_events.append(interval)

        for r in routines:
            if not r.is_active_on(target_date, is_holiday=is_holiday):
                continue

            if r.rule.rotation_items:
                item_name = history.get_next_rotation_item(r.rule.rotation_items)
                block_name = f"{r.name} ({item_name})"
            else:
                block_name = r.name

            interval = r.time.to_interval(target_date) if r.time else None

            if not interval or r.time.all_day or r.time.flexible:
                blocks.append(TimeBlock(
                    id=f"{r.name}-{target_date}-{uuid.uuid4().hex[:8]}",
                    name=block_name,
                    category=r.category,
                    time_config=r.time or TimeConfig(all_day=True)
                ))
                continue

            # 衝突回避の計算
            routine_intervals = [interval]
            for ext_inv in parsed_events:
                new_intervals = []
                for ri in routine_intervals:
                    new_intervals.extend(ri.subtract(ext_inv))
                routine_intervals = new_intervals

            for frag in routine_intervals:
                frag_id = f"{r.name}-{target_date}-{uuid.uuid4().hex[:8]}"
                blocks.append(TimeBlock(
                    id=frag_id,
                    name=block_name,
                    category=r.category,
                    time_config=TimeConfig(
                        start=frag.start.strftime("%H:%M"),
                        end=frag.end.strftime("%H:%M")
                    )
                ))

        return DailySchedule(date=target_date, blocks=blocks)
```

### src/domain/coo/services/holiday_detection_service.py
```python
from typing import List

from domain.coo.schedule import TimeBlock


class HolidayDetectionService:
    """祝日や休暇を判定するドメインサービス"""

    @staticmethod
    def is_holiday(events: List[TimeBlock]) -> bool:
        """
        終日の予定であり、タイトルに特定のキーワードが含まれている場合に休暇と判定する。
        """
        holiday_keywords = ["祝日", "有給", "休み", "Holiday", "休暇"]
        for event in events:
            if event.time_config and event.time_config.all_day:
                if any(kw in event.name for kw in holiday_keywords):
                    return True
        return False
```

### src/domain/coo/history.py
```python
from datetime import date
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class RoutineExecutionHistory(BaseModel):
    """
    ローテーションタスクや定期的タスクの実行履歴（前回いつやったか）を管理する。
    """
    last_executed_dates: Dict[str, date] = Field(default_factory=dict)

    def record_execution(self, item_name: str, execution_date: date):
        """
        特定のアイテムの実行日を記録・更新する。
        """
        # 過去の記録があっても、新しい日付なら上書きする
        if item_name not in self.last_executed_dates or execution_date > self.last_executed_dates[item_name]:
            self.last_executed_dates[item_name] = execution_date

    def get_next_rotation_item(self, items: List[str]) -> Optional[str]:
        """
        与えられた候補アイテムのリストから、次回実行すべきアイテムを判定する。
        - まだ一度も実行されていないアイテムがあれば、それを優先する（複数ある場合はリストの順序に従う）
        - すべて実行済みの場合は、前回実行日が最も古いものを返す
        """
        if not items:
            return None

        # 一度も実行されていないアイテムを探す
        never_executed = [item for item in items if item not in self.last_executed_dates]
        if never_executed:
            return never_executed[0]

        # すべて実行済みの場合は、一番古い日付のものを選ぶ
        # 日付が同じ場合はリストの出現順にする
        items_with_dates = [(item, self.last_executed_dates[item]) for item in items]
        items_with_dates.sort(key=lambda x: x[1])

        return items_with_dates[0][0]
```

