from collections.abc import Callable

from faker import Faker

from src.client import Client
from src.enums import Gender
from src.exceptions import (
    AccountClosedError,
    AccountFrozenError,
    InsufficientFundsError,
    InvalidOperationError,
)

fake = Faker("ru_RU")
Faker.seed(42)


def create_fake_client() -> Client:
    gender = fake.random_element((Gender.MALE, Gender.FEMALE))
    birth_date = fake.date_of_birth(minimum_age=18, maximum_age=80)

    if gender == Gender.MALE:
        first_name = fake.first_name_male()
        last_name = fake.last_name_male()
        middle_name = fake.middle_name_male()
    else:
        first_name = fake.first_name_female()
        last_name = fake.last_name_female()
        middle_name = fake.middle_name_female()

    return Client(
        first_name=first_name,
        last_name=last_name,
        middle_name=middle_name,
        birth_year=birth_date.year,
        passport=fake.numerify("##########"),
        gender=gender,
        phone=fake.phone_number(),
        email=fake.email(),
    )


def show_expected_error(
    title: str,
    operation: Callable[[], object],
) -> None:
    print(f"\n=== {title} ===")

    try:
        operation()
    except (
        AccountClosedError,
        AccountFrozenError,
        InsufficientFundsError,
        InvalidOperationError,
    ) as error:
        print(f"{type(error).__name__}: {error}")
