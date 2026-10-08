import uuid

from django.db import models

from .household import Household


class Member(models.Model):
    class Role(models.TextChoices):
        OWNER = "owner"
        MEMBER = "member"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    household = models.ForeignKey(Household, on_delete=models.PROTECT, related_name="members")
    display_name = models.CharField(max_length=80)
    role = models.CharField(max_length=16, choices=Role.choices, default=Role.MEMBER)
    token_hash = models.CharField(max_length=64, unique=True)  # sha256 of the raw token; raw is never stored
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["household", "display_name"], name="uniq_member_name"),
        ]

    def __str__(self):
        return f"{self.display_name} ({self.role})"
