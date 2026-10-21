import pytest
from django.core.management import call_command

from ledger.demo import DEMO_HOUSEHOLD
from ledger.models import Household
from ledger.services import authenticate_token, evidence_packet

pytestmark = pytest.mark.django_db


def seeded(settings, token=None):
    settings.DEBUG = True
    settings.DEMO_TOKEN = token
    call_command("seed_demo")
    return Household.objects.get(name=DEMO_HOUSEHOLD)


def test_the_demo_story_has_a_lapsed_deadline_a_conflict_and_a_letter_step(settings):
    result = evidence_packet(seeded(settings))
    assert result.integrity.ok and result.entry_count == 7
    late = [i for i in result.packet.issues if i.summary.overdue]
    assert len(late) == 1
    assert late[0].recurrence.count == 3
    assert late[0].next_step.action == "letter"
    assert len(late[0].conflicts) == 1


def test_a_configured_demo_token_belongs_to_ibrahim(settings):
    seeded(settings, token="demo-token-xyz")
    assert authenticate_token("demo-token-xyz").display_name == "Ibrahim"
