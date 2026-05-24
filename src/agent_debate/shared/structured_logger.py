"""Structured JSON logger with FIFO file rotation (rubric §A14, HW2 spec §8.6)."""
from __future__ import annotations

import json
import threading
from datetime import UTC, datetime
from pathlib import Path


class StructuredLogger:
    """
    Input:  level, component, event, payload (dict via **kwargs, optional)
    Output: appends JSONL record; rotates FIFO at max_lines_per_file
    Setup:  output_dir (Path), fifo_files (int), max_lines_per_file (int)
    """

    def __init__(self, output_dir: Path, fifo_files: int, max_lines_per_file: int) -> None:
        self.output_dir = output_dir
        self.fifo_files = fifo_files
        self.max_lines = max_lines_per_file
        self._lock = threading.Lock()
        self._current_idx = 0
        self._current_lines = 0
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def log(self, level: str, component: str, event: str, **payload) -> None:
        record = {
            "ts": datetime.now(tz=UTC).isoformat(),
            "level": level,
            "component": component,
            "event": event,
        }
        if payload:
            record["payload"] = payload
        line = json.dumps(record, separators=(",", ":")) + "\n"
        with self._lock:
            self._rotate_if_needed()
            with self._current_path().open("a", encoding="utf-8") as f:
                f.write(line)
            self._current_lines += 1

    def _current_path(self) -> Path:
        return self.output_dir / f"log-{self._current_idx:03d}.jsonl"

    def _rotate_if_needed(self) -> None:
        if self._current_lines >= self.max_lines:
            self._current_idx = (self._current_idx + 1) % self.fifo_files
            self._current_lines = 0
            self._current_path().unlink(missing_ok=True)
