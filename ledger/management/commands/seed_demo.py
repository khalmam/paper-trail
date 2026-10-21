from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.utils import timezone

from ledger.demo import DEMO_HOUSEHOLD
from ledger.services import append_entry, create_member, get_or_create_household


class Command(BaseCommand):
    help = "DEV ONLY: wipe everything and load a fake household with backdated entries."

    def add_arguments(self, parser):
        parser.add_argument(
            "--allow-wipe-demo-server", action="store_true",
            help="Permit this wipe with DEBUG off. Only for the public demo server.")

    def handle(self, *args, **options):
        if not settings.DEBUG:
            if not options["allow_wipe_demo_server"]:
                raise CommandError("seed_demo only runs with DEBUG on (or with --allow-wipe-demo-server)")
            from ledger.models import Household
            others = Household.objects.exclude(name=DEMO_HOUSEHOLD).count()
            if others:
                raise CommandError(f"Refusing to wipe: {others} household(s) other than the demo exist.")
        with connection.cursor() as c:  # TRUNCATE is not blocked by the row-level trigger
            c.execute("TRUNCATE ledger_entry, ledger_member, ledger_household RESTART IDENTITY CASCADE")
        now = timezone.now()
        hh = get_or_create_household(DEMO_HOUSEHOLD)
        _, owner_token = create_member(household=hh, display_name="Ibrahim", role="owner",
                                       token=getattr(settings, "DEMO_TOKEN", None) or None)
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
        newest = leak(14, "Ibrahim", "Ceiling is leaking again")
        append_entry(
            household=hh, author="Ibrahim", kind="landlord_contact", issue_id=newest.issue_id,
            at=now - timedelta(days=13),
            payload={"room": "bedroom", "method": "text", "note": "Texted the landlord that the leak is back",
                     "contacted_on": (now - timedelta(days=13)).date().isoformat()},
        )

        def deadline(set_days_ago, author, due_days_ago):
            append_entry(
                household=hh, author=author, kind="deadline_set", issue_id=newest.issue_id,
                at=now - timedelta(days=set_days_ago),
                payload={"room": "bedroom", "what": "fix the ceiling",
                         "deadline_date": (now - timedelta(days=due_days_ago)).date().isoformat()},
            )

        deadline(12, "Ibrahim", 8)  # the landlord promised a date, and it lapsed
        deadline(11, "Amina", 9)    # the roommates recorded different dates
        self.stdout.write(self.style.SUCCESS("Seeded 7 entries (fake data)."))
        self.stdout.write(f"Ibrahim token: {owner_token}")
        self.stdout.write(f"Amina token:   {mate_token}")
