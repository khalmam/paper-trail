import pytest

from ledger.domain.corrections import validate_correction


@pytest.mark.parametrize("kind,field,value", [
    ("issue_logged", "category", "plumbing"),
    ("issue_logged", "happened_on", "yesterday"),
    ("issue_logged", "method", "text"),
    ("landlord_contact", "method", "pigeon"),
    ("deadline_set", "deadline_date", "2026-13-40"),
    ("issue_logged", "room", "   "),
    ("resolved", "note", "x"),
    ("correction", "field", "x"),
])
def test_bad_corrections_are_rejected(kind, field, value):
    with pytest.raises(ValueError):
        validate_correction(kind, field, value)


def test_good_values_are_cleaned():
    assert validate_correction("issue_logged", "room", "  Hallway ") == "hallway"
    assert validate_correction("issue_logged", "category", "MOLD") == "mold"
    assert validate_correction("landlord_contact", "contacted_on", "2026-10-05") == "2026-10-05"
