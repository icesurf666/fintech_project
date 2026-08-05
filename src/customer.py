from dataclasses import dataclass

from src.enums import Gender


@dataclass
class Customer:
    first_name: str
    last_name: str
    middle_name: str
    birth_year: int
    passport: str
    gender: Gender

    @property
    def full_name(self) -> str:
        return f"{self.last_name} {self.first_name} {self.middle_name}"
