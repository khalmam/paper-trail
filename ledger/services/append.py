import json
import uuid

from django.db import transaction
from django.utils import timezone

from ledger.domain.chain import GENESIS_HASH, compute_hash
from ledger.models import Entry, Household


def append_entry(*, household: Household, author: str, kind: str, payload: dict, issue_id=None) -> Entry:
    """Sync on purpose: atomic() + select_for_update() are not async-safe.
    Async callers go through mcp_server.runner.run_db."""
    payload = json.loads(json.dumps(payload))  # force JSON-clean before hashing
    with transaction.atomic():
        # Lock the household row (not "the last entry") so the very first append is serialized too.
        Household.objects.select_for_update().get(pk=household.pk)
        last = Entry.objects.filter(household=household).order_by("-seq").first()
        seq = last.seq + 1 if last else 1
        prev_hash = last.hash if last else GENESIS_HASH
        issue_id = issue_id or uuid.uuid4()
        created_at = timezone.now()
        digest = compute_hash(
            household_id=household.pk, seq=seq, issue_id=issue_id, kind=kind,
            author=author, payload=payload, created_at=created_at, prev_hash=prev_hash,
        )
        return Entry.objects.create(
            household=household, seq=seq, issue_id=issue_id, kind=kind, author=author,
            payload=payload, created_at=created_at, prev_hash=prev_hash, hash=digest,
        )
