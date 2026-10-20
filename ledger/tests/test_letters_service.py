from datetime import date

import pytest

from ledger.exceptions import NoSuchIssue
from ledger.models import Entry
from ledger.services import (confirm_letter_sent, draft_letter, evidence_packet, log_issue,
                             record_landlord_contact, set_deadline)

pytestmark = pytest.mark.django_db
TODAY = date(2026, 10, 11)


def story(hh):
    log_issue(household=hh, author="Ibrahim", room="Bedroom", category="leak", description="ceiling drips")
    record_landlord_contact(household=hh, author="Ibrahim", method="text", note="told him", room="bedroom")
    set_deadline(household=hh, author="Ibrahim", deadline="2026-10-03", what="fix the ceiling", room="bedroom")


def test_drafting_writes_nothing_to_the_ledger(hh):
    story(hh)
    before = Entry.objects.filter(household=hh).count()
    letter = draft_letter(hh, "bedroom", today=TODAY)
    assert "ceiling drips" in letter.body and "2026-10-03" in letter.body
    assert Entry.objects.filter(household=hh).count() == before


def test_confirming_adds_a_letter_sent_entry_and_the_chain_stays_intact(hh):
    story(hh)
    entry = confirm_letter_sent(household=hh, author="Ibrahim", room="bedroom", sent_on="2026-10-10")
    assert entry.kind == "letter_sent" and entry.payload["sent_on"] == "2026-10-10"
    assert evidence_packet(hh, today=TODAY).integrity.ok


def test_bad_method_bad_date_and_no_issue_are_refused(hh):
    with pytest.raises(NoSuchIssue):
        draft_letter(hh, today=TODAY)
    story(hh)
    with pytest.raises(ValueError):
        confirm_letter_sent(household=hh, author="Ibrahim", method="pigeon")
    with pytest.raises(ValueError):
        confirm_letter_sent(household=hh, author="Ibrahim", sent_on="soon")
