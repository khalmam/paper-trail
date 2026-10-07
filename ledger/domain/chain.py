"""Pure hash-chain logic. No Django imports: trivially unit-testable."""
import hashlib
import json
from dataclasses import dataclass
from datetime import timezone

GENESIS_HASH = "0" * 64


def canonical_bytes(*, household_id, seq, issue_id, kind, author, payload, created_at, prev_hash) -> bytes:
    """Deterministic serialization. Keep floats out of payloads (jsonb round-trips can differ)."""
    body = {
        "household": str(household_id),
        "seq": seq,
        "issue": str(issue_id),
        "kind": kind,
        "author": author,
        "payload": payload,
        "created_at": created_at.astimezone(timezone.utc).isoformat(),
        "prev_hash": prev_hash,
    }
    return json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def compute_hash(**fields) -> str:
    return hashlib.sha256(canonical_bytes(**fields)).hexdigest()


@dataclass(frozen=True)
class VerifyResult:
    ok: bool
    checked: int
    head_hash: str
    bad_seq: int | None = None
    reason: str | None = None
