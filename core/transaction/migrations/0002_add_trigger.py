from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('transaction', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE OR REPLACE FUNCTION prevent_transactionledger_modification()
            RETURNS trigger AS $$
            BEGIN
                RAISE EXCEPTION 'TransactionLedger is immutable. Cannot UPDATE or DELETE.';
                RETURN NULL;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER transactionledger_no_update_delete
            BEFORE UPDATE OR DELETE ON transaction_transactionledger
            FOR EACH ROW
            EXECUTE FUNCTION prevent_transactionledger_modification();
            """,
            reverse_sql="""
            DROP TRIGGER IF EXISTS transactionledger_no_update_delete ON transaction_transactionledger;
            DROP FUNCTION IF EXISTS prevent_transactionledger_modification();
            """
        ),
    ]