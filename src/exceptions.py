class AccountFrozenError(Exception):
    """Raised when an operation is attempted on a frozen account."""


class AccountClosedError(Exception):
    """Raised when an operation is attempted on a closed account."""


class InvalidOperationError(Exception):
    """Raised when an operation is not permitted."""


class InsufficientFundsError(Exception):
    """Raised when the account balance is too low."""
