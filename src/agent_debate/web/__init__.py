"""Live-streaming debate GUI — FastAPI + SSE wrapper around the SDK.

Phase 13 bonus deliverable. The terminal menu remains the primary
evaluation surface; this module simply exposes the same orchestrator
through a browser by tapping the LifecycleRegistry hooks and pushing
events down an SSE stream.
"""
from __future__ import annotations

__all__ = ["api", "sse_broker"]
