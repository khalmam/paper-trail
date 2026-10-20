from datetime import date

from ai.interface import ParsedIssue
from ai.validate import parse_checked, weekday_date

TUESDAY = date(2026, 10, 20)


class Stub:
    def __init__(self, deadline):
        self.deadline = deadline

    def parse_issue(self, utterance, today):
        return ParsedIssue("bedroom", "leak", utterance, deadline_on=self.deadline)


def test_a_named_weekday_is_computed_by_code():
    assert weekday_date("he promised to fix it by Friday", TUESDAY) == "2026-10-23"
    assert weekday_date("by Tuesday", TUESDAY) == "2026-10-27"  # never today
    assert weekday_date("by Monday", TUESDAY) == "2026-10-26"


def test_no_weekday_or_two_weekdays_means_no_override():
    assert weekday_date("by the 30th", TUESDAY) is None
    assert weekday_date("Friday or Saturday", TUESDAY) is None


def test_the_models_off_by_one_date_is_corrected():
    parsed = parse_checked(Stub("2026-10-24"), "he promised Friday", TUESDAY)
    assert parsed.deadline_on == "2026-10-23"


def test_a_stated_calendar_date_is_left_alone():
    assert parse_checked(Stub("2026-10-30"), "he said by the 30th", TUESDAY).deadline_on == "2026-10-30"
