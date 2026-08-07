from enum import Enum


class AccountStatus(Enum):
    ACTIVE = "active"
    FROZEN = "frozen"
    CLOSED = "closed"


class ClientStatus(Enum):
    ACTIVE = "active"
    BLOCKED = "blocked"


class Currency(Enum):
    EUR = "EUR"
    USD = "USD"
    RUB = "RUB"
    KZT = "KZT"
    CNY = "CNY"


class Gender(Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class TransactionType(Enum):
    TRANSFER = "transfer"
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"


class TransactionStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AuditLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
