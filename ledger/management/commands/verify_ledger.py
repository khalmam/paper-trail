from django.core.management.base import BaseCommand

from ledger.demo import DEMO_HOUSEHOLD
from ledger.models import Household
from ledger.services import verify_chain


class Command(BaseCommand):
    help = "Verify the demo household's hash chain and print the result."

    def handle(self, *args, **options):
        r = verify_chain(Household.objects.get(name=DEMO_HOUSEHOLD))
        if r.ok:
            self.stdout.write(self.style.SUCCESS(f"OK: all {r.verified} entries intact. head={r.head_hash[:12]}"))
        else:
            self.stdout.write(self.style.ERROR(f"BROKEN at entry {r.bad_seq}: {r.reason}"))
