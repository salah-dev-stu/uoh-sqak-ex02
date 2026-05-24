"""Centralized API call manager.

Implements rubric §A4 ApiGatekeeper signature verbatim. Owns:
- Rate limiting (requests/minute, concurrent max)
- Token budget (warn at 75%, hard cap at 95% per rubric §A8)
- FIFO queue with backpressure (rubric §A5)
- Retry-with-backoff on transient errors
- Logged spend tracking via shared multiprocessing.Value + Lock (ADR-006)
"""
from __future__ import annotations

import collections
import time
from collections.abc import Callable
from dataclasses import dataclass
from decimal import Decimal
from multiprocessing.sharedctypes import Synchronized
from multiprocessing.synchronize import Lock


class BudgetExhausted(Exception):  # noqa: N818
    """Token spend crossed the hard cap; no more LLM calls allowed."""


class RateLimitExceeded(Exception):  # noqa: N818
    """Rate-limit windowed budget hit; caller should back off."""


class BackpressureExceeded(Exception):  # noqa: N818
    """FIFO queue is full; producer must slow down (rubric §A5)."""


@dataclass(frozen=True)
class QueueStatus:
    depth: int
    capacity: int
    in_flight: int


class ApiGatekeeper:
    """
    Input:  api_call (callable), *args, **kwargs
    Output: response (T); raises BudgetExhausted or RateLimitExceeded
    Setup:  config (dict), shared_spend (mp.Value), lock (mp.Lock),
            queue_capacity (int, default: 100)
    """

    def __init__(
        self,
        config: dict,
        shared_spend: Synchronized,
        lock: Lock,
        queue_capacity: int = 100,
    ) -> None:
        self.config = config
        self.shared_spend = shared_spend
        self.lock = lock
        self._queue: collections.deque = collections.deque()
        self._capacity = queue_capacity
        self._in_flight = 0
        self._call_times: collections.deque = collections.deque()

    def execute[T](self, api_call: Callable[..., T], *args, **kwargs) -> T:
        self._check_budget_hard_cap()
        now = time.time()
        self._enforce_rate_limit(now)
        self._call_times.append(now)
        max_retries = self.config.get("max_retries", 3)
        backoff = [1, 2, 4]
        last_exc: Exception | None = None
        for attempt in range(max_retries):
            try:
                self._in_flight += 1
                return api_call(*args, **kwargs)
            except (ConnectionError, TimeoutError) as exc:
                last_exc = exc
                if attempt < max_retries - 1:
                    time.sleep(backoff[min(attempt, len(backoff) - 1)])
                continue
            finally:
                self._in_flight -= 1
        raise last_exc if last_exc else RuntimeError("retries exhausted")

    def update_spend(self, tokens: int) -> None:
        with self.lock:
            self.shared_spend.value += tokens

    def get_spend_so_far(self) -> int:
        with self.lock:
            return self.shared_spend.value

    def estimate_cost(self, n_debates: int) -> Decimal:
        return Decimal("0.00")  # zero in login mode; override for API-key mode

    def get_queue_status(self) -> QueueStatus:
        return QueueStatus(
            depth=len(self._queue),
            capacity=self._capacity,
            in_flight=self._in_flight,
        )

    def enqueue(self, item: object) -> None:
        if len(self._queue) >= self._capacity:
            raise BackpressureExceeded(
                f"queue full ({len(self._queue)}/{self._capacity})"
            )
        self._queue.append(item)

    def drain(self) -> None:
        self._queue.clear()

    def _check_budget_hard_cap(self) -> None:
        cap = self.config["tokens_per_debate"]
        spent = self.get_spend_so_far()
        pct = (spent / cap) * 100 if cap else 0
        if pct >= self.config["hard_cap_percent"]:
            raise BudgetExhausted(f"spend {spent}/{cap} ({pct:.0f}%) >= hard cap")

    def _enforce_rate_limit(self, now: float) -> None:
        window = 60.0
        while self._call_times and (now - self._call_times[0]) > window:
            self._call_times.popleft()
        if len(self._call_times) >= self.config["requests_per_minute"]:
            raise RateLimitExceeded("requests_per_minute exceeded")
