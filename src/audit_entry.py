from dataclasses import dataclass, field
from datetime import datetime

from src.enums import AuditLevel


@dataclass
class AuditEntry:
    level: AuditLevel
    message: str
    timestamp: datetime = field(default_factory=lambda: datetime.now().astimezone())
    transaction_id: str | None = None
    client_id: str | None = None
