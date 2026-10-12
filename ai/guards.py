"""Spend protection for pay-per-call AI services. Per process: one server process = one cap."""
import threading
from collections.abc import Callable
from datetime import date


class BudgetExceeded(RuntimeError):
    pass


class CallBudget:
    def __init__(self, daily_limit: int, today: Callable[[], date] = date.today):
        self.daily_limit = daily_limit
        self._today = today
        self._day = today()
        self._used = 0
        self._lock = threading.Lock()

    def _roll(self) -> None:
        now = self._today()
        if now != self._day:
            self._day, self._used = now, 0

    @property
    def used(self) -> int:
        with self._lock:
            self._roll()
            return self._used

    def charge(self) -> None:
        with self._lock:
            self._roll()
            if self._used >= self.daily_limit:
                raise BudgetExceeded(f"The daily AI call limit of {self.daily_limit} was reached.")
            self._used += 1


def call_with_retries(fn: Callable, budget: CallBudget, max_attempts: int = 2,
                      retryable: tuple = (Exception,)):
    """Every attempt is charged. Running out of budget is never retried."""
    assert max_attempts >= 1
    last: Exception | None = None
    for _ in range(max_attempts):
        budget.charge()
        try:
            return fn()
        except BudgetExceeded:
            raise
        except retryable as exc:
            last = exc
    raise last
