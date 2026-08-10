from demos.simulation import run_simulation
from src.bank import Bank
from src.client import Client
from src.enums import Currency, TransactionStatus
from src.transaction import Transaction
from src.transaction_processor import TransactionProcessor


def show_client_scenario(
    bank: Bank,
    client: Client,
    transactions: list[Transaction],
) -> None:
    print(f"\n=== Accounts of {client.full_name} ===")

    for account in bank.search_accounts(client.client_id):
        print(account)

    print("\n=== Client transaction history ===")

    for transaction in transactions:
        sender_is_client = (
            transaction.sender is not None
            and transaction.sender.owner.client_id == client.client_id
        )
        receiver_is_client = (
            transaction.receiver is not None
            and transaction.receiver.owner.client_id == client.client_id
        )

        if sender_is_client or receiver_is_client:
            print(
                f"{transaction.transaction_id}: "
                f"{transaction.amount:.2f} {transaction.currency.value}, "
                f"status={transaction.status.value}"
            )


def show_reports(
    bank: Bank,
    transactions: list[Transaction],
    processor: TransactionProcessor,
) -> None:
    print("\n=== Suspicious operations ===")

    for entry in processor.audit_log.get_suspicious_entries():
        print(
            f"{entry.level.value}: {entry.message}, transaction={entry.transaction_id}"
        )

    print("\n=== Top 3 clients in RUB ===")

    ranking = bank.get_clients_ranking(Currency.RUB)

    for position, (client, balance) in enumerate(ranking[:3], start=1):
        print(f"{position}. {client.full_name}: {balance:.2f} RUB")

    print("\n=== Transaction statistics ===")
    statistics: dict[TransactionStatus, int] = {}

    for transaction in transactions:
        status = transaction.status
        statistics[status] = statistics.get(status, 0) + 1

    for status, count in statistics.items():
        print(f"{status.value}: {count}")

    print("\n=== Bank total balance ===")

    for currency, balance in bank.get_total_balance().items():
        print(f"{currency.value}: {balance:.2f}")


def run_demo() -> None:
    simulation = run_simulation(show_logs=True)

    show_client_scenario(
        simulation.bank,
        simulation.clients[0],
        simulation.transactions,
    )
    show_reports(
        simulation.bank,
        simulation.transactions,
        simulation.processor,
    )


if __name__ == "__main__":
    run_demo()
