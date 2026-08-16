from src.bank_account import BankAccount
from src.client import Client
from src.enums import Currency
from src.exceptions import InvalidOperationError


class SavingsAccount(BankAccount):
    def __init__(
        self,
        owner: Client,
        currency: Currency,
        min_balance: float,
        monthly_rate: float,
    ) -> None:
        super().__init__(owner, currency)
        self._validate_non_negative_number(min_balance, "Minimum balance")
        self._validate_non_negative_number(monthly_rate, "Monthly rate")

        self.min_balance = min_balance
        self.monthly_rate = monthly_rate

    def withdraw(self, amount: float) -> None:
        self._ensure_active()
        self._validate_amount(amount)

        if self.balance - amount < self.min_balance:
            raise InvalidOperationError("Minimum balance cannot be exceeded")

        self._balance -= amount

    def apply_monthly_interest(self) -> None:
        self._ensure_active()
        interest = self._balance * self.monthly_rate
        self._balance += interest

    def get_account_info(self) -> str:
        return (
            f"{super().get_account_info()}, "
            f"Monthly rate: {self.monthly_rate * 100:.2f}%, "
            f"Minimum balance: {self.min_balance:.2f} "
            f"{self.currency.value}"
        )

    def __str__(self) -> str:
        return self.get_account_info()
