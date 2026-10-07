import pytest
from django.db import DatabaseError, connection, transaction

from ledger.exceptions import ImmutableEntryError
from ledger.models import Entry

pytestmark = pytest.mark.django_db


def test_orm_blocks_update_and_delete(hh, chain):
    e = Entry.objects.get(pk=chain[0].pk)
    e.author = "mallory"
    with pytest.raises(ImmutableEntryError):
        e.save()
    with pytest.raises(ImmutableEntryError):
        e.delete()
    with pytest.raises(ImmutableEntryError):
        Entry.objects.filter(household=hh).update(author="x")
    with pytest.raises(ImmutableEntryError):
        Entry.objects.filter(household=hh).delete()


def test_db_trigger_blocks_raw_sql(chain):
    with pytest.raises(DatabaseError), transaction.atomic():
        with connection.cursor() as c:
            c.execute("UPDATE ledger_entry SET author='x' WHERE id=%s", [chain[0].pk])
