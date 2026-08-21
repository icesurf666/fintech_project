from datetime import datetime

import pytest

from src.audit_log import AuditLog
from src.bank import Bank
from src.bank_account import BankAccount
from src.client import Client
from src.enums import Currency, Gender, RiskLevel, TransactionStatus, TransactionType
from src.exceptions import InvalidOperationError
from src.investment_account import InvestmentAccount
from src.premium_account import PremiumAccount
from src.report_builder import ReportBuilder
from src.risk_analyzer import RiskAnalyzer
from src.savings_account import SavingsAccount
from src.transaction import Transaction
from src.transaction_processor import TransactionProcessor
from src.transaction_queue import TransactionQueue


def test_bank_opens_and_registers_specialized_accounts(
    client: Client,
    tmp_path,
) -> None:
    bank = Bank()
    bank.add_client(client)

    savings = bank.open_account(
        client.client_id,
        Currency.RUB,
        account_type=SavingsAccount,
        min_balance=1000,
        monthly_rate=0.01,
    )
    premium = bank.open_account(
        client.client_id,
        Currency.RUB,
        account_type=PremiumAccount,
        withdrawal_limit=50_000,
        overdraft_limit=10_000,
        fee=100,
    )
    investment = bank.open_account(
        client.client_id,
        Currency.USD,
        account_type=InvestmentAccount,
        portfolio={"stocks": 5000, "bonds": 3000},
    )

    assert isinstance(savings, SavingsAccount)
    assert isinstance(premium, PremiumAccount)
    assert isinstance(investment, InvestmentAccount)

    for account in (savings, premium, investment):
        assert bank.accounts[account.account_number] is account
        assert account.account_number in client.account_numbers

    savings.deposit(5000)
    premium.deposit(7000)
    investment.deposit(2000)

    assert bank.get_client_total_balance(client.client_id) == {
        Currency.RUB: 12_000,
        Currency.USD: 2000,
    }
    assert bank.get_clients_ranking(Currency.RUB)[0] == (client, 12_000)

    report = ReportBuilder(
        bank,
        [],
        AuditLog(str(tmp_path / "audit.log")),
    ).build_bank_report()
    assert report["accounts_count"] == 3
    assert report["total_balance"] == {"RUB": 12_000, "USD": 2000}


def test_processor_handles_deposit_and_withdrawal(
    client: Client,
    tmp_path,
) -> None:
    account = BankAccount(client, Currency.RUB)
    processor = TransactionProcessor(
        risk_analyzer=RiskAnalyzer(frequent_operations_limit=100),
        audit_log=AuditLog(str(tmp_path / "audit.log")),
    )

    deposit = Transaction(
        TransactionType.DEPOSIT,
        1000,
        Currency.RUB,
        sender=None,
        receiver=account,
    )
    deposit.created_at = datetime.now().astimezone().replace(hour=12)
    processor.process(deposit)

    withdrawal = Transaction(
        TransactionType.WITHDRAWAL,
        250,
        Currency.RUB,
        sender=account,
        receiver=None,
    )
    withdrawal.created_at = datetime.now().astimezone().replace(hour=12)
    processor.process(withdrawal)

    assert deposit.status == TransactionStatus.COMPLETED
    assert withdrawal.status == TransactionStatus.COMPLETED
    assert account.balance == 750
    assert len(processor.audit_log.entries) == 2


def test_queue_respects_priority_set_before_add(client: Client) -> None:
    sender = BankAccount(client, Currency.RUB)
    receiver = BankAccount(client, Currency.RUB)
    low_priority = Transaction(
        TransactionType.TRANSFER,
        100,
        Currency.RUB,
        sender,
        receiver,
        priority=0,
    )
    high_priority = Transaction(
        TransactionType.TRANSFER,
        100,
        Currency.RUB,
        sender,
        receiver,
        priority=10,
    )
    queue = TransactionQueue()

    queue.add(low_priority)
    queue.add(high_priority)

    assert queue.get_next() is high_priority


