from datetime import datetime

from src.audit_log import AuditLog
from src.enums import (
    AccountStatus,
    AuditLevel,
    Currency,
    RiskLevel,
    TransactionStatus,
    TransactionType,
)
from src.exceptions import (
    AccountClosedError,
    AccountFrozenError,
    InsufficientFundsError,
    InvalidOperationError,
)
from src.risk_analyzer import RiskAnalyzer
from src.transaction import Transaction

EXCHANGE_RATES = {
    Currency.RUB: 1.0,
    Currency.USD: 90.0,
    Currency.EUR: 100.0,
    Currency.KZT: 0.2,
    Currency.CNY: 12.0,
}


class TransactionProcessor:
    def __init__(
        self,
        external_fee_rate: float = 0.01,
        risk_analyzer: RiskAnalyzer | None = None,
        audit_log: AuditLog | None = None,
    ) -> None:
        self.errors: list[str] = []
        self.external_fee_rate = external_fee_rate
        self.risk_analyzer = (
            risk_analyzer if risk_analyzer is not None else RiskAnalyzer()
        )
        self.audit_log = audit_log if audit_log is not None else AuditLog()

    def process(self, transaction: Transaction) -> None:
        if transaction.status != TransactionStatus.PENDING:
            raise InvalidOperationError("Only pending transaction can be processed")

        risk_level = self.risk_analyzer.analyze(transaction)

        client_id = None

        if transaction.sender is not None:
            client_id = transaction.sender.owner.client_id

        if risk_level == RiskLevel.HIGH:
            transaction.status = TransactionStatus.FAILED
            transaction.rejection_reason = "Transaction blocked due to high risk"
            transaction.updated_at = datetime.now().astimezone()

            self.audit_log.add(
                level=AuditLevel.ERROR,
                message="High-risk transaction blocked",
                transaction_id=transaction.transaction_id,
                client_id=client_id,
            )

            return

        if risk_level == RiskLevel.MEDIUM:
            self.audit_log.add(
                level=AuditLevel.WARNING,
                message="Medium-risk transaction detected",
                transaction_id=transaction.transaction_id,
                client_id=client_id,
            )

        while transaction.attempts < transaction.max_attempts:
            transaction.attempts += 1

            try:
                self._execute_transfer(transaction)
            except (
                AccountClosedError,
                AccountFrozenError,
                InsufficientFundsError,
                InvalidOperationError,
            ) as error:
                transaction.rejection_reason = str(error)
                transaction.updated_at = datetime.now().astimezone()
                self.errors.append(
                    f"Transaction {transaction.transaction_id}, "
                    f"attempt {transaction.attempts}: {error}"
                )

                self.audit_log.add(
                    level=AuditLevel.ERROR,
                    message=str(error),
                    transaction_id=transaction.transaction_id,
                    client_id=client_id,
                )
            else:
                transaction.status = TransactionStatus.COMPLETED
                transaction.rejection_reason = None
                transaction.updated_at = datetime.now().astimezone()

                self.audit_log.add(
                    level=AuditLevel.INFO,
                    message="Transaction completed",
                    transaction_id=transaction.transaction_id,
                    client_id=client_id,
                )
                return

        transaction.status = TransactionStatus.FAILED

    def _execute_transfer(self, transaction: Transaction) -> None:
        if transaction.transaction_type != TransactionType.TRANSFER:
            raise InvalidOperationError("Only transfers are supported")

        if transaction.sender is None:
            raise InvalidOperationError("Sender is required")

        if transaction.receiver is None:
            raise InvalidOperationError("Receiver is required")

        sender = transaction.sender
        receiver = transaction.receiver

        if sender.status != AccountStatus.ACTIVE:
            raise InvalidOperationError("Sender account is not active")

        if receiver.status != AccountStatus.ACTIVE:
            raise InvalidOperationError("Receiver account is not active")

        if sender.owner.client_id != receiver.owner.client_id:
            transaction.fee = transaction.amount * self.external_fee_rate
        else:
            transaction.fee = 0

        if transaction.currency != sender.currency:
            raise InvalidOperationError(
                "Transaction currency does not match sender currency"
            )

        sender_rate = EXCHANGE_RATES[sender.currency]
        receiver_rate = EXCHANGE_RATES[receiver.currency]

        amount_in_rub = transaction.amount * sender_rate
        converted_amount = amount_in_rub / receiver_rate

        total_amount = transaction.amount + transaction.fee

        sender.withdraw(total_amount)
        receiver.deposit(converted_amount)
