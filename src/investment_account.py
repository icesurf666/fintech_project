from math import isfinite
from typing import ClassVar

from src.bank_account import BankAccount
from src.customer import Customer
from src.enums import Currency
from src.exceptions import InvalidOperationError


class InvestmentAccount(BankAccount):
    ASSET_GROWTH_RATES: ClassVar[dict[str, float]] = {
        "stocks": 0.10,
        "bonds": 0.05,
        "etf": 0.07,
    }

    def __init__(
        self,
        owner: Customer,
        currency: Currency,
        portfolio: dict[str, float],
    ):
        super().__init__(owner, currency)
        self._validate_portfolio(portfolio)

        self.portfolio = portfolio.copy()

    @classmethod
    def _validate_portfolio(cls, portfolio: dict[str, float]) -> None:
        if not isinstance(portfolio, dict):
            raise InvalidOperationError("Portfolio must be a dictionary")

        for asset, value in portfolio.items():
            if asset not in cls.ASSET_GROWTH_RATES:
                raise InvalidOperationError(f"Unsupported asset: {asset}")

            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not isfinite(value)
                or value < 0
            ):
                raise InvalidOperationError(
                    f"Asset value must be a non-negative number: {asset}"
                )

    def project_yearly_growth(self) -> float:
        projected_value = 0.0

        for asset, value in self.portfolio.items():
            rate = self.ASSET_GROWTH_RATES[asset]
            projected_value += value * (1 + rate)

        return projected_value

    def withdraw(self, amount: float) -> None:
        super().withdraw(amount)

    def get_account_info(self) -> str:
        portfolio_info = ", ".join(
            f"{asset}: {value:.2f} {self.currency.value}"
            for asset, value in self.portfolio.items()
        )

        return (
            f"{super().get_account_info()}, "
            f"Portfolio: {{{portfolio_info}}}, "
            f"Projected yearly value: "
            f"{self.project_yearly_growth():.2f} {self.currency.value}"
        )

    def __str__(self) -> str:
        return self.get_account_info()
