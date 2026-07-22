import os
from pathlib import Path

from core_service.src.domain.system_events.gateway import SystemEventGateway
from core_service.src.infrastructure.system_events.queue_system_event_gateway import QueueSystemEventGateway

class SystemEventFactory:
    @staticmethod
    def create_gateway() -> SystemEventGateway:
        """
        SystemEventGatewayのインスタンスを生成して返す。
        設定（環境変数）からAGENT_QUEUE_DIRを注入する。
        """
        # 環境変数からQueueディレクトリを取得（デフォルトはフォールバックとして設定）
        queue_dir_str = os.getenv("AGENT_QUEUE_DIR", "/Users/shoheihasegawa/you_inc/agent-core/queue")
        queue_dir = Path(queue_dir_str)
        
        return QueueSystemEventGateway(queue_dir=queue_dir)
