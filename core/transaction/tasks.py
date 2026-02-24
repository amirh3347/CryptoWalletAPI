from celery import shared_task

from transaction.models import TransactionLedger


@shared_task
def look_for_high_amount_transactions(transaction_id):
    transaction = TransactionLedger.objects.get(id=transaction_id)
    if transaction.amount > 100:
        message = f"""
            warning to monitoring team!!
            a high amount transaction applied just now.
            make sure to check.
            from wallet: {transaction.wallet_from.wallet_address}
            to wallet: {transaction.wallet_to.wallet_address}
            with currency: {transaction.currency}
            and amount of: {transaction.amount} 
        """
        print(message, flush=True)
