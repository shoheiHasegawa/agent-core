import sys
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import io

agent_core_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(agent_core_dir / "tools"))

import read_inbox_queue

class TestReadInboxQueue(unittest.TestCase):
    @patch('read_inbox_queue.QUEUE_DIR')
    @patch('read_inbox_queue.backup_queue')
    @patch('sys.argv', ['read_inbox_queue.py', '--limit', '2'])
    def test_read_queue_limit(self, mock_backup, mock_queue_dir):
        mock_queue_dir.exists.return_value = True
        
        # 3つのモックパケットを用意
        p1 = MagicMock(); p1.name = "mobile_packet_1.md"
        p2 = MagicMock(); p2.name = "mobile_packet_2.md"
        p3 = MagicMock(); p3.name = "mobile_packet_3.md"
        
        mock_queue_dir.glob.return_value = [p1, p2, p3]

        with patch('builtins.open', unittest.mock.mock_open(read_data="content")), \
             patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            
            # CLIツールとしてのエントリーポイント（main関数）を呼び出す想定
            read_inbox_queue.main()
            
        output = mock_stdout.getvalue()
        
        # limit 2 なので3つ目は出力されないはず
        self.assertIn("mobile_packet_1.md", output)
        self.assertIn("mobile_packet_2.md", output)
        self.assertNotIn("mobile_packet_3.md", output)

if __name__ == '__main__':
    unittest.main()
