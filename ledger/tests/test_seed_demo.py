import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

pytestmark = pytest.mark.django_db


def test_seed_refuses_in_production_without_the_explicit_flag(settings):
    settings.DEBUG = False
    with pytest.raises(CommandError, match="DEBUG"):
        call_command("seed_demo")


def test_seed_with_the_flag_works_on_a_demo_only_database(settings):
    settings.DEBUG = False
    call_command("seed_demo", "--allow-wipe-demo-server")
