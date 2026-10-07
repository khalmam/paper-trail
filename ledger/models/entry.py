import uuid

from django.db import models

from ledger.exceptions import ImmutableEntryError

from .household import Household
from .querysets import AppendOnlyQuerySet


class Entry(models.Model):
    class Kind(models.TextChoices):
        ISSUE_LOGGED = "issue_logged"
        UPDATE = "update"
        LANDLORD_CONTACT = "landlord_contact"
        DEADLINE_SET = "deadline_set"
        LETTER_SENT = "letter_sent"
        CORRECTION = "correction"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    household = models.ForeignKey(Household, on_delete=models.PROTECT, related_name="entries")
    seq = models.PositiveIntegerField()
    issue_id = models.UUIDField(db_index=True)
    kind = models.CharField(max_length=32, choices=Kind.choices)
    author = models.CharField(max_length=80)
    payload = models.JSONField()
    created_at = models.DateTimeField()  # server-set in services.append
    prev_hash = models.CharField(max_length=64)
    hash = models.CharField(max_length=64)

    objects = AppendOnlyQuerySet.as_manager()

    class Meta:
        ordering = ["household_id", "seq"]
        constraints = [
            models.UniqueConstraint(fields=["household", "seq"], name="uniq_household_seq"),
        ]

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ImmutableEntryError("Entries are append-only; add a correction entry instead.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ImmutableEntryError("Entries are append-only.")
