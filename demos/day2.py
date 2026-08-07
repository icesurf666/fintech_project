from demos.common import create_fake_client, show_expected_error
from src.enums import Currency
from src.investment_account import InvestmentAccount
from src.premium_account import PremiumAccount
from src.savings_account import SavingsAccount


def demonstrate_savings_accounts() -> None:
    savings_rub = SavingsAccount(
        owner=create_fake_client(),
        currency=Currency.RUB,
        min_balance=1000,
        monthly_rate=0.01,
    )
    savings_usd = SavingsAccount(
        owner=create_fake_client(),
        currency=Currency.USD,
        min_balance=500,
        monthly_rate=0.02,
    )

    savings_rub.deposit(10_000)
    savings_rub.apply_monthly_interest()
    savings_rub.withdraw(500)
    savings_usd.deposit(5000)
    savings_usd.apply_monthly_interest()

    print("=== Savings accounts ===")
    print(savings_rub)
    print(savings_usd)
    show_expected_error(
        "Savings account minimum balance",
        lambda: savings_rub.withdraw(9000),
    )


def demonstrate_premium_accounts() -> None:
    premium_rub = PremiumAccount(
        owner=create_fake_client(),
        currency=Currency.RUB,
        withdrawal_limit=50_000,
        overdraft_limit=20_000,
        fee=100,
    )
    premium_eur = PremiumAccount(
        owner=create_fake_client(),
        currency=Currency.EUR,
        withdrawal_limit=5000,
        overdraft_limit=2000,
        fee=20,
    )

    premium_rub.deposit(10_000)
    premium_rub.withdraw(12_000)
    premium_eur.deposit(3000)
    premium_eur.withdraw(1000)

    print("\n=== Premium accounts ===")
    print(premium_rub)
    print(premium_eur)
    show_expected_error(
        "Premium account withdrawal limit",
        lambda: premium_eur.withdraw(6000),
    )


def demonstrate_investment_accounts() -> None:
    investment_usd = InvestmentAccount(
        owner=create_fake_client(),
        currency=Currency.USD,
        portfolio={"stocks": 5000, "bonds": 3000, "etf": 2000},
    )
    investment_cny = InvestmentAccount(
        owner=create_fake_client(),
        currency=Currency.CNY,
        portfolio={"stocks": 8000, "bonds": 1000, "etf": 4000},
    )

    investment_usd.deposit(2000)
    investment_usd.withdraw(500)
    investment_cny.deposit(5000)

    print("\n=== Investment accounts ===")
    print(investment_usd)
    print(investment_cny)
    print(
        "USD portfolio yearly projection: "
        f"{investment_usd.project_yearly_growth():.2f} USD"
    )
    print(
        "CNY portfolio yearly projection: "
        f"{investment_cny.project_yearly_growth():.2f} CNY"
    )


def run_demo() -> None:
    demonstrate_savings_accounts()
    demonstrate_premium_accounts()
    demonstrate_investment_accounts()


if __name__ == "__main__":
    run_demo()
