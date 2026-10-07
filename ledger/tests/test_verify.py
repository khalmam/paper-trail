import pytest

from ledger.models import Household
from ledger.services import verify_chain

pytestmark = pytest.mark.django_db


def test_verify_ok_and_empty(hh, chain):
    r = verify_chain(hh)
    assert r.ok and r.checked == 4 and r.head_hash == chain[-1].hash
    assert verify_chain(Household.objects.create(name="empty")).ok


def test_tamper_content_names_exact_entry(hh, chain, tamper):
    tamper("UPDATE ledger_entry SET payload = jsonb_set(payload, '{note}', '\"nothing happened\"') "
           "WHERE id=%s", [chain[1].pk])
    r = verify_chain(hh)
    assert not r.ok and r.bad_seq == 2 and "altered" in r.reason


def test_tamper_and_rehash_caught_at_next_link(hh, chain, tamper):
    tamper("UPDATE ledger_entry SET author='mallory', hash=%s WHERE id=%s", ["a" * 64, chain[1].pk])
    r = verify_chain(hh)
    assert not r.ok and r.bad_seq in (2, 3)


def test_deleted_entry_detected(hh, chain, tamper):
    tamper("DELETE FROM ledger_entry WHERE id=%s", [chain[1].pk])
    r = verify_chain(hh)
    assert not r.ok and r.bad_seq == 2 and "missing" in r.reason
