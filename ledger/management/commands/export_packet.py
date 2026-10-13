from pathlib import Path

from django.core.management.base import BaseCommand

from ledger.demo import DEMO_HOUSEHOLD
from ledger.models import Household
from ledger.services import evidence_packet
from render.packet_html import render_packet


class Command(BaseCommand):
    help = "Write the household's evidence packet as one printable HTML file."

    def add_arguments(self, parser):
        parser.add_argument("--household", default=DEMO_HOUSEHOLD)
        parser.add_argument("--room", default=None, help="Only the latest issue in this room")
        parser.add_argument("--out", default="out/packet.html")

    def handle(self, *args, household, room, out, **options):
        result = evidence_packet(Household.objects.get(name=household), room)
        path = Path(out)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_packet(result.to_dict()), encoding="utf-8")
        verdict = "record check passed" if result.integrity.ok else "RECORD CHECK FAILED"
        self.stdout.write(self.style.SUCCESS(f"Wrote {path} ({len(result.packet.issues)} issues, {verdict})"))
