import json

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction

from ledger.demo import DEMO_HOUSEHOLD

TRIGGER = "ledger_entry_no_update_delete"


class Command(BaseCommand):
    help = "DEV ONLY: simulate an attacker with database access editing one entry."

    def add_arguments(self, parser):
        parser.add_argument("--seq", type=int, default=1)

    def handle(self, *args, seq, **options):
        if not settings.DEBUG:
            raise CommandError("tamper_demo only runs with DEBUG on")
        edit = json.dumps({"description": "nothing happened", "note": "nothing happened"})
        with transaction.atomic(), connection.cursor() as c:  # atomic: trigger is always re-enabled
            c.execute(f"ALTER TABLE ledger_entry DISABLE TRIGGER {TRIGGER}")
            c.execute(
                "UPDATE ledger_entry SET payload = payload || %s::jsonb WHERE seq = %s AND household_id = "
                "(SELECT id FROM ledger_household WHERE name = %s)",
                [edit, seq, DEMO_HOUSEHOLD],
            )
            c.execute(f"ALTER TABLE ledger_entry ENABLE TRIGGER {TRIGGER}")
        self.stdout.write(self.style.WARNING(f"Entry {seq} was edited behind the app's back."))
