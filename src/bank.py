from datetime import datetime

from src.bank_account import BankAccount
from src.client import Client
from src.enums import AccountStatus, ClientStatus, Currency
from src.exceptions import InvalidOperationError


class Bank:
    def __init__(self) -> None:
        self.clients = {}
        self.accounts = {}
        self.failed_login_attempts = {}
        self.suspicious_actions = []

    @staticmethod
    def _ensure_operation_allowed() -> None:
        current_hour = datetime.now().astimezone().hour

        if 0 <= current_hour < 5:
            raise InvalidOperationError(
                "Operations are not allowed between 00:00 and 05:00"
            )

    def add_client(self, client: Client) -> None:
        self._ensure_operation_allowed()

        if not isinstance(client, Client):
            raise InvalidOperationError("Invalid client")

        if client.client_id in self.clients:
            raise InvalidOperationError("Client already exists")

        self.clients[client.client_id] = client

    def open_account(
        self,
        client_id: str,
        currency: Currency,
    ) -> BankAccount:
        self._ensure_operation_allowed()

        if client_id not in self.clients:
            raise InvalidOperationError("Client not found")

        client = self.clients[client_id]

        account = BankAccount(
            owner=client,
            currency=currency,
        )

        self.accounts[account.account_number] = account
        client.account_numbers.append(account.account_number)

        return account

    def close_account(
        self,
        account_number: str,
    ) -> None:
        self._ensure_operation_allowed()

        if account_number not in self.accounts:
            raise InvalidOperationError("Account not found")

        account = self.accounts[account_number]

        if account.status == AccountStatus.CLOSED:
            raise InvalidOperationError("Account is already closed")
        account.status = AccountStatus.CLOSED

    def freeze_account(
        self,
        account_number: str,
    ) -> None:
        self._ensure_operation_allowed()

        if account_number not in self.accounts:
            raise InvalidOperationError("Account not found")

        account = self.accounts[account_number]

        if account.status == AccountStatus.CLOSED:
            raise InvalidOperationError("Closed account cannot be frozen")
        account.status = AccountStatus.FROZEN

    def unfreeze_account(self, account_number: str) -> None:
        self._ensure_operation_allowed()

        if account_number not in self.accounts:
            raise InvalidOperationError("Account not found")

        account = self.accounts[account_number]

        if account.status == AccountStatus.CLOSED:
            raise InvalidOperationError("Closed account cannot be unfrozen")
        if account.status != AccountStatus.FROZEN:
            raise InvalidOperationError("Account is not frozen")
        account.status = AccountStatus.ACTIVE

    def authenticate_client(self, client_id: str, passport: str) -> bool:
        self._ensure_operation_allowed()

        if client_id not in self.clients:
            raise InvalidOperationError("Client not found")

        client = self.clients[client_id]

        if client.status == ClientStatus.BLOCKED:
            raise InvalidOperationError("Client is blocked")

        if client.passport == passport:
            self.failed_login_attempts[client_id] = 0
            return True
        attempts = self.failed_login_attempts.get(client_id, 0)

        attempts += 1
        self.failed_login_attempts[client_id] = attempts

        if attempts >= 3:
            client.status = ClientStatus.BLOCKED
            self.suspicious_actions.append(
                f"Client {client_id} was blocked after 3 failed login attempts"
            )

        return False

    def search_account(self, account_number):
        account = self.accounts[account_number]
        return account

    def search_accounts(
        self,
        client_id: str,
    ) -> list[BankAccount]:
        if client_id not in self.clients:
            raise InvalidOperationError("Client not found")

        client = self.clients[client_id]
        accounts = []

        for account_number in client.account_numbers:
            account = self.accounts[account_number]
            accounts.append(account)

        return accounts

    def get_client_total_balance(
        self,
        client_id: str,
    ) -> dict[Currency, float]:
        accounts = self.search_accounts(client_id)
        total_balance = {}

        for account in accounts:
            currency = account.currency
            current_balance = total_balance.get(currency, 0)
            total_balance[currency] = current_balance + account.balance

        return total_balance

    def get_total_balance(self) -> dict[Currency, float]:
        total_balance = {}

        for account in self.accounts.values():
            currency = account.currency
            total_balance[currency] = total_balance.get(currency, 0) + account.balance

        return total_balance

    def get_clients_ranking(
        self,
        currency: Currency,
    ) -> list[tuple[Client, float]]:
        ranking = []

        for client in self.clients.values():
            balances = self.get_client_total_balance(client.client_id)
            balance = balances.get(currency, 0)
            ranking.append((client, balance))

        return sorted(
            ranking,
            key=lambda item: item[1],
            reverse=True,
        )
