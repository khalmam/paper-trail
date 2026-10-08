import hashlib
import secrets

from ledger.models import Household, Member


def _hash(raw: str) -> str:
    # Plain SHA-256 is fine here: tokens are 192 random bits, not human passwords.
    return hashlib.sha256(raw.encode()).hexdigest()


def create_member(*, household: Household, display_name: str, role: str = Member.Role.MEMBER) -> tuple[Member, str]:
    """Returns (member, raw_token). The raw token is shown once and never stored."""
    raw = secrets.token_urlsafe(24)
    member = Member.objects.create(
        household=household, display_name=display_name, role=role, token_hash=_hash(raw)
    )
    return member, raw


def authenticate_token(raw: str) -> Member | None:
    return Member.objects.select_related("household").filter(token_hash=_hash(raw)).first()
