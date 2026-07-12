import sys
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import io

agent_core_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(agent_core_dir / "tools"))

import register_zettelkasten_note

class TestRegisterZettelkastenNote(unittest.TestCase):
    @patch('register_zettelkasten_note.SecondBrainFactory')
    @patch('sys.argv', ['register_zettelkasten_note.py', '--type', 'inbox', '--title', 'Test Title'])
    def test_read_body_from_stdin(self, mock_factory):
        mock_service = MagicMock()
        mock_factory.create_service.return_value = mock_service
        mock_service.register_inbox_note.return_value = True

        # stdin がパイプ経由であることをモックする (isatty = False)
        mock_stdin = io.StringIO("This is body content from stdin")
        mock_stdin.isatty = MagicMock(return_value=False)
        
        with patch('sys.stdin', mock_stdin):
            register_zettelkasten_note.main()

        # stdin から読み取った内容で register_inbox_note が呼ばれることを検証
        mock_service.register_inbox_note.assert_called_once_with(
            title='Test Title',
            content='This is body content from stdin',
            tags=[]
        )

if __name__ == '__main__':
    unittest.main()
