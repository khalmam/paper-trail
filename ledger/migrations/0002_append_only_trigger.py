from django.db import migrations

FORWARD = """
CREATE FUNCTION ledger_entry_immutable() RETURNS trigger AS $$
BEGIN
  RAISE EXCEPTION 'ledger_entry is append-only';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER ledger_entry_no_update_delete
BEFORE UPDATE OR DELETE ON ledger_entry
FOR EACH ROW EXECUTE FUNCTION ledger_entry_immutable();
"""
REVERSE = """
DROP TRIGGER ledger_entry_no_update_delete ON ledger_entry;
DROP FUNCTION ledger_entry_immutable();
"""


class Migration(migrations.Migration):
    dependencies = [("ledger", "0001_initial")]
    operations = [migrations.RunSQL(FORWARD, REVERSE)]
