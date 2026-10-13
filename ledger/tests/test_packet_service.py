from datetime import date

import pytest

from ledger.services import add_update, evidence_packet, log_issue, record_landlord_contact

pytestmark = pytest.mark.django_db
TODAY = date(2026, 10, 11)


def two_issues(hh):
    log_issue(household=hh, author="Ibrahim", room="Bedroom", category="leak", description="drip")
    log_issue(household=hh, author="Ibrahim", room="Kitchen", category="pests", description="ants")


def test_packet_reports_intact_chain_and_head_hash(hh):
    two_issues(hh)
    record_landlord_contact(household=hh, author="Ibrahim", method="text", note="told him", room="kitchen")
    result = evidence_packet(hh, today=TODAY)
    assert result.integrity.ok and result.entry_count == 3
    assert result.head_hash == result.integrity.head_hash
    assert len(result.packet.issues) == 2


def test_room_filter_returns_one_issue(hh):
    two_issues(hh)
    result = evidence_packet(hh, room="bedroom", today=TODAY)
    assert [i.summary.room for i in result.packet.issues] == ["bedroom"]
    assert result.entry_count == 2  # integrity still covers the whole log


def test_packet_names_the_altered_entry(hh, tamper):
    two_issues(hh)
    add_update(household=hh, author="Ibrahim", note="worse", room="bedroom")
    tamper("UPDATE ledger_entry SET payload = jsonb_set(payload, '{room}', '\"garden\"') WHERE seq = 1")
    result = evidence_packet(hh, today=TODAY)
    assert not result.integrity.ok and result.integrity.bad_seq == 1


def test_empty_household_has_an_empty_packet(hh):
    result = evidence_packet(hh, today=TODAY)
    assert result.packet.issues == [] and result.head_hash is None and result.integrity.ok


def test_packet_is_json_ready(hh):
    import json
    two_issues(hh)
    data = json.loads(json.dumps(evidence_packet(hh, today=TODAY).to_dict()))
    assert data["integrity"]["ok"] and data["head_hash"] and "notice" in data
