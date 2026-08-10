from datetime import datetime, timedelta

from demos.common import create_fake_client
from src.bank_account import BankAccount
from src.enums import AccountStatus, Currency, TransactionType
from src.premium_account import PremiumAccount
from src.risk_analyzer import RiskAnalyzer
from src.transaction import Transaction
from src.transaction_processor import TransactionProcessor
from src.transaction_queue import TransactionQueue


def create_transactions() -> list[Transaction]:
    first_client = create_fake_client()
    second_client = create_fake_client()

    rub_sender = BankAccount(first_client, Currency.RUB)
    rub_receiver = BankAccount(second_client, Currency.RUB)
    own_rub_receiver = BankAccount(first_client, Currency.RUB)
    usd_sender = BankAccount(first_client, Currency.USD)
    usd_receiver = BankAccount(second_client, Currency.USD)
    frozen_receiver = BankAccount(
        second_client,
        Currency.RUB,
        status=AccountStatus.FROZEN,
    )
    poor_sender = BankAccount(first_client, Currency.RUB)
    premium_sender = PremiumAccount(
        first_client,
        Currency.RUB,
        withdrawal_limit=5000,
        overdraft_limit=5000,
        fee=50,
    )

    rub_sender.deposit(50_000)
    usd_sender.deposit(500)

    transactions = [
        Transaction(
            TransactionType.TRANSFER, 1000, Currency.RUB, rub_sender, rub_receiver
        ),
        Transaction(
            TransactionType.TRANSFER, 2000, Currency.RUB, rub_sender, rub_receiver
        ),
        Transaction(
            TransactionType.TRANSFER,
            3000,
            Currency.RUB,
            rub_sender,
            rub_receiver,
            scheduled_at=datetime.now().astimezone() - timedelta(minutes=1),
        ),
        Transaction(
            TransactionType.TRANSFER, 4000, Currency.RUB, rub_sender, rub_receiver
        ),
        Transaction(
            TransactionType.TRANSFER, 9000, Currency.RUB, rub_sender, usd_receiver
        ),
        Transaction(
            TransactionType.TRANSFER, 100, Currency.USD, usd_sender, rub_receiver
        ),
        Transaction(
            TransactionType.TRANSFER, 500, Currency.RUB, rub_sender, own_rub_receiver
        ),
        Transaction(
            TransactionType.TRANSFER, 1000, Currency.RUB, premium_sender, rub_receiver
        ),
        Transaction(
            TransactionType.TRANSFER, 100, Currency.RUB, rub_sender, frozen_receiver
        ),
        Transaction(
            TransactionType.TRANSFER, 1000, Currency.RUB, poor_sender, rub_receiver
        ),
    ]

    for transaction in transactions:
        transaction.created_at = transaction.created_at.replace(hour=12)

    return transactions


def run_demo() -> None:
    transactions = create_transactions()
    queue = TransactionQueue()
    processor = TransactionProcessor(
        risk_analyzer=RiskAnalyzer(
            large_amount_limit=1_000_000,
            frequent_operations_limit=100,
        )
    )

    for transaction in transactions:
        queue.add(transaction)

    queue.prioritize(transactions[4].transaction_id, priority=10)
    queue.cancel(transactions[3].transaction_id)

    while True:
        transaction = queue.get_next()

        if transaction is None:
            break

        processor.process(transaction)

    print("=== Transaction processing ===")
    for transaction in transactions:
        reason = transaction.rejection_reason or "-"
        print(
            f"{transaction.transaction_id}: "
            f"{transaction.status.value}, "
            f"attempts={transaction.attempts}, "
            f"fee={transaction.fee:.2f}, "
            f"reason={reason}"
        )

    print(f"Recorded errors: {len(processor.errors)}")


if __name__ == "__main__":
    run_demo()
