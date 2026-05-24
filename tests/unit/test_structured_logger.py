"""Structured JSON logger with FIFO rotation (rubric §A14, HW2 spec §8.6)."""
import json
from pathlib import Path

from agent_debate.shared.structured_logger import StructuredLogger


def test_logger_writes_json_line(tmp_path: Path):
    logger = StructuredLogger(output_dir=tmp_path, fifo_files=20, max_lines_per_file=500)
    logger.log(level="INFO", component="test", event="hello", a=1)
    files = sorted(tmp_path.glob("*.jsonl"))
    assert len(files) == 1
    line = files[0].read_text().strip()
    record = json.loads(line)
    assert record["component"] == "test"
    assert record["event"] == "hello"
    assert record["payload"] == {"a": 1}
    assert "ts" in record


def test_logger_rotates_after_max_lines(tmp_path: Path):
    logger = StructuredLogger(output_dir=tmp_path, fifo_files=20, max_lines_per_file=3)
    for i in range(7):
        logger.log(level="INFO", component="t", event=f"e{i}")
    files = sorted(tmp_path.glob("*.jsonl"))
    assert len(files) >= 3


def test_logger_caps_at_fifo_files(tmp_path: Path):
    logger = StructuredLogger(output_dir=tmp_path, fifo_files=2, max_lines_per_file=1)
    for i in range(10):
        logger.log(level="INFO", component="t", event=f"e{i}")
    files = sorted(tmp_path.glob("*.jsonl"))
    assert len(files) <= 2
