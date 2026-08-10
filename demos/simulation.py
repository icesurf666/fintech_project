from dataclasses import dataclass
from random import Random

from demos.common import create_fake_client
from src.bank import Bank
from src.bank_account import BankAccount
from src.client import Client
from src.enums import Currency, TransactionStatus, TransactionType
from src.risk_analyzer import RiskAnalyzer
from src.transaction import Transaction
from src.transaction_processor import TransactionProcessor
from src.transaction_queue import TransactionQueue


@dataclass
class SimulationResult:
    bank: Bank
    clients: list[Client]
    accounts: list[BankAccount]
    transactions: list[Transaction]
    processor: TransactionProcessor
    balance_history: list[float]


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
            sender, receiver = random_generator.sample(currency_accounts, 2)
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


def run_simulation(show_logs: bool = False) -> SimulationResult:
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

    transactions, transaction_scenarios = create_transactions(
        rub_accounts,
        usd_accounts,
        poor_account,
        frozen_account,
    )

    queue = TransactionQueue()

    if show_logs:
        print("=== Bank initialization ===")
        print(f"Clients: {len(clients)}")
        print(f"Accounts: {len(accounts)}")
        print("\n=== Adding transactions to queue ===")

    for transaction in transactions:
        queue.add(transaction)

        if show_logs:
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

    if show_logs:
        print(f"CANCELLED: {cancelled_transaction.transaction_id}")
        print("\n=== Transaction processing ===")

    processor = TransactionProcessor()
    processor.risk_analyzer = RiskAnalyzer(
        large_amount_limit=100_000,
        frequent_operations_limit=100,
    )

    tracked_account = rub_accounts[0]
    balance_history = [tracked_account.balance]

    while True:
        transaction = queue.get_next()

        if transaction is None:
            break

        processor.process(transaction)
        balance_history.append(tracked_account.balance)

        if show_logs:
            scenario = transaction_scenarios[transaction.transaction_id]

            if transaction.status == TransactionStatus.COMPLETED:
                print(
                    f"EXECUTED: {transaction.transaction_id}, "
                    f"type={scenario}, amount={transaction.amount:.2f}"
                )
            else:
                print(
                    f"REJECTED: {transaction.transaction_id}, "
                    f"type={scenario}, reason={transaction.rejection_reason}"
                )

    return SimulationResult(
        bank=bank,
        clients=clients,
        accounts=accounts,
        transactions=transactions,
        processor=processor,
        balance_history=balance_history,
    )
