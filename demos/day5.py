from src.bank_account import BankAccount
from src.client import Client
from src.enums import Currency, Gender, TransactionType
from src.risk_analyzer import RiskAnalyzer
from src.transaction import Transaction
from src.transaction_processor import TransactionProcessor


def create_client(number: int) -> Client:
    return Client(
        first_name=f"Client{number}",
        last_name="Test",
        middle_name="User",
        birth_year=2000,
        passport=f"000000000{number}",
        gender=Gender.OTHER,
        phone=f"+7000000000{number}",
        email=f"client{number}@example.com",
    )


def create_transaction(
    amount: float,
    sender: BankAccount,
    receiver: BankAccount,
    hour: int = 12,
) -> Transaction:
    transaction = Transaction(
        transaction_type=TransactionType.TRANSFER,
        amount=amount,
        currency=sender.currency,
        sender=sender,
        receiver=receiver,
    )
    transaction.created_at = transaction.created_at.replace(hour=hour)
    return transaction


def run_demo() -> None:
    first_client = create_client(1)
    second_client = create_client(2)
    third_client = create_client(3)
    fourth_client = create_client(4)

    first_sender = BankAccount(first_client, Currency.RUB)
    first_own_receiver = BankAccount(first_client, Currency.RUB)
    external_receiver = BankAccount(second_client, Currency.RUB)
    second_sender = BankAccount(second_client, Currency.RUB)
    third_sender = BankAccount(third_client, Currency.RUB)
    fourth_sender = BankAccount(fourth_client, Currency.RUB)
    fourth_own_receiver = BankAccount(fourth_client, Currency.RUB)

    first_sender.deposit(100_000)
    second_sender.deposit(200_000)
    third_sender.deposit(10_000)

    scenarios = [
        (
            "Normal transaction",
            create_transaction(1000, first_sender, first_own_receiver),
        ),
        (
            "New receiver",
            create_transaction(2000, first_sender, external_receiver),
        ),
        (
            "Known receiver",
            create_transaction(2000, first_sender, external_receiver),
        ),
        (
            "Frequent transaction",
            create_transaction(2000, first_sender, external_receiver),
        ),
        (
            "Large transaction",
            create_transaction(150_000, second_sender, first_own_receiver),
        ),
        (
            "Night transaction",
            create_transaction(1000, third_sender, first_own_receiver, hour=2),
        ),
        (
            "Insufficient funds",
            create_transaction(1000, fourth_sender, fourth_own_receiver),
        ),
    ]

    processor = TransactionProcessor()
    processor.risk_analyzer = RiskAnalyzer(
        large_amount_limit=100_000,
        frequent_operations_limit=4,
    )

    print("=== Audit and risk analysis ===")
    for title, transaction in scenarios:
        processor.process(transaction)
        reason = transaction.rejection_reason or "-"
        print(f"{title}: {transaction.status.value}, reason={reason}")

    audit_log = processor.audit_log

    print("\n=== Suspicious operations ===")
    for entry in audit_log.get_suspicious_entries():
        print(
            f"{entry.level.value}: {entry.message}, transaction={entry.transaction_id}"
        )

    print("\n=== Client risk profiles ===")
    for client in (
        first_client,
        second_client,
        third_client,
        fourth_client,
    ):
        risk_level = audit_log.get_client_risk_profile(client.client_id)
        print(f"{client.full_name}: {risk_level.value}")

    print("\n=== Error statistics ===")
    for message, count in audit_log.get_error_statistics().items():
        print(f"{message}: {count}")

    print(f"\nAudit file: {audit_log.file_path}")


if __name__ == "__main__":
    run_demo()
