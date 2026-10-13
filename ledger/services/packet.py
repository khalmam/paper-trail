from dataclasses import dataclass
from datetime import date

from django.conf import settings
from django.utils import timezone

from engine.packet import Packet, build_packet
from engine.types import EntryView
from ledger.domain.chain import VerifyResult
from ledger.models import Entry, Household

from .lookup import find_issue
from .verify import verify_chain


@dataclass(frozen=True)
class EvidencePacket:
    packet: Packet
    integrity: VerifyResult
    head_hash: str | None   # hash of the newest entry; the anchor to keep outside the database
    entry_count: int

    def to_dict(self) -> dict:
        i = self.integrity
        return {
            **self.packet.to_dict(),
            "integrity": {"ok": i.ok, "verified": i.verified, "bad_seq": i.bad_seq, "reason": i.reason},
            "head_hash": self.head_hash,
            "entry_count": self.entry_count,
        }


def evidence_packet(household: Household, room: str | None = None,
                    today: date | None = None) -> EvidencePacket:
    """Full packet for the household, or only the latest issue in `room`."""
    today = today or timezone.now().date()
    issue_id = str(find_issue(household, room).issue_id) if room else None
    entries = list(Entry.objects.filter(household=household).order_by("seq"))
    views = [
        EntryView(seq=e.seq, kind=e.kind, issue_id=str(e.issue_id), author=e.author,
                  created_at=e.created_at, payload=e.payload)
        for e in entries
    ]
    return EvidencePacket(
        packet=build_packet(views, today, settings.RECURRENCE_WINDOW_DAYS, issue_id),
        integrity=verify_chain(household),
        head_hash=entries[-1].hash if entries else None,
        entry_count=len(entries),
    )
