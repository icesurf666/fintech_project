from faker import Faker

from src.bank_account import BankAccount
from src.customer import Customer
from src.enums import AccountStatus, Currency, Gender
from src.exceptions import (
    AccountClosedError,
    AccountFrozenError,
    InsufficientFundsError,
    InvalidOperationError,
)
from src.investment_account import InvestmentAccount
from src.premium_account import PremiumAccount
from src.savings_account import SavingsAccount

fake = Faker("ru_RU")
Faker.seed(42)


def create_fake_customer() -> Customer:
    gender = fake.random_element((Gender.MALE, Gender.FEMALE))
    birth_date = fake.date_of_birth(minimum_age=18, maximum_age=80)

    if gender == Gender.MALE:
        first_name = fake.first_name_male()
        last_name = fake.last_name_male()
        middle_name = fake.middle_name_male()
    else:
        first_name = fake.first_name_female()
        last_name = fake.last_name_female()
        middle_name = fake.middle_name_female()

    return Customer(
        first_name=first_name,
        last_name=last_name,
        middle_name=middle_name,
        birth_year=birth_date.year,
        passport=fake.numerify("##########"),
        gender=gender,
    )


def show_expected_error(title: str, operation) -> None:
    print(f"\n=== {title} ===")
    try:
        operation()
    except (
        AccountClosedError,
        AccountFrozenError,
        InsufficientFundsError,
        InvalidOperationError,
    ) as error:
        print(f"{type(error).__name__}: {error}")


def demonstrate_savings_accounts() -> None:
    savings_rub = SavingsAccount(
        owner=create_fake_customer(),
        currency=Currency.RUB,
        min_balance=1000,
        monthly_rate=0.01,
    )
    savings_usd = SavingsAccount(
        owner=create_fake_customer(),
        currency=Currency.USD,
        min_balance=500,
        monthly_rate=0.02,
    )

    savings_rub.deposit(10_000)
    savings_rub.apply_monthly_interest()
    savings_rub.withdraw(500)

    savings_usd.deposit(5000)
    savings_usd.apply_monthly_interest()

    print("\n=== Savings accounts ===")
    print(savings_rub)
    print(savings_usd)

    show_expected_error(
        "Savings account minimum balance",
        lambda: savings_rub.withdraw(9000),
    )


def demonstrate_premium_accounts() -> None:
    premium_rub = PremiumAccount(
        owner=create_fake_customer(),
        currency=Currency.RUB,
        withdrawal_limit=50_000,
        overdraft_limit=20_000,
        fee=100,
    )
    premium_eur = PremiumAccount(
        owner=create_fake_customer(),
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
        owner=create_fake_customer(),
        currency=Currency.USD,
        portfolio={"stocks": 5000, "bonds": 3000, "etf": 2000},
    )
    investment_cny = InvestmentAccount(
        owner=create_fake_customer(),
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


def demonstrate_bank_accounts() -> None:
    active_account = BankAccount(
        owner=create_fake_customer(),
        currency=Currency.EUR,
    )
    frozen_account = BankAccount(
        owner=create_fake_customer(),
        currency=Currency.USD,
        status=AccountStatus.FROZEN,
    )
    closed_account = BankAccount(
        owner=create_fake_customer(),
        currency=Currency.RUB,
        status=AccountStatus.CLOSED,
    )

    print("=== Initial accounts ===")
    print(active_account)
    print(frozen_account)
    print(closed_account)

    print("\n=== Valid deposit and withdrawal ===")
    active_account.deposit(1000)
    active_account.withdraw(250)
    print(active_account)

    show_expected_error(
        "Deposit to frozen account",
        lambda: frozen_account.deposit(100),
    )
    show_expected_error(
        "Withdrawal from frozen account",
        lambda: frozen_account.withdraw(100),
    )
    show_expected_error(
        "Deposit to closed account",
        lambda: closed_account.deposit(100),
    )
    show_expected_error(
        "Insufficient funds",
        lambda: active_account.withdraw(5000),
    )

    invalid_amounts = (-100, 0, "100", True, float("inf"), float("nan"))
    for amount in invalid_amounts:
        show_expected_error(
            f"Invalid deposit amount: {amount!r}",
            lambda amount=amount: active_account.deposit(amount),
        )

    invalid_account_numbers = ("", "   ", "123", 12345)
    for account_number in invalid_account_numbers:
        show_expected_error(
            f"Invalid account number: {account_number!r}",
            lambda account_number=account_number: BankAccount(
                owner=create_fake_customer(),
                currency=Currency.KZT,
                account_number=account_number,
            ),
        )

    custom_number_account = BankAccount(
        owner=create_fake_customer(),
        currency=Currency.CNY,
        account_number="  12345678  ",
    )
    print("\n=== Normalized custom account number ===")
    print(custom_number_account)


def main() -> None:
    demonstrate_bank_accounts()
    demonstrate_savings_accounts()
    demonstrate_premium_accounts()
    demonstrate_investment_accounts()


if __name__ == "__main__":
    main()
