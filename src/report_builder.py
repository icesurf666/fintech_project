import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt

from src.audit_log import AuditLog
from src.bank import Bank
from src.enums import Currency
from src.exceptions import InvalidOperationError
from src.transaction import Transaction


class ReportBuilder:
    def __init__(
        self,
        bank: Bank,
        transactions: list[Transaction],
        audit_log: AuditLog,
    ) -> None:
        self.bank = bank
        self.transactions = transactions
        self.audit_log = audit_log

    def build_client_report(self, client_id: str) -> dict:
        if client_id not in self.bank.clients:
            raise InvalidOperationError("Client not found")

        client = self.bank.clients[client_id]
        accounts = self.bank.search_accounts(client_id)
        client_balance = self.bank.get_client_total_balance(client_id)

        account_data = []

        for account in accounts:
            account_data.append(
                {
                    "account_number": account.account_number,
                    "currency": account.currency.value,
                    "balance": account.balance,
                    "status": account.status.value,
                }
            )

        transaction_history = []

        for transaction in self.transactions:
            sender_is_client = (
                transaction.sender is not None
                and transaction.sender.owner.client_id == client_id
            )
            receiver_is_client = (
                transaction.receiver is not None
                and transaction.receiver.owner.client_id == client_id
            )

            if sender_is_client or receiver_is_client:
                transaction_history.append(
                    {
                        "transaction_id": transaction.transaction_id,
                        "type": transaction.transaction_type.value,
                        "amount": transaction.amount,
                        "currency": transaction.currency.value,
                        "status": transaction.status.value,
                    }
                )

        return {
            "client_id": client.client_id,
            "full_name": client.full_name,
            "status": client.status.value,
            "accounts": account_data,
            "balance": {
                currency.value: amount for currency, amount in client_balance.items()
            },
            "transactions": transaction_history,
        }

    def build_bank_report(self) -> dict:
        client_count = len(self.bank.clients)
        transaction_count = len(self.transactions)
        accounts_count = len(self.bank.accounts)
        total_balance = {}

        transaction_statistics = {
            "pending": 0,
            "completed": 0,
            "failed": 0,
            "cancelled": 0,
        }

        for transaction in self.transactions:
            status = transaction.status.value
            transaction_statistics[status] += 1

        for currency, balance in self.bank.get_total_balance().items():
            total_balance[currency.value] = balance

        return {
            "clients_count": client_count,
            "accounts_count": accounts_count,
            "transactions_count": transaction_count,
            "total_balance": total_balance,
            "transaction_statistics": transaction_statistics,
        }

    def build_risk_report(self) -> dict:
        suspicious_operations = []
        client_risk_profiles = {}
        error_statistics = self.audit_log.get_error_statistics()
        suspicious_entries = self.audit_log.get_suspicious_entries()

        for entry in suspicious_entries:
            suspicious_operations.append(
                {
                    "level": entry.level.value,
                    "message": entry.message,
                    "timestamp": entry.timestamp.isoformat(),
                    "transaction_id": entry.transaction_id,
                    "client_id": entry.client_id,
                }
            )

        for client in self.bank.clients.values():
            risk_level = self.audit_log.get_client_risk_profile(client.client_id)

            client_risk_profiles[client.client_id] = {
                "full_name": client.full_name,
                "risk_level": risk_level.value,
            }

        return {
            "suspicious_operations": suspicious_operations,
            "client_risk_profiles": client_risk_profiles,
            "error_statistics": error_statistics,
        }

    def export_to_json(
        self,
        report: dict,
        file_path: str,
    ) -> None:
        with Path(file_path).open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                report,
                file,
                ensure_ascii=False,
                indent=4,
            )

    def export_to_csv(
        self,
        rows: list[dict],
        file_path: str,
    ) -> None:
        with Path(file_path).open(
            "w",
            encoding="utf-8",
            newline="",
        ) as file:
            if not rows:
                return

            column_names = rows[0].keys()

            writer = csv.DictWriter(
                file,
                fieldnames=column_names,
            )

            writer.writeheader()
            writer.writerows(rows)

    def build_text_report(
        self,
        report: dict,
    ) -> str:
        lines = []

        for key, value in report.items():
            line = f"{key}: {value}"
            lines.append(line)

        return "\n".join(lines)

    def save_transaction_status_chart(
        self,
        file_path: str,
    ) -> None:
        bank_report = self.build_bank_report()
        transaction_statistics = bank_report["transaction_statistics"]

        labels = list(transaction_statistics.keys())
        values = list(transaction_statistics.values())

        if not any(values):
            raise InvalidOperationError("No transaction data for chart")

        plt.figure(figsize=(8, 6))
        plt.pie(
            values,
            labels=labels,
            autopct="%1.1f%%",
        )
        plt.title("Transaction statuses")
        plt.savefig(file_path)
        plt.close()

    def save_clients_balance_chart(
        self,
        currency: Currency,
        file_path: str,
    ) -> None:
        ranking = self.bank.get_clients_ranking(currency)

        labels = []
        values = []

        for client, balance in ranking:
            labels.append(client.full_name)
            values.append(balance)

        if not ranking:
            raise InvalidOperationError("No clients for chart")

        plt.figure(figsize=(10, 6))

        plt.bar(
            labels,
            values,
        )

        plt.title(f"Client balances in {currency.value}")
        plt.xlabel("Clients")
        plt.ylabel(f"Balance ({currency.value})")

        plt.xticks(
            rotation=45,
            ha="right",
        )

        plt.tight_layout()
        plt.savefig(file_path)
        plt.close()

    def save_balance_history_chart(
        self,
        balance_history: list[float],
        file_path: str,
    ) -> None:
        if not balance_history:
            raise InvalidOperationError("Balance history is empty")

        operation_numbers = range(len(balance_history))

        plt.figure(figsize=(10, 6))

        plt.plot(
            operation_numbers,
            balance_history,
            marker="o",
        )

        plt.title("Balance history")
        plt.xlabel("Operation number")
        plt.ylabel("Balance")
        plt.grid(True)

        plt.tight_layout()
        plt.savefig(file_path)
        plt.close()

    def save_charts(
        self,
        output_dir: str,
        currency: Currency,
        balance_history: list[float],
    ) -> None:
        charts_directory = Path(output_dir)

        charts_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.save_transaction_status_chart(
            str(charts_directory / "transaction_statuses.png")
        )

        self.save_clients_balance_chart(
            currency,
            str(charts_directory / "client_balances.png"),
        )

        self.save_balance_history_chart(
            balance_history,
            str(charts_directory / "balance_history.png"),
        )
