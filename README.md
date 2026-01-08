# Python Accounting

[![Build Status](https://github.com/ekmungai/python-accounting/workflows/Python%20package/badge.svg)](https://github.com/ekmungai/python-accounting/actions)
[![codecov](https://codecov.io/gh/ekmungai/python-accounting/branch/main/graph/badge.svg)](https://codecov.io/gh/ekmungai/python-accounting)
[![Python Version](https://img.shields.io/pypi/pyversions/python-accounting.svg)](https://pypi.org/project/python-accounting/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/python-accounting.svg)](https://badge.fury.io/py/python-accounting)

**The world's most comprehensive Double Entry Bookkeeping Python library.**

Python Accounting is a powerful, IFRS/GAAP-compliant accounting library that provides complete financial statement generation, multi-currency support, and enterprise-grade features for building accounting systems.

## ✨ Features

- 📊 **Complete Financial Statements**: Income Statement, Balance Sheet, Cashflow Statement, Statement of Changes in Equity
- 🌍 **Multi-Currency Support**: Exchange rates with historical tracking and automatic conversion
- 📈 **Budget Management**: Budget vs Actual comparison with variance analysis
- 🔒 **Ledger Integrity**: Built-in tamper protection for transaction security
- 📁 **Export Options**: PDF, Excel, CSV, and JSON export for all reports
- 🖥️ **CLI Tool**: Command-line interface for quick operations
- 🔌 **Event System**: Hooks for transaction posting, balance changes, and more
- 🌐 **Internationalization**: Multi-language support (English, German, French, Dutch)
- ⚡ **Batch Operations**: Efficient bulk processing for large datasets

## 🚀 Quick Start

### Installation

```bash
# Basic installation
pip install python-accounting

# With database drivers
pip install python-accounting[postgres]  # PostgreSQL
pip install python-accounting[mysql]     # MySQL/MariaDB

# With export capabilities
pip install python-accounting[pdf]       # PDF export
pip install python-accounting[excel]     # Excel export

# Everything
pip install python-accounting[all]
```

### Basic Usage

```python
from python_accounting.config import config
from python_accounting.models import Base, Entity, Currency, Account
from python_accounting.database.session import get_session
from sqlalchemy import create_engine

# Initialize database
engine = create_engine("sqlite:///accounting.db")
Base.metadata.create_all(engine)

with get_session(engine) as session:
    # Create entity and currency
    entity = Entity(name="My Company")
    session.add(entity)
    session.commit()
    
    currency = Currency(name="US Dollars", code="USD", entity_id=entity.id)
    session.add(currency)
    session.commit()
    
    # Create accounts
    bank = Account(
        name="Bank Account",
        account_type=Account.AccountType.BANK,
        currency_id=currency.id,
        entity_id=entity.id,
    )
    revenue = Account(
        name="Sales Revenue",
        account_type=Account.AccountType.OPERATING_REVENUE,
        currency_id=currency.id,
        entity_id=entity.id,
    )
    session.add_all([bank, revenue])
    session.commit()
```

### Creating Transactions

```python
from datetime import datetime
from python_accounting.transactions import CashSale
from python_accounting.models import LineItem

# Create a cash sale
cash_sale = CashSale(
    narration="Product sale",
    transaction_date=datetime.now(),
    account_id=bank.id,
    entity_id=entity.id,
)
session.add(cash_sale)
session.flush()

# Add line item
line_item = LineItem(
    narration="Product A",
    account_id=revenue.id,
    amount=100,
    entity_id=entity.id,
)
session.add(line_item)
session.flush()

cash_sale.line_items.add(line_item)
cash_sale.post(session)  # Post to ledger
```

### Generating Reports

```python
from python_accounting.reports import IncomeStatement, BalanceSheet, CashflowStatement

# Generate reports
income_statement = IncomeStatement(session)
print(income_statement)

balance_sheet = BalanceSheet(session)
print(balance_sheet)

cashflow = CashflowStatement(session)
print(cashflow)

# Export to different formats
from python_accounting.exporters import export_report

export_report(income_statement, "income_statement.pdf", "pdf")
export_report(balance_sheet, "balance_sheet.xlsx", "excel")
export_report(cashflow, "cashflow.json", "json")
```

### Using the CLI

```bash
# Initialize database
pyaccount init --database-url sqlite:///accounting.db

# Create entity
pyaccount entity create "My Company" --currency USD

# List accounts
pyaccount account list --entity-id 1

# Generate reports
pyaccount report income-statement --entity-id 1
pyaccount report balance-sheet --entity-id 1 --export pdf --output balance.pdf
```

## 📚 Documentation

Full documentation is available on [ReadTheDocs](https://python-accounting.readthedocs.io/).

### Available Reports

| Report | Description | IFRS/GAAP |
|--------|-------------|-----------|
| Income Statement | Profit & Loss | ✅ |
| Balance Sheet | Statement of Financial Position | ✅ |
| Cashflow Statement | Statement of Cash Flows | ✅ |
| Equity Statement | Statement of Changes in Equity | ✅ |
| Trial Balance | Debit/Credit verification | ✅ |
| Aging Schedule | Receivables/Payables aging | ✅ |
| Budget Report | Budget vs Actual analysis | ✅ |

### Supported Databases

| Database | Status |
|----------|--------|
| SQLite | ✅ Fully tested |
| PostgreSQL | ✅ Fully tested |
| MySQL/MariaDB | ✅ Fully tested |

## 🔧 Advanced Features

### Multi-Currency Support

```python
from python_accounting.models import ExchangeRate

# Set exchange rate
rate = ExchangeRate(
    from_currency_id=usd.id,
    to_currency_id=eur.id,
    rate=Decimal("0.85"),
    effective_date=datetime.now(),
    entity_id=entity.id,
)
session.add(rate)
session.commit()

# Convert amounts
converted = ExchangeRate.convert(session, Decimal("100"), usd.id, eur.id)
```

### Budget Management

```python
from python_accounting.models import Budget
from python_accounting.reports import BudgetReport

# Create budget
budget = Budget(
    account_id=marketing_account.id,
    reporting_period_id=period.id,
    amount=Decimal("10000"),
    name="Marketing Budget Q1",
    entity_id=entity.id,
)
session.add(budget)
session.commit()

# Generate variance report
report = BudgetReport(session)
print(report)
```

### Event Hooks

```python
from python_accounting.events import EventManager, EventType

def on_transaction_posted(event):
    print(f"Transaction {event.data['transaction_id']} posted!")
    # Send notification, update cache, etc.

EventManager.subscribe(EventType.TRANSACTION_POSTED, on_transaction_posted)
```

### Batch Operations

```python
from python_accounting.utils.batch import BatchProcessor

processor = BatchProcessor(session, batch_size=100)

# Bulk create accounts
result = processor.bulk_create_accounts([
    {"name": "Account 1", "account_type": "BANK", "currency_id": currency.id},
    {"name": "Account 2", "account_type": "RECEIVABLE", "currency_id": currency.id},
    # ... more accounts
])

print(f"Success rate: {result.success_rate}%")
```

## 🛠️ Development

```bash
# Clone repository
git clone https://github.com/ekmungai/python-accounting.git
cd python-accounting

# Install with Poetry
poetry install --with dev,test

# Run tests
poetry run pytest

# Run linting
poetry run ruff check python_accounting/

# Type checking
poetry run mypy python_accounting/
```

## 📝 Changelog

See [CHANGELOG](https://github.com/ekmungai/python-accounting/blob/main/CHANGELOG.md) for version history.

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING](https://github.com/ekmungai/python-accounting/blob/main/CONTRIBUTING) for guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/ekmungai/python-accounting/blob/main/LICENSE) file for details.

## 🙏 Acknowledgments

This library is a community initiative by [microbooks.io](https://microbooks.io).

---

**Built with ❤️ for the accounting community**
