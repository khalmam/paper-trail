import pytest
from django.db import connection

from ledger.models import Household
from ledger.services import append_entry


@pytest.fixture
def hh(db):
    return Household.objects.create(name="Test flat")


@pytest.fixture
def chain(hh):
    return [
        append_entry(household=hh, author="ibrahim", kind="issue_logged",
                     payload={"room": "bedroom", "category": "leak", "note": f"leak {i}"})
        for i in range(4)
    ]


@pytest.fixture
def tamper(db):
    """Simulates a DBA/attacker: disables the trigger (DDL rolls back with the test) then runs SQL."""
    def run(sql, params=()):
        with connection.cursor() as c:
            c.execute("SET CONSTRAINTS ALL IMMEDIATE")
            c.execute("ALTER TABLE ledger_entry DISABLE TRIGGER ledger_entry_no_update_delete")
            c.execute(sql, params)
    return run
