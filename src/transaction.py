from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from src.bank_account import BankAccount
from src.enums import (
    Currency,
    TransactionStatus,
    TransactionType,
)
from src.exceptions import InvalidOperationError


@dataclass
class Transaction:
    transaction_type: TransactionType
    amount: float
    currency: Currency
    sender: BankAccount | None
    receiver: BankAccount | None

    transaction_id: str = field(default_factory=lambda: uuid4().hex[:12])
    fee: float = 0.0
    status: TransactionStatus = TransactionStatus.PENDING
    rejection_reason: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now().astimezone())
    updated_at: datetime = field(default_factory=lambda: datetime.now().astimezone())
    priority: int = 0
    scheduled_at: datetime | None = None
    attempts: int = 0
    max_attempts: int = 3

    def __post_init__(self) -> None:
        if self.amount <= 0:
            raise InvalidOperationError("Amount must be greater than zero")

        if self.max_attempts <= 0:
            raise InvalidOperationError("Maximum attempts must be greater than zero")
