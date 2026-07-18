import os
import json
import sqlite3
import pytest
from unittest import mock
import tempfile
import shutil

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from tools.harvest_tool import HarvestTool

@pytest.fixture
def workspace():
    temp_dir = tempfile.mkdtemp()
    
    # Create required directories
    os.makedirs(os.path.join(temp_dir, "agent-core", "data", "task_registry"))
    os.makedirs(os.path.join(temp_dir, "agent-core", "data", "task_archive"))
    os.makedirs(os.path.join(temp_dir, "agent-core", "queue"))
    
    yield temp_dir
    
    shutil.rmtree(temp_dir)

def test_harvest_tool_completed_task_with_zero_actual_fallback(workspace):
    # Setup task JSON
    task_id = "task-123"
    task_json_path = os.path.join(workspace, "agent-core", "data", "task_registry", f"{task_id}.json")
    with open(task_json_path, 'w', encoding='utf-8') as f:
        json.dump({
            "title": "Test Task",
            "category": "M",
            "task_type": "ONE_OFF",
            "area_id": "Area-1"
        }, f)
        
    # Setup Briefing file
    briefing_path = os.path.join(workspace, "Briefing_2026-07-18.md")
    with open(briefing_path, 'w', encoding='utf-8') as f:
        f.write("- [x] Test Task (本日予定: 30, 本日実績: 0) <!-- id: task-123 -->\n")
        
    # Run tool
    tool = HarvestTool(workspace)
    tool.run(briefing_path)
    
    # Assert DB
    db_path = os.path.join(workspace, "agent-core", "data", "metrics.db")
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT actual_minutes, is_completed FROM activity_logs WHERE task_id=?", (task_id,))
        row = cursor.fetchone()
        assert row is not None
        assert row[0] == 30  # Fallback to estimated
        assert row[1] == 1   # True
        
    # Assert JSON moved to archive
    assert not os.path.exists(task_json_path)
    archive_path = os.path.join(workspace, "agent-core", "data", "task_archive", "202607", f"{task_id}.json")
    assert os.path.exists(archive_path)
    with open(archive_path, 'r', encoding='utf-8') as f:
        archived_data = json.load(f)
        assert archived_data["status"] == "COMPLETED"

def test_harvest_tool_in_progress_task(workspace):
    # Setup task JSON
    task_id = "task-456"
    task_json_path = os.path.join(workspace, "agent-core", "data", "task_registry", f"{task_id}.json")
    with open(task_json_path, 'w', encoding='utf-8') as f:
        json.dump({
            "title": "In Progress Task",
            "cumulative_minutes": 10
        }, f)
        
    # Setup Briefing file
    briefing_path = os.path.join(workspace, "Briefing_2026-07-19.md")
    with open(briefing_path, 'w', encoding='utf-8') as f:
        f.write("- [ ] In Progress Task (本日予定: 60, 本日実績: 20) <!-- id: task-456 -->\n")
        
    # Run tool
    tool = HarvestTool(workspace)
    tool.run(briefing_path)
    
    # Assert DB
    db_path = os.path.join(workspace, "agent-core", "data", "metrics.db")
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT actual_minutes, is_completed FROM activity_logs WHERE task_id=?", (task_id,))
        row = cursor.fetchone()
        assert row is not None
        assert row[0] == 20
        assert row[1] == 0
        
    # Assert JSON NOT moved, cumulative_minutes updated
    assert os.path.exists(task_json_path)
    with open(task_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        assert data["cumulative_minutes"] == 30  # 10 + 20

def test_harvest_tool_upsert_behavior(workspace):
    tool = HarvestTool(workspace)
    tool._ensure_db()
    db_path = os.path.join(workspace, "agent-core", "data", "metrics.db")
    
    # Pre-insert a row
    with sqlite3.connect(db_path) as conn:
        conn.execute('''
            INSERT INTO activity_logs (task_id, title, task_type, category, area_id, estimated_minutes, actual_minutes, worked_date, is_completed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ("task-789", "Old Title", "ONE_OFF", "M", "A-1", 10, 10, "2026-07-20", 0))

    # Setup task JSON
    task_id = "task-789"
    task_json_path = os.path.join(workspace, "agent-core", "data", "task_registry", f"{task_id}.json")
    with open(task_json_path, 'w', encoding='utf-8') as f:
        json.dump({"title": "New Title"}, f)
        
    # Setup Briefing file
    briefing_path = os.path.join(workspace, "Briefing_2026-07-20.md")
    with open(briefing_path, 'w', encoding='utf-8') as f:
        f.write("- [x] New Title (本日予定: 10, 本日実績: 5) <!-- id: task-789 -->\n")
        
    # Run tool
    tool.run(briefing_path)
    
    # Assert DB is updated
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT actual_minutes, is_completed, title FROM activity_logs WHERE task_id=?", (task_id,))
        row = cursor.fetchone()
        assert row[0] == 5
        assert row[1] == 1
        assert row[2] == "New Title"
