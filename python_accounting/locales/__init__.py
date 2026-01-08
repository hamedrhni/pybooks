# locales/__init__.py
# Copyright (C) 2024 - 2028 the PythonAccounting authors and contributors
# <see AUTHORS file>
#
# This module is part of PythonAccounting and is released under
# the MIT License: https://www.opensource.org/licenses/mit-license.php

"""
Internationalization (i18n) support for Python Accounting.

This module provides multi-language support for error messages, report labels,
and other user-facing strings.

Usage:
    from python_accounting.locales import get_translator, set_locale
    
    # Set the locale
    set_locale("de")
    
    # Get translated strings
    t = get_translator()
    print(t("report.income_statement.title"))  # "Gewinn- und Verlustrechnung"
"""

from __future__ import annotations

from typing import Dict, Any, Optional
from pathlib import Path
import json

# Default locale
_current_locale: str = "en"

# Translation storage
_translations: Dict[str, Dict[str, Any]] = {}

# Available locales
AVAILABLE_LOCALES = [
    "en",  # English (default)
    "de",  # German
    "fr",  # French
    "es",  # Spanish
    "nl",  # Dutch
    "pt",  # Portuguese
]


def _load_translations(locale: str) -> Dict[str, Any]:
    """
    Load translations for a specific locale.
    
    Args:
        locale: The locale code (e.g., 'en', 'de').
        
    Returns:
        Dictionary of translations.
    """
    if locale in _translations:
        return _translations[locale]
    
    # Try to load from file
    locale_file = Path(__file__).parent / f"{locale}.json"
    if locale_file.exists():
        with open(locale_file, "r", encoding="utf-8") as f:
            _translations[locale] = json.load(f)
    else:
        # Fall back to default translations
        _translations[locale] = _get_default_translations(locale)
    
    return _translations[locale]


