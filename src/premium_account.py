from src.bank_account import BankAccount
from src.client import Client
from src.enums import Currency
from src.exceptions import InsufficientFundsError, InvalidOperationError


class PremiumAccount(BankAccount):
    def __init__(
        self,
        owner: Client,
        currency: Currency,
        withdrawal_limit: float,
        overdraft_limit: float,
        fee: float,
    ):
        super().__init__(owner, currency)

        self.withdrawal_limit = withdrawal_limit
        self.overdraft_limit = overdraft_limit
        self.fee = fee

    def withdraw(self, amount: float) -> None:
        self._ensure_active()
        self._validate_amount(amount)

        if amount > self.withdrawal_limit:
            raise InvalidOperationError("Withdrawal amount exceeds the limit")

        total_amount = amount + self.fee

        if self.balance - total_amount < -self.overdraft_limit:
            raise InsufficientFundsError("Overdraft limit exceeded")

        self._balance -= total_amount

    def get_account_info(self) -> str:
        base_info = super().get_account_info()
        return (
            f"{base_info}, "
            f"Withdrawal limit: {self.withdrawal_limit:.2f} {self.currency.value}, "
            f"Overdraft limit: {self.overdraft_limit:.2f} {self.currency.value}, "
            f"Fee: {self.fee:.2f} {self.currency.value}"
        )

    def __str__(self) -> str:
        return self.get_account_info()
