import json
from datetime import date, datetime, timezone

from engine import kinds
from engine.packet import NOTICE, build_packet
from engine.types import EntryView

TODAY = date(2026, 10, 11)
T = datetime(2026, 10, 1, 9, tzinfo=timezone.utc)


def e(seq, kind, issue, author="Ibrahim", **payload):
    return EntryView(seq, kind, issue, author, T, payload)


def opener(seq, issue, when="2026-10-01", room="bedroom", author="Ibrahim"):
    return e(seq, kinds.ISSUE_LOGGED, issue, author, room=room, category="leak",
             description="drip", happened_on=when)


def test_one_section_per_issue_open_first():
    entries = [opener(1, "A"), e(2, kinds.RESOLVED, "A"), opener(3, "B", room="kitchen")]
    packet = build_packet(entries, TODAY)
    assert [i.summary.issue_id for i in packet.issues] == ["B", "A"]
    assert packet.issues[1].next_step.action == "none"


def test_sections_carry_the_rule_results():
    entries = [
        opener(1, "A"),
        e(2, kinds.LANDLORD_CONTACT, "A", method="text", contacted_on="2026-10-02", note="told"),
        e(3, kinds.DEADLINE_SET, "A", deadline_date="2026-10-03", what="fix"),
    ]
    [item] = build_packet(entries, TODAY).issues
    assert item.summary.overdue and item.next_step.action == "letter"
    assert item.completeness.percent == 60
    assert [t.seq for t in item.timeline.items] == [1, 2, 3]


def test_recurrence_and_conflicts_attach_to_the_right_issue():
    entries = [
        opener(1, "A", when="2026-09-20"), opener(2, "B", when="2026-10-05"),
        e(3, kinds.DEADLINE_SET, "B", "Ibrahim", deadline_date="2026-10-10", what="fix"),
        e(4, kinds.DEADLINE_SET, "B", "Amina", deadline_date="2026-10-15", what="fix"),
    ]
    by_id = {i.summary.issue_id: i for i in build_packet(entries, TODAY).issues}
    assert by_id["A"].recurrence.count == 2 and by_id["B"].recurrence.count == 2
    assert by_id["A"].conflicts == () and len(by_id["B"].conflicts) == 1


def test_filter_to_one_issue():
    entries = [opener(1, "A"), opener(2, "B", room="kitchen")]
    packet = build_packet(entries, TODAY, issue_id="B")
    assert [i.summary.issue_id for i in packet.issues] == ["B"]
    assert build_packet(entries, TODAY, issue_id="nope").issues == []


def test_packet_is_json_ready_and_carries_the_notice():
    packet = build_packet([opener(1, "A")], TODAY)
    data = json.loads(json.dumps(packet.to_dict()))
    assert data["notice"] == NOTICE and data["generated_on"] == "2026-10-11"
    assert "not legal advice" in NOTICE.lower()


def test_notice_makes_no_promises():
    text = NOTICE.lower()
    for word in ("guarantee", "proves", "entitled", "must", "will win"):
        assert word not in text
