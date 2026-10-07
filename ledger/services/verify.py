from ledger.domain.chain import GENESIS_HASH, VerifyResult, compute_hash
from ledger.models import Entry, Household


def verify_chain(household: Household) -> VerifyResult:
    prev_hash, expected = GENESIS_HASH, 1
    for e in Entry.objects.filter(household=household).order_by("seq").iterator():
        if e.seq != expected:
            return VerifyResult(False, expected - 1, prev_hash, expected,
                                f"Entry {expected} is missing (sequence jumps to {e.seq}).")
        recomputed = compute_hash(
            household_id=e.household_id, seq=e.seq, issue_id=e.issue_id, kind=e.kind,
            author=e.author, payload=e.payload, created_at=e.created_at, prev_hash=e.prev_hash,
        )
        if recomputed != e.hash:
            return VerifyResult(False, e.seq - 1, prev_hash, e.seq,
                                f"Entry {e.seq} was altered: its contents no longer match its hash.")
        if e.prev_hash != prev_hash:
            return VerifyResult(False, e.seq - 1, prev_hash, e.seq,
                                f"Entry {e.seq} does not link to entry {e.seq - 1}: one of them was altered.")
        prev_hash, expected = e.hash, e.seq + 1
    return VerifyResult(True, expected - 1, prev_hash)
