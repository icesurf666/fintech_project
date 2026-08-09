from random import Random

from demos.common import create_fake_client
from src.bank import Bank
from src.bank_account import BankAccount
from src.client import Client
from src.enums import (
    Currency,
    TransactionStatus,
    TransactionType,
)
from src.risk_analyzer import RiskAnalyzer
from src.transaction import Transaction
from src.transaction_processor import TransactionProcessor
from src.transaction_queue import TransactionQueue


def get_accounts_by_currency(
    accounts: list[BankAccount],
    currency: Currency,
) -> list[BankAccount]:
    return [account for account in accounts if account.currency == currency]


def create_transactions(
    rub_accounts: list[BankAccount],
    usd_accounts: list[BankAccount],
    poor_account: BankAccount,
    frozen_account: BankAccount,
) -> tuple[list[Transaction], dict[str, str]]:
    random_generator = Random(42)

    scenario_types = (
        ["normal"] * 25
        + ["insufficient_funds"] * 5
        + ["frozen"] * 3
        + ["large"] * 3
        + ["night"] * 3
        + ["cancelled"]
    )
    random_generator.shuffle(scenario_types)

    transactions = []
    transaction_scenarios = {}

    for scenario in scenario_types:
        if scenario in ("normal", "cancelled"):
            currency = random_generator.choice([Currency.RUB, Currency.USD])
            currency_accounts = (
                rub_accounts if currency == Currency.RUB else usd_accounts
            )
            sender, receiver = random_generator.sample(
                currency_accounts,
                2,
            )
            amount = random_generator.randint(500, 5000)
        elif scenario == "insufficient_funds":
            sender = poor_account
            receiver = random_generator.choice(rub_accounts)
            amount = 10_000
        elif scenario == "frozen":
            sender = frozen_account
            receiver = random_generator.choice(rub_accounts)
            amount = 1000
        elif scenario == "large":
            sender, receiver = random_generator.sample(rub_accounts, 2)
            amount = 150_000
        else:
            sender, receiver = random_generator.sample(rub_accounts, 2)
            amount = 1000

        transaction = Transaction(
            transaction_type=TransactionType.TRANSFER,
            amount=amount,
            currency=sender.currency,
            sender=sender,
            receiver=receiver,
        )

        if scenario == "night":
            transaction.created_at = transaction.created_at.replace(
                hour=2,
                minute=0,
            )

        transactions.append(transaction)
        transaction_scenarios[transaction.transaction_id] = scenario

    return transactions, transaction_scenarios


def process_queue(
    queue: TransactionQueue,
    processor: TransactionProcessor,
    transaction_scenarios: dict[str, str],
) -> None:
    print("\n=== Transaction processing ===")

    while True:
        transaction = queue.get_next()

        if transaction is None:
            break

        processor.process(transaction)
        scenario = transaction_scenarios[transaction.transaction_id]

        if transaction.status == TransactionStatus.COMPLETED:
            print(
                f"EXECUTED: {transaction.transaction_id}, "
                f"type={scenario}, amount={transaction.amount:.2f}"
            )
        else:
            print(
                f"REJECTED: {transaction.transaction_id}, "
                f"type={scenario}, "
                f"reason={transaction.rejection_reason}"
            )


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
    bank = Bank()
    clients = [create_fake_client() for _ in range(5)]
    accounts = []

    for client in clients:
        bank.add_client(client)

        rub_account = bank.open_account(client.client_id, Currency.RUB)
        usd_account = bank.open_account(client.client_id, Currency.USD)

        accounts.append(rub_account)
        accounts.append(usd_account)

    for account in accounts:
        account.deposit(100_000)

    rub_accounts = get_accounts_by_currency(accounts, Currency.RUB)
    usd_accounts = get_accounts_by_currency(accounts, Currency.USD)

    poor_account = bank.open_account(clients[0].client_id, Currency.RUB)
    frozen_account = bank.open_account(clients[1].client_id, Currency.RUB)
    frozen_account.deposit(10_000)
    bank.freeze_account(frozen_account.account_number)
    accounts.extend([poor_account, frozen_account])

    print("=== Bank initialization ===")
    print(f"Clients: {len(clients)}")
    print(f"Accounts: {len(accounts)}")

    transactions, transaction_scenarios = create_transactions(
        rub_accounts,
        usd_accounts,
        poor_account,
        frozen_account,
    )

    queue = TransactionQueue()

    print("\n=== Adding transactions to queue ===")

    for transaction in transactions:
        queue.add(transaction)
        scenario = transaction_scenarios[transaction.transaction_id]
        print(
            f"QUEUED: {transaction.transaction_id}, "
            f"type={scenario}, amount={transaction.amount:.2f}"
        )

    cancelled_transaction = next(
        transaction
        for transaction in transactions
        if transaction_scenarios[transaction.transaction_id] == "cancelled"
    )
    queue.cancel(cancelled_transaction.transaction_id)
    print(f"CANCELLED: {cancelled_transaction.transaction_id}")

    processor = TransactionProcessor()
    processor.risk_analyzer = RiskAnalyzer(
        large_amount_limit=100_000,
        frequent_operations_limit=100,
    )

    process_queue(queue, processor, transaction_scenarios)
    show_client_scenario(bank, clients[0], transactions)
    show_reports(bank, transactions, processor)


if __name__ == "__main__":
    run_demo()
