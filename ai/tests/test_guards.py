from datetime import date, timedelta

import pytest

from ai.guards import BudgetExceeded, CallBudget, call_with_retries


def test_daily_limit_then_rollover():
    day = [date(2026, 10, 11)]
    budget = CallBudget(2, today=lambda: day[0])
    budget.charge()
    budget.charge()
    with pytest.raises(BudgetExceeded):
        budget.charge()
    day[0] += timedelta(days=1)
    budget.charge()
    assert budget.used == 1


def test_retries_stop_at_the_attempt_limit():
    calls = []

    def always_fails():
        calls.append(1)
        raise TimeoutError("boom")

    budget = CallBudget(100)
    with pytest.raises(TimeoutError):
        call_with_retries(always_fails, budget, max_attempts=3)
    assert len(calls) == 3 and budget.used == 3


def test_success_is_charged_once():
    budget = CallBudget(10)
    assert call_with_retries(lambda: "ok", budget) == "ok" and budget.used == 1


def test_budget_exhaustion_is_never_retried():
    budget = CallBudget(1)
    budget.charge()
    calls = []
    with pytest.raises(BudgetExceeded):
        call_with_retries(lambda: calls.append(1), budget, max_attempts=5)
    assert calls == []
