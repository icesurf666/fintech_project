# Fintech Project

A banking system built with Python using object-oriented programming
principles.

The project includes several account types, client management,
transaction processing, auditing, risk analysis, reporting, and data
visualization.

## Features

- Basic, savings, premium, and investment accounts
- Deposits, withdrawals, fees, overdrafts, and currency conversion
- Client and bank account management
- Transaction queue with priorities, cancellation, and scheduled operations
- Transaction retries and error logging
- Audit logging and suspicious transaction analysis
- Client, bank, and risk reports
- JSON and CSV report export
- Chart generation with Matplotlib

## Project Structure

```text
fintech_project/
├── main.py              # Demo launcher
├── requirements.txt     # Project dependencies
├── src/                 # Banking system source code
│   ├── account.py
│   ├── bank.py
│   ├── bank_account.py
│   ├── client.py
│   ├── report_builder.py
│   ├── transaction.py
│   └── ...
├── tests/               # Unit and integration tests
│   └── test_required_fixes.py
└── demos/               # Feature demonstrations
    ├── day1.py
    ├── day2.py
    ├── day3.py
    ├── day4.py
    ├── day5.py
    ├── day6.py
    └── day7.py
```

## Installation

Python 3.13 or newer is required.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

## Usage

Run the demonstration for a specific day:

```bash
python3 main.py 1
python3 main.py 6
python3 main.py 7
```

Run all demonstrations sequentially by omitting the day number:

```bash
python3 main.py
```

A demonstration can also be run directly as a module:

```bash
python3 -m demos.day7
```

## Reports

The Day 7 demonstration generates files in `reports/day7`:

- Client, bank, and risk reports in JSON format
- Client account and transaction data in CSV format
- Pie, bar, and line charts in PNG format

The `reports` directory contains generated files and is excluded from Git.

## Code Quality

Run the test suite:

```bash
python3 -m pytest
```

Run Ruff checks and verify formatting:

```bash
python3 -m ruff check .
python3 -m ruff format --check .
```
