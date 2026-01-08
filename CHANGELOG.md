# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-01-08

### Added

#### Multi-Currency Support
- New `ExchangeRate` model for storing exchange rates with historical tracking
- `ExchangeRate.get_rate()` method for looking up rates as of a specific date
- `ExchangeRate.convert()` method for currency conversion
- Support for triangulated currency conversion

#### Budget Management
- New `Budget` model for financial planning
- `Budget.variance()` and `Budget.variance_percentage()` methods
- `Budget.get_summary()` for budget overview by period

#### Export Capabilities
- New `exporters` module with support for:
  - CSV export
  - JSON export
  - Excel export (requires `openpyxl`)
  - PDF export (requires `reportlab`)
- `export_report()` convenience function

#### New Financial Reports
- `EquityStatement` - Statement of Changes in Equity (IFRS/GAAP compliant)
- `BudgetReport` - Budget vs Actual comparison with variance analysis

#### Event System
- New `events` module for hooks and callbacks
- `EventManager` class for subscribing to and emitting events
- Support for: transaction, balance, period, account, and assignment events
- Event history tracking

#### CLI Tool
- `pyaccount` command-line interface
- Database initialization: `pyaccount init`
- Entity management: `pyaccount entity create/list`
- Account listing: `pyaccount account list`
- Report generation with export: `pyaccount report income-statement/balance-sheet/cashflow`

#### Internationalization
- New `locales` module for multi-language support
- Built-in translations: English, German, French, Dutch
- `set_locale()` and `t()` functions for translation

#### Batch Operations
- New `utils/batch.py` module for efficient bulk operations
- `BatchProcessor` class with methods:
  - `bulk_create_accounts()`
  - `bulk_create_transactions()`
  - `bulk_balance_query()`
- `BatchResult` dataclass with success/failure tracking

#### Enhanced Error Handling
- Complete rewrite of `exceptions` module
- Error codes with format PAxxxx (e.g., PA1001)
- Categories: Transaction (PA1xxx), Account (PA2xxx), Balance (PA3xxx), Period (PA4xxx), Validation (PA5xxx), System (PA9xxx)
- `to_dict()` method for API-friendly error responses

### Changed

#### Dependencies
- Updated Python support: 3.10, 3.11, 3.12, 3.13
- Updated SQLAlchemy to ^2.0.36
- Updated pytest to ^8.3.0
- Database drivers (mysqlclient, psycopg2-binary) moved to optional extras
- Added new dependencies: pydantic, rich, click

#### CI/CD
- Enhanced GitHub Actions workflow
- Multi-database matrix testing (SQLite, PostgreSQL, MySQL)
- Code coverage with Codecov integration
- Separate lint, test, and build jobs

#### Documentation
- Completely rewritten README with:
  - Badges (build status, coverage, PyPI version, license)
  - Feature highlights
  - Comprehensive usage examples
  - Advanced feature documentation

### Added Files
- `python_accounting/models/exchange_rate.py`
- `python_accounting/models/budget.py`
- `python_accounting/events/__init__.py`
- `python_accounting/exporters/__init__.py`
- `python_accounting/cli/__init__.py`
- `python_accounting/reports/equity_statement.py`
- `python_accounting/reports/budget_report.py`
- `python_accounting/locales/__init__.py`
- `python_accounting/utils/batch.py`
- `.pre-commit-config.yaml`

## [1.0.1] - 2024-03-01

### Fixed
- Minor bug fixes

## [1.0.0] - 2024-03-01

### Added
- Initial release
- Double entry bookkeeping
- Income Statement
- Balance Sheet
- Cashflow Statement
- Trial Balance
- Aging Schedule
- Transaction types: CashSale, ClientInvoice, CashPurchase, SupplierBill, ClientReceipt, SupplierPayment, JournalEntry, CreditNote, DebitNote, ContraEntry
