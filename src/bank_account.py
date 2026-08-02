from src.account import AbstractAccount
from src.enums import AccountStatus
from src.exceptions import AccountClosedError, AccountFrozenError, InsufficientFundsError

class BankAccount(AbstractAccount):
    def _ensure_active(self) -> None:
        if self.status == AccountStatus.FROZEN:
            raise AccountFrozenError("Account is frozen")

        if self.status == AccountStatus.CLOSED:
            raise AccountClosedError("Account is closed")

    def _check_sufficient_funds(self, amount: float) -> None:
        if amount > self._balance:
            raise InsufficientFundsError("Insufficient funds")

    def deposit(self, amount: float) -> None:
        self._ensure_active()
        self._validate_amount(amount)
        self._balance += amount

    
    def withdraw(self, amount: float) -> None:
        self._ensure_active()
        self._validate_amount(amount)
        self._check_sufficient_funds(amount)
        self._balance -= amount

    def get_account_info(self) -> str:
        return (
            f"Account type: {self.__class__.__name__}, "
            f"Owner: {self.owner.full_name}, "
            f"Account: ****{self.account_number[-4:]}, "
            f"Status: {self.status.value}, "
            f"Balance: {self.balance:.2f} {self.currency.value}"
        )