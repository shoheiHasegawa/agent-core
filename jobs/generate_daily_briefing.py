#!/usr/bin/env python3
import argparse
import sys
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

# パス解決
sys.path.append(str(Path(__file__).parent.parent.resolve()))
sys.path.append(str(Path(__file__).parent.parent.parent / "core-service" / "src"))

from app_context import SessionLocal, get_core_service_container


def parse_args():
    parser = argparse.ArgumentParser(description="Daily Briefing Generator & Calendar Sync")
    parser.add_argument(
        "--date",
        "-d",
        type=str,
        default=None,
        help="Target date in YYYY-MM-DD format. If omitted, auto-calculated based on current time (>=18:00 -> tomorrow, <18:00 -> today).",
    )
    return parser.parse_args()


def resolve_target_date(date_str: str | None) -> datetime.date:
    if date_str:
        return datetime.strptime(date_str, "%Y-%m-%d").date()

    now = datetime.now(ZoneInfo("Asia/Tokyo"))
    if now.hour >= 18:
        # 夜間（18:00〜23:59）の実行 ➡ 「明日」の計画を立てる
        return now.date() + timedelta(days=1)
    else:
        # 早朝・日中（00:00〜17:59）の実行 ➡ 「今日」の計画を立てる（遅延起動・朝起動）
        return now.date()


def main():
    args = parse_args()
    try:
        target_date = resolve_target_date(args.date)
        print(f"🌅 Starting Daily Action Planner (generate_daily_briefing for {target_date})...")

        print("  - Injecting dependencies with Unit of Work...")
        session = SessionLocal()
        try:
            service = get_core_service_container(session).get_daily_planning_service()
            print(f"  - Executing DailyActionService.plan_day({target_date})...")
            briefing = service.plan_day(target_date, sync_to_calendar=True)
            session.commit()

        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

        print(f"  - Saved daily briefing ({target_date}) to Mobile Vault via BriefingGateway.")
        print("✅ Daily Action Planner completed successfully.")

    except Exception as e:
        error_details = f"スケジュール生成が失敗しました: {str(e)}\nTraceback:\n{traceback.format_exc()}"
        print(f"🚨 [FATAL ERROR] {error_details}")
        gateway = get_core_service_container().system_event_gateway
        gateway.publish_error("generate_daily_briefing", error_details)
        sys.exit(1)


if __name__ == "__main__":
    main()
