# Changelog

## [Unreleased] - 2026-08-16

Fixes from mentor review:

- `Bank.open_account()` can open savings, premium, and investment accounts.
- `TransactionProcessor` handles deposits and withdrawals, not only transfers.
- `TransactionQueue` keeps priority order on `add()` and `get_next()`.
- Savings and premium accounts validate their parameters (no negative values).
- `Bank.search_account()` raises `InvalidOperationError` instead of `KeyError`.
