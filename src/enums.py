from enum import Enum


class AccountStatus(Enum):
    ACTIVE = "active"
    FROZEN = "frozen"
    CLOSED = "closed"


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
