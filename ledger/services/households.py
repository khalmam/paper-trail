from ledger.models import Household


def get_or_create_household(name: str) -> Household:
    household, _ = Household.objects.get_or_create(name=name)
    return household
