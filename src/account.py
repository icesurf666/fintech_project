from abc import ABC, abstractmethod
from math import isfinite
from uuid import uuid4
from src.customer import Customer
from src.enums import AccountStatus, Currency
from src.exceptions import InvalidOperationError


class AbstractAccount(ABC):
    def __init__(
        self,
        owner: Customer,
        currency: Currency,
        account_number: str | None = None,
        status: AccountStatus = AccountStatus.ACTIVE,
    ):
        self._validate_owner(owner)
        self._validate_currency(currency)
        self._validate_status(status)

        self.account_number = self._prepare_account_number(account_number)
        self.currency = currency
        self._balance = 0.0
        self.status = status
        self.owner = owner

    @staticmethod
    def _validate_owner(owner: Customer) -> None:
        if not isinstance(owner, Customer):
            raise InvalidOperationError("Invalid customer")

    @staticmethod
    def _validate_currency(currency: Currency) -> None:
        if not isinstance(currency, Currency):
            raise InvalidOperationError("Invalid currency")

    @staticmethod
    def _validate_status(status: AccountStatus) -> None:
        if not isinstance(status, AccountStatus):
            raise InvalidOperationError("Invalid account status")

    @staticmethod
    def _validate_amount(amount: int | float) -> None:
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            raise InvalidOperationError("Amount must be numeric")

        if not isfinite(amount):
            raise InvalidOperationError("Amount must be finite")

        if amount <= 0:
            raise InvalidOperationError("Amount must be greater than zero")

    @staticmethod
    def _prepare_account_number(account_number: str | None) -> str:
        if account_number is None:
            return uuid4().hex[:12]

        if not isinstance(account_number, str):
            raise InvalidOperationError(
                "Account number must be a string"
            )

        account_number = account_number.strip()

        if len(account_number) < 4:
            raise InvalidOperationError(
                "Account number must contain at least 4 characters"
            )

        return account_number

    @property
    def balance(self) -> float:
        return self._balance

    @abstractmethod
    def deposit(self, amount: float) -> None:
        pass

    @abstractmethod
    def withdraw(self, amount: float) -> None:
        pass

    @abstractmethod
    def get_account_info(self) -> str:
        pass

    def __str__(self) -> str:
        return self.get_account_info()
