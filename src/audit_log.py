from datetime import datetime
from pathlib import Path

from src.audit_entry import AuditEntry
from src.enums import AuditLevel, RiskLevel


class AuditLog:
    def __init__(
        self,
        file_path: str | None = None,
    ) -> None:
        self.entries: list[AuditEntry] = []
        self.file_path = file_path

        if file_path is None:
            current_time = datetime.now().astimezone()
            file_name = current_time.strftime("audit_%Y-%m-%d_%H-%M-%S.log")
            self.file_path = file_name
        else:
            self.file_path = file_path

    def add(
        self,
        level: AuditLevel,
        message: str,
        transaction_id: str | None = None,
        client_id: str | None = None,
    ) -> None:
        entry = AuditEntry(
            level=level,
            message=message,
            transaction_id=transaction_id,
            client_id=client_id,
        )

        self.entries.append(entry)
        self.save_to_file(entry)

    def filter_by_level(
        self,
        level: AuditLevel,
    ) -> list[AuditEntry]:
        filtered_entries = []

        for entry in self.entries:
            if entry.level == level:
                filtered_entries.append(entry)

        return filtered_entries

    def save_to_file(
        self,
        entry: AuditEntry,
    ) -> None:
        line = (
            f"{entry.timestamp.isoformat()} | "
            f"{entry.level.value} | "
            f"{entry.message} | "
            f"transaction={entry.transaction_id} | "
            f"client={entry.client_id}\n"
        )

        with Path(self.file_path).open(
            "a",
            encoding="utf-8",
        ) as file:
            file.write(line)

    def get_suspicious_entries(
        self,
    ) -> list[AuditEntry]:
        suspicious_entries = []
        for entry in self.entries:
            if entry.level in (
                AuditLevel.WARNING,
                AuditLevel.ERROR,
            ):
                suspicious_entries.append(entry)

        return suspicious_entries

    def filter_by_client(
        self,
        client_id: str,
    ) -> list[AuditEntry]:
        client_entries = []

        for entry in self.entries:
            if entry.client_id == client_id:
                client_entries.append(entry)

        return client_entries

    def get_client_risk_profile(
        self,
        client_id: str,
    ) -> RiskLevel:
        client_entries = self.filter_by_client(client_id)

        for entry in client_entries:
            if entry.level == AuditLevel.ERROR:
                return RiskLevel.HIGH

        for entry in client_entries:
            if entry.level == AuditLevel.WARNING:
                return RiskLevel.MEDIUM

        return RiskLevel.LOW

    def get_error_statistics(
        self,
    ) -> dict[str, int]:
        statistics = {}

        for entry in self.entries:
            if entry.level != AuditLevel.ERROR:
                continue

            message = entry.message
            statistics[message] = statistics.get(message, 0) + 1

        return statistics
