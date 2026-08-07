from datetime import timedelta

from src.enums import RiskLevel
from src.transaction import Transaction


class RiskAnalyzer:
    def __init__(
        self,
        large_amount_limit: float = 100_000,
        frequent_operations_limit: int = 3,
        frequency_window_minutes: int = 1,
    ) -> None:
        self.large_amount_limit = large_amount_limit
        self.frequent_operations_limit = frequent_operations_limit
        self.frequency_window_minutes = frequency_window_minutes
        self.transaction_history: list[Transaction] = []
        self.known_receivers: dict[str, set[str]] = {}

    def analyze_amount(
        self,
        transaction: Transaction,
    ) -> RiskLevel:
        if transaction.amount >= self.large_amount_limit:
            return RiskLevel.HIGH

        if transaction.amount >= self.large_amount_limit / 2:
            return RiskLevel.MEDIUM

        return RiskLevel.LOW

    def analyze_frequency(
        self,
        transaction: Transaction,
    ) -> RiskLevel:
        if transaction.sender is None:
            return RiskLevel.LOW

        client_id = transaction.sender.owner.client_id
        operations_count = 1
        window_start = transaction.created_at - timedelta(
            minutes=self.frequency_window_minutes
        )

        for old_transaction in self.transaction_history:
            if old_transaction.sender is None:
                continue

            old_client_id = old_transaction.sender.owner.client_id

            if (
                old_client_id == client_id
                and old_transaction.created_at >= window_start
            ):
                operations_count += 1

        self.transaction_history.append(transaction)

        if operations_count >= self.frequent_operations_limit:
            return RiskLevel.HIGH

        return RiskLevel.LOW

    def analyze_new_receiver(
        self,
        transaction: Transaction,
    ) -> RiskLevel:
        if transaction.sender is None or transaction.receiver is None:
            return RiskLevel.LOW

        sender = transaction.sender
        receiver = transaction.receiver

        if sender.owner.client_id == receiver.owner.client_id:
            return RiskLevel.LOW

        client_id = sender.owner.client_id
        receiver_number = receiver.account_number

        known_accounts = self.known_receivers.setdefault(
            client_id,
            set(),
        )

        if receiver_number not in known_accounts:
            known_accounts.add(receiver_number)
            return RiskLevel.MEDIUM

        return RiskLevel.LOW

    def analyze_night_operation(
        self,
        transaction: Transaction,
    ) -> RiskLevel:
        hour = transaction.created_at.hour

        if 0 <= hour < 5:
            return RiskLevel.HIGH

        return RiskLevel.LOW

    def analyze(
        self,
        transaction: Transaction,
    ) -> RiskLevel:
        risk_levels = [
            self.analyze_amount(transaction),
            self.analyze_frequency(transaction),
            self.analyze_new_receiver(transaction),
            self.analyze_night_operation(transaction),
        ]

        if RiskLevel.HIGH in risk_levels:
            return RiskLevel.HIGH

        if RiskLevel.MEDIUM in risk_levels:
            return RiskLevel.MEDIUM

        return RiskLevel.LOW
