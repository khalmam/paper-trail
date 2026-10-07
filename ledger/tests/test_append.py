import pytest
from django.db import IntegrityError, transaction

from ledger.domain.chain import GENESIS_HASH
from ledger.models import Entry

pytestmark = pytest.mark.django_db


def test_links_and_sequence(chain):
    assert [e.seq for e in chain] == [1, 2, 3, 4]
    assert chain[0].prev_hash == GENESIS_HASH
    for a, b in zip(chain, chain[1:]):
        assert b.prev_hash == a.hash


def test_duplicate_seq_rejected(hh, chain):
    with pytest.raises(IntegrityError), transaction.atomic():
        Entry.objects.create(household=hh, seq=1, issue_id=chain[0].issue_id, kind="update",
                             author="x", payload={}, created_at=chain[0].created_at,
                             prev_hash=GENESIS_HASH, hash="f" * 64)
