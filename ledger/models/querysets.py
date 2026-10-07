from django.db.models import QuerySet

from ledger.exceptions import ImmutableEntryError


class AppendOnlyQuerySet(QuerySet):
    def update(self, **kwargs):
        raise ImmutableEntryError("Entries are append-only; add a correction entry instead.")

    def delete(self):
        raise ImmutableEntryError("Entries are append-only.")
