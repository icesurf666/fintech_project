from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from src.enums import ClientStatus, Gender
from src.exceptions import InvalidOperationError


@dataclass
class Client:
    first_name: str
    last_name: str
    middle_name: str
    birth_year: int
    passport: str
    gender: Gender
    phone: str
    email: str
    client_id: str = field(default_factory=lambda: uuid4().hex[:8])
    status: ClientStatus = ClientStatus.ACTIVE
    account_numbers: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.check_age():
            raise InvalidOperationError("Client must be at least 18 years old")

    @property
    def full_name(self) -> str:
        return f"{self.last_name} {self.first_name} {self.middle_name}"

    def check_age(self) -> bool:
        age = datetime.now().astimezone().year - self.birth_year
        return age >= 18
