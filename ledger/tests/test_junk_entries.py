import pytest

from ledger.models import Entry
from ledger.services import (confirm_letter_sent, draft_letter, log_issue,
                             record_landlord_contact, set_deadline)
from datetime import date

pytestmark = pytest.mark.django_db
TODAY = date(2026, 10, 11)


def story(hh):
    first = log_issue(household=hh, author="Ibrahim", room="Bedroom", category="leak",
                      description="ceiling drips", happened_on="2026-10-01")
    record_landlord_contact(household=hh, author="Ibrahim", method="text", note="told him", room="bedroom")
    set_deadline(household=hh, author="Ibrahim", deadline="2026-10-03", what="fix the ceiling", room="bedroom")
    return first


def test_placeholder_rooms_and_descriptions_never_reach_the_chain(hh):
    for room, text in (("<unknown>", "ceiling drips"), ("unknown", "x"), ("  ", "x"), ("kitchen", "<UNKNOWN>")):
        with pytest.raises(ValueError):
            log_issue(household=hh, author="Ibrahim", room=room, category="leak", description=text)
    assert Entry.objects.filter(household=hh).count() == 0


def test_default_letter_is_about_the_most_urgent_issue_not_the_newest(hh):
    first = story(hh)
    log_issue(household=hh, author="Ibrahim", room="kitchen", category="leak",
              description="sink drips", happened_on="2026-10-09")
    letter = draft_letter(hh, today=TODAY)
    assert "ceiling drips" in letter.body and "sink drips" not in letter.body
    sent = confirm_letter_sent(household=hh, author="Ibrahim")
    assert sent.issue_id == first.issue_id
