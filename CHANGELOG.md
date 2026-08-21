# Changelog

## [Unreleased] - 2026-08-21

Second round of mentor review fixes:

- `Bank.open_account()` rejects a duplicate `account_number` instead of
  silently overwriting an existing account
- `RiskAnalyzer` mark a receiver as known only after a transfer succeeds. Failed transfers to a new account stay flagged as new-receiver.

## 2026-08-16

First round of mentor review fixes:

- `Bank.open_account()` can open savings, premium, and investment accounts.
- `TransactionProcessor` handles deposits and withdrawals, not only transfers.
- `TransactionQueue` keeps priority order on `add()` and `get_next()`.
- Savings and premium accounts validate their parameters (no negative values).
- `Bank.search_account()` raises `InvalidOperationError` instead of `KeyError`.
