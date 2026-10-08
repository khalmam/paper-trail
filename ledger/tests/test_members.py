import pytest

from ledger.services import authenticate_token, create_member

pytestmark = pytest.mark.django_db


def test_token_roundtrip(hh):
    member, raw = create_member(household=hh, display_name="Ibrahim", role="owner")
    assert raw != member.token_hash and raw not in member.token_hash
    assert authenticate_token(raw) == member
    assert authenticate_token("not-a-token") is None
