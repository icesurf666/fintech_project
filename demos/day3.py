from demos.common import create_fake_client
from src.bank import Bank
from src.enums import Currency
from src.exceptions import InvalidOperationError


def run_demo() -> None:
    bank = Bank()
    first_client = create_fake_client()
    second_client = create_fake_client()
    third_client = create_fake_client()

    try:
        bank.add_client(first_client)
        bank.add_client(second_client)
        bank.add_client(third_client)

        first_rub_account = bank.open_account(first_client.client_id, Currency.RUB)
        first_usd_account = bank.open_account(first_client.client_id, Currency.USD)
        second_rub_account = bank.open_account(second_client.client_id, Currency.RUB)
        third_rub_account = bank.open_account(third_client.client_id, Currency.RUB)

        first_rub_account.deposit(30_000)
        first_usd_account.deposit(500)
        second_rub_account.deposit(75_000)
        third_rub_account.deposit(10_000)

        print("=== Client accounts ===")
        for account in bank.search_accounts(first_client.client_id):
            print(account)

        print("\n=== First client total balance ===")
        for currency, balance in bank.get_client_total_balance(
            first_client.client_id
        ).items():
            print(f"{currency.value}: {balance:.2f}")

        print("\n=== Bank total balance ===")
        for currency, balance in bank.get_total_balance().items():
            print(f"{currency.value}: {balance:.2f}")

        print("\n=== Clients ranking in RUB ===")
        for position, (client, balance) in enumerate(
            bank.get_clients_ranking(Currency.RUB),
            start=1,
        ):
            print(f"{position}. {client.full_name}: {balance:.2f} RUB")

        print("\n=== Freeze and unfreeze account ===")
        bank.freeze_account(first_rub_account.account_number)
        print(first_rub_account)
        bank.unfreeze_account(first_rub_account.account_number)
        print(first_rub_account)

        print("\n=== Failed authentication attempts ===")
        for attempt in range(1, 4):
            authenticated = bank.authenticate_client(
                third_client.client_id,
                "wrong-passport",
            )
            print(f"Attempt {attempt}: {authenticated}")

        print(f"Client status: {third_client.status.value}")
        print(f"Suspicious actions: {bank.suspicious_actions}")
    except InvalidOperationError as error:
        print(f"InvalidOperationError: {error}")


if __name__ == "__main__":
    run_demo()