def test_queue_respects_priority_changed_after_add(client: Client) -> None:
    sender = BankAccount(client, Currency.RUB)
    receiver = BankAccount(client, Currency.RUB)
    first = Transaction(
        TransactionType.TRANSFER,
        100,
        Currency.RUB,
        sender,
        receiver,
    )
    second = Transaction(
        TransactionType.TRANSFER,
        100,
        Currency.RUB,
        sender,
        receiver,
    )
    queue = TransactionQueue()
    queue.add(first)
    queue.add(second)

    second.priority = 10

    assert queue.get_next() is second


@pytest.mark.parametrize(
    "account_factory",
    [
        lambda client: SavingsAccount(client, Currency.RUB, -1, 0.01),
        lambda client: SavingsAccount(client, Currency.RUB, 0, -0.01),
        lambda client: PremiumAccount(client, Currency.RUB, -1, 1000, 10),
        lambda client: PremiumAccount(client, Currency.RUB, 1000, -1, 10),
        lambda client: PremiumAccount(client, Currency.RUB, 1000, 1000, -1),
    ],
)
def test_specialized_accounts_reject_negative_parameters(
    client: Client,
    account_factory,
) -> None:
    with pytest.raises(InvalidOperationError):
        account_factory(client)


def _make_client(client_id: str) -> Client:
    return Client(
        first_name="Other",
        last_name="Client",
        middle_name="User",
        birth_year=2000,
        passport="0987654321",
        gender=Gender.OTHER,
        phone="+70000000001",
        email=f"{client_id}@example.com",
        client_id=client_id,
    )


def test_bank_rejects_duplicate_account_number(client: Client) -> None:
    other = _make_client("other-1")
    bank = Bank()
    bank.add_client(client)
    bank.add_client(other)

    first = bank.open_account(
        client.client_id,
        Currency.RUB,
        account_number="ACC-0001",
    )

    with pytest.raises(InvalidOperationError):
        bank.open_account(
            other.client_id,
            Currency.RUB,
            account_number="ACC-0001",
        )

    assert bank.accounts["ACC-0001"] is first
    assert other.account_numbers == []


def _make_transfer(sender: BankAccount, receiver: BankAccount) -> Transaction:
    transfer = Transaction(
        TransactionType.TRANSFER,
        100,
        Currency.RUB,
        sender,
        receiver,
    )
    # Force a daytime hour so the risk analyzer does not block the transfer
    # as a night operation (which would make the test time-dependent).
    transfer.created_at = datetime.now().astimezone().replace(hour=12)
    return transfer


def test_failed_transfer_does_not_mark_receiver_known(
    client: Client,
    tmp_path,
) -> None:
    receiver_owner = _make_client("receiver-1")
    sender = BankAccount(client, Currency.RUB)
    receiver = BankAccount(receiver_owner, Currency.RUB)

    risk_analyzer = RiskAnalyzer()
    processor = TransactionProcessor(
        risk_analyzer=risk_analyzer,
        audit_log=AuditLog(str(tmp_path / "audit.log")),
    )

    transfer = _make_transfer(sender, receiver)

    # A brand-new receiver is flagged as MEDIUM risk.
    assert risk_analyzer.analyze_new_receiver(transfer) == RiskLevel.MEDIUM

    # Sender has no funds, so the transfer fails.
    processor.process(transfer)
    assert transfer.status == TransactionStatus.FAILED

    # The failed transfer must not mark the receiver as known.
    assert risk_analyzer.analyze_new_receiver(transfer) == RiskLevel.MEDIUM


def test_successful_transfer_marks_receiver_known(
    client: Client,
    tmp_path,
) -> None:
    receiver_owner = _make_client("receiver-2")
    sender = BankAccount(client, Currency.RUB)
    receiver = BankAccount(receiver_owner, Currency.RUB)
    sender.deposit(1000)

    risk_analyzer = RiskAnalyzer()
    processor = TransactionProcessor(
        risk_analyzer=risk_analyzer,
        audit_log=AuditLog(str(tmp_path / "audit.log")),
    )

    transfer = _make_transfer(sender, receiver)
    processor.process(transfer)

    # After a successful transfer the receiver is known, so risk drops to LOW.
    assert transfer.status == TransactionStatus.COMPLETED
    assert risk_analyzer.analyze_new_receiver(transfer) == RiskLevel.LOW
