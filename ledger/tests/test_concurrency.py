import uuid
from concurrent.futures import ThreadPoolExecutor

import pytest
from django.db import connection

from ledger.models import Entry, Household
from ledger.services import append_entry, verify_chain


@pytest.mark.django_db(transaction=True)
def test_concurrent_appends_stay_contiguous():
    hh = Household.objects.create(name="Race")

    def work(i):
        try:
            append_entry(household=hh, author=f"t{i}", kind="update", issue_id=uuid.uuid4(), payload={"i": i})
        finally:
            connection.close()

    with ThreadPoolExecutor(8) as pool:
        list(pool.map(work, range(16)))  # re-raises any worker exception
    seqs = list(Entry.objects.filter(household=hh).order_by("seq").values_list("seq", flat=True))
    assert seqs == list(range(1, 17))
    assert verify_chain(hh).ok
