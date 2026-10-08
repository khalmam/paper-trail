from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.utils import timezone

from ledger.demo import DEMO_HOUSEHOLD
from ledger.services import append_entry, create_member, get_or_create_household


class Command(BaseCommand):
    help = "DEV ONLY: wipe everything and load a fake household with backdated entries."

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("seed_demo only runs with DEBUG on")
        with connection.cursor() as c:  # TRUNCATE is not blocked by the row-level trigger
            c.execute("TRUNCATE ledger_entry, ledger_member, ledger_household RESTART IDENTITY CASCADE")
        now = timezone.now()
        hh = get_or_create_household(DEMO_HOUSEHOLD)
        _, owner_token = create_member(household=hh, display_name="Ibrahim", role="owner")
        _, mate_token = create_member(household=hh, display_name="Amina")

        def leak(days_ago, author, text):
            when = now - timedelta(days=days_ago)
            return append_entry(
                household=hh, author=author, kind="issue_logged", at=when,
                payload={"room": "bedroom", "category": "leak", "description": text,
                         "happened_on": when.date().isoformat()},
            )

        first = leak(62, "Ibrahim", "Ceiling dripping near the window")
        append_entry(
            household=hh, author="Ibrahim", kind="landlord_contact", issue_id=first.issue_id,
            at=now - timedelta(days=61),
            payload={"room": "bedroom", "method": "text", "note": "Texted the landlord about the leak"},
        )
        leak(31, "Amina", "Stain spreading, drips after rain")
        leak(2, "Ibrahim", "Ceiling is leaking again")
        self.stdout.write(self.style.SUCCESS("Seeded 4 entries (fake data)."))
        self.stdout.write(f"Ibrahim token: {owner_token}")
        self.stdout.write(f"Amina token:   {mate_token}")
