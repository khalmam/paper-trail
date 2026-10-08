class ImmutableEntryError(Exception):
    """Raised on any attempt to modify or delete a ledger entry."""


class NoSuchIssue(ValueError):
    """No logged issue matches the request."""
