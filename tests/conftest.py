import pytest

from src.bank import Bank
from src.client import Client
from src.enums import Gender


@pytest.fixture
def client() -> Client:
    return Client(
        first_name="Test",
        last_name="Client",
        middle_name="User",
        birth_year=2000,
        passport="1234567890",
        gender=Gender.OTHER,
        phone="+70000000000",
        email="test@example.com",
    )


@pytest.fixture(autouse=True)
def allow_bank_operations(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        Bank,
        "_ensure_operation_allowed",
        staticmethod(lambda: None),
    )
