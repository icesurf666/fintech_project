from datetime import datetime

from src.enums import TransactionStatus
from src.exceptions import InvalidOperationError
from src.transaction import Transaction


class TransactionQueue:
    def __init__(self) -> None:
        self.transactions: list[Transaction] = []

    def add(self, transaction: Transaction) -> None:
        if not isinstance(transaction, Transaction):
            raise InvalidOperationError("Only transactions can be added to the queue")

        self.transactions.append(transaction)
        self._sort_by_priority()

    def _sort_by_priority(self) -> None:
        self.transactions.sort(
            key=lambda transaction: transaction.priority,
            reverse=True,
        )

    def cancel(self, transaction_id: str) -> None:
        for transaction in self.transactions:
            if transaction.transaction_id == transaction_id:
                if transaction.status != TransactionStatus.PENDING:
                    raise InvalidOperationError(
                        "Only pending transaction can be cancelled"
                    )

                transaction.status = TransactionStatus.CANCELLED
                transaction.updated_at = datetime.now().astimezone()
                return

        raise InvalidOperationError("Transaction not found")

    def prioritize(
        self,
        transaction_id: str,
        priority: int,
    ) -> None:
        for transaction in self.transactions:
            if transaction.transaction_id == transaction_id:
                transaction.priority = priority
                self._sort_by_priority()
                return

        raise InvalidOperationError("Transaction not found")

    def get_next(self) -> Transaction | None:
        current_time = datetime.now().astimezone()
        self._sort_by_priority()

        for transaction in self.transactions:
            if transaction.status != TransactionStatus.PENDING:
                continue
            if (
                transaction.scheduled_at is not None
                and transaction.scheduled_at > current_time
            ):
                continue

            self.transactions.remove(transaction)

            return transaction
        return None
