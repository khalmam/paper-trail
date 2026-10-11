"""The engine must not import the ledger, so this test catches the two drifting apart."""
from engine import kinds
from ledger.models import Entry


def test_engine_kinds_exist_in_ledger():
    engine_kinds = {v for k, v in vars(kinds).items() if k.isupper()}
    assert engine_kinds <= set(Entry.Kind.values)