def _get_default_translations(locale: str) -> Dict[str, Any]:
    """
    Get default translations (English base with some common translations).
    
    Args:
        locale: The locale code.
        
    Returns:
        Dictionary of translations.
    """
    # English base translations
    base = {
        "reports": {
            "income_statement": {
                "title": "Income Statement",
                "operating_revenues": "Operating Revenues",
                "operating_expenses": "Operating Expenses",
                "gross_profit": "Gross Profit",
                "net_profit": "Net Profit",
            },
            "balance_sheet": {
                "title": "Balance Sheet",
                "assets": "Assets",
                "liabilities": "Liabilities",
                "equity": "Equity",
                "total_assets": "Total Assets",
                "total_liabilities": "Total Liabilities",
                "net_assets": "Net Assets",
            },
            "cashflow": {
                "title": "Cashflow Statement",
                "operating": "Operating Cash Flow",
                "investing": "Investment Cash Flow",
                "financing": "Financing Cash Flow",
                "net_cashflow": "Net Cash Flow",
            },
            "equity_statement": {
                "title": "Statement of Changes in Equity",
                "opening_balance": "Opening Balance",
                "closing_balance": "Closing Balance",
            },
            "budget_report": {
                "title": "Budget vs Actual Report",
                "budgeted": "Budgeted",
                "actual": "Actual",
                "variance": "Variance",
                "favorable": "Favorable",
                "unfavorable": "Unfavorable",
            },
        },
        "accounts": {
            "types": {
                "asset": "Asset",
                "liability": "Liability",
                "equity": "Equity",
                "revenue": "Revenue",
                "expense": "Expense",
            },
        },
        "errors": {
            "invalid_transaction": "Invalid transaction",
            "insufficient_balance": "Insufficient balance",
            "period_closed": "Reporting period is closed",
            "missing_line_items": "Transaction must have at least one line item",
        },
        "common": {
            "total": "Total",
            "date": "Date",
            "description": "Description",
            "amount": "Amount",
            "balance": "Balance",
        },
    }
    
    # German translations
    if locale == "de":
        return {
            "reports": {
                "income_statement": {
                    "title": "Gewinn- und Verlustrechnung",
                    "operating_revenues": "Betriebliche Erträge",
                    "operating_expenses": "Betriebliche Aufwendungen",
                    "gross_profit": "Bruttogewinn",
                    "net_profit": "Nettogewinn",
                },
                "balance_sheet": {
                    "title": "Bilanz",
                    "assets": "Aktiva",
                    "liabilities": "Passiva",
                    "equity": "Eigenkapital",
                    "total_assets": "Summe Aktiva",
                    "total_liabilities": "Summe Verbindlichkeiten",
                    "net_assets": "Reinvermögen",
                },
                "cashflow": {
                    "title": "Kapitalflussrechnung",
                    "operating": "Operativer Cashflow",
                    "investing": "Investitions-Cashflow",
                    "financing": "Finanzierungs-Cashflow",
                    "net_cashflow": "Netto-Cashflow",
                },
            },
            "common": {
                "total": "Gesamt",
                "date": "Datum",
                "description": "Beschreibung",
                "amount": "Betrag",
                "balance": "Saldo",
            },
        }
    
    # French translations
    if locale == "fr":
        return {
            "reports": {
                "income_statement": {
                    "title": "Compte de Résultat",
                    "operating_revenues": "Produits d'exploitation",
                    "operating_expenses": "Charges d'exploitation",
                    "gross_profit": "Marge brute",
                    "net_profit": "Résultat net",
                },
                "balance_sheet": {
                    "title": "Bilan",
                    "assets": "Actif",
                    "liabilities": "Passif",
                    "equity": "Capitaux propres",
                },
            },
            "common": {
                "total": "Total",
                "date": "Date",
                "description": "Description",
                "amount": "Montant",
                "balance": "Solde",
            },
        }
    
    # Dutch translations
    if locale == "nl":
        return {
            "reports": {
                "income_statement": {
                    "title": "Winst- en Verliesrekening",
                    "operating_revenues": "Bedrijfsopbrengsten",
                    "operating_expenses": "Bedrijfskosten",
                    "gross_profit": "Brutowinst",
                    "net_profit": "Nettowinst",
                },
                "balance_sheet": {
                    "title": "Balans",
                    "assets": "Activa",
                    "liabilities": "Passiva",
                    "equity": "Eigen vermogen",
                },
            },
            "common": {
                "total": "Totaal",
                "date": "Datum",
                "description": "Omschrijving",
                "amount": "Bedrag",
                "balance": "Saldo",
            },
        }
    
    return base


def set_locale(locale: str) -> None:
    """
    Set the current locale.
    
    Args:
        locale: The locale code (e.g., 'en', 'de', 'fr').
        
    Raises:
        ValueError: If the locale is not supported.
    """
    global _current_locale
    
    if locale not in AVAILABLE_LOCALES:
        raise ValueError(
            f"Unsupported locale: {locale}. "
            f"Available locales: {', '.join(AVAILABLE_LOCALES)}"
        )
    
    _current_locale = locale
    _load_translations(locale)


def get_locale() -> str:
    """
    Get the current locale.
    
    Returns:
        The current locale code.
    """
    return _current_locale


def get_translator():
    """
    Get a translator function for the current locale.
    
    Returns:
        A function that takes a dotted key path and returns the translated string.
    """
    translations = _load_translations(_current_locale)
    
    def translate(key: str, default: Optional[str] = None) -> str:
        """
        Translate a key to the current locale.
        
        Args:
            key: Dotted key path (e.g., 'reports.income_statement.title').
            default: Default value if translation not found.
            
        Returns:
            The translated string or the default/key if not found.
        """
        parts = key.split(".")
        value = translations
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default if default is not None else key
        
        return value if isinstance(value, str) else (default or key)
    
    return translate


# Shorthand function
def t(key: str, default: Optional[str] = None) -> str:
    """
    Translate a key to the current locale.
    
    This is a shorthand for get_translator()(key, default).
    
    Args:
        key: Dotted key path (e.g., 'reports.income_statement.title').
        default: Default value if translation not found.
        
    Returns:
        The translated string or the default/key if not found.
    """
    return get_translator()(key, default)
