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


def main() -> None:
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


if __name__ == "__main__":
    main()
