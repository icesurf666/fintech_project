from demos.common import create_fake_client, show_expected_error
from src.bank_account import BankAccount
from src.enums import AccountStatus, Currency


def run_demo() -> None:
    active_account = BankAccount(
        owner=create_fake_client(),
        currency=Currency.EUR,
    )
    frozen_account = BankAccount(
        owner=create_fake_client(),
        currency=Currency.USD,
        status=AccountStatus.FROZEN,
    )
    closed_account = BankAccount(
        owner=create_fake_client(),
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
                owner=create_fake_client(),
                currency=Currency.KZT,
                account_number=account_number,
            ),
        )

    custom_number_account = BankAccount(
        owner=create_fake_client(),
        currency=Currency.CNY,
        account_number="  12345678  ",
    )
    print("\n=== Normalized custom account number ===")
    print(custom_number_account)


if __name__ == "__main__":
    run_demo()
