# exceptions/__init__.py
# Copyright (C) 2024 - 2028 the PythonAccounting authors and contributors
# <see AUTHORS file>
#
# This module is part of PythonAccounting and is released under
# the MIT License: https://www.opensource.org/licenses/mit-license.php

"""
Custom exceptions for Python Accounting with error codes.

Each exception has:
- A unique error code for programmatic handling
- A descriptive message
- Optional context data

Error Code Format:
- PA1xxx: Transaction errors
- PA2xxx: Account errors  
- PA3xxx: Balance errors
- PA4xxx: Period errors
- PA5xxx: Validation errors
- PA9xxx: System errors
"""

from __future__ import annotations

from typing import Dict, Any, Optional


class AccountingError(Exception):
    """
    Base exception for all accounting errors.
    
    Attributes:
        code: Unique error code (e.g., 'PA1001').
        message: Human-readable error message.
        context: Additional context data.
    """
    
    code: str = "PA0000"
    default_message: str = "An accounting error occurred"
    
    def __init__(
        self,
        message: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        self.message = message or self.default_message
        self.context = context or {}
        super().__init__(self.message)
    
    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            "error_code": self.code,
            "message": self.message,
            "context": self.context,
        }


# Transaction Errors (PA1xxx)

class PostedTransactionError(AccountingError):
    """Raised when attempting to modify a posted transaction."""
    code = "PA1001"
    default_message = "Cannot modify a posted transaction"


class MissingLineItemError(AccountingError):
    """Raised when a transaction has no line items."""
    code = "PA1002"
    default_message = "Transaction must have at least one line item"


class RedundantTransactionError(AccountingError):
    """Raised when transaction main account is also a line item account."""
    code = "PA1003"
    default_message = "Transaction main account cannot be a line item account"


class InvalidTransactionTypeError(AccountingError):
    """Raised when an invalid transaction type is used."""
    code = "PA1004"
    default_message = "Invalid transaction type for this operation"


class InvalidTransactionDateError(AccountingError):
    """Raised when transaction date is invalid for the reporting period."""
    code = "PA1005"
    default_message = "Transaction date is outside the current reporting period"


class UnbalancedTransactionError(AccountingError):
    """Raised when debits don't equal credits."""
    code = "PA1006"
    default_message = "Transaction is not balanced - debits must equal credits"


# Account Errors (PA2xxx)

class InvalidAccountTypeError(AccountingError):
    """Raised when an account type is invalid for the operation."""
    code = "PA2001"
    default_message = "Invalid account type for this operation"


class InvalidCategoryAccountTypeError(AccountingError):
    """Raised when account type doesn't match category."""
    code = "PA2002"
    default_message = "Account type does not match the category type"


class HangingTransactionsError(AccountingError):
    """Raised when trying to delete account with transactions."""
    code = "PA2003"
    default_message = "Cannot delete account with existing transactions"


class DuplicateAccountError(AccountingError):
    """Raised when creating a duplicate account."""
    code = "PA2004"
    default_message = "An account with this code already exists"


# Balance Errors (PA3xxx)

class InsufficientBalanceError(AccountingError):
    """Raised when account has insufficient balance."""
    code = "PA3001"
    default_message = "Insufficient balance for this operation"


class NegativeAmountError(AccountingError):
    """Raised when a negative amount is provided where positive is required."""
    code = "PA3002"
    default_message = "Amount cannot be negative"


class InvalidBalanceTransactionError(AccountingError):
    """Raised when balance transaction type is invalid."""
    code = "PA3003"
    default_message = "Invalid transaction type for opening balance"


class AdjustingReportingPeriodError(AccountingError):
    """Raised when adjusting an invalid reporting period."""
    code = "PA3004"
    default_message = "Cannot adjust this reporting period"


# Period Errors (PA4xxx)

class ClosedReportingPeriodError(AccountingError):
    """Raised when operating on a closed period."""
    code = "PA4001"
    default_message = "This reporting period is closed"


class MissingReportingPeriodError(AccountingError):
    """Raised when no reporting period is found."""
    code = "PA4002"
    default_message = "No active reporting period found"


class InvalidReportingPeriodError(AccountingError):
    """Raised when reporting period configuration is invalid."""
    code = "PA4003"
    default_message = "Invalid reporting period configuration"


# Validation Errors (PA5xxx)

class MissingEntityError(AccountingError):
    """Raised when entity is required but not provided."""
    code = "PA5001"
    default_message = "Entity is required for this operation"


class InvalidAssignmentError(AccountingError):
    """Raised when assignment configuration is invalid."""
    code = "PA5002"
    default_message = "Invalid assignment configuration"


class SelfAssignmentError(AccountingError):
    """Raised when trying to assign a transaction to itself."""
    code = "PA5003"
    default_message = "Cannot assign a transaction to itself"


class OverAssignmentError(AccountingError):
    """Raised when assignment amount exceeds available balance."""
    code = "PA5004"
    default_message = "Assignment amount exceeds available balance"


class InvalidExchangeRateError(AccountingError):
    """Raised when exchange rate is invalid or not found."""
    code = "PA5005"
    default_message = "Exchange rate not found for the specified currencies"


# System Errors (PA9xxx)

class IntegrityError(AccountingError):
    """Raised when ledger integrity check fails."""
    code = "PA9001"
    default_message = "Ledger integrity check failed - data may have been tampered"


class ConfigurationError(AccountingError):
    """Raised when configuration is invalid."""
    code = "PA9002"
    default_message = "Invalid configuration"


class DatabaseError(AccountingError):
    """Raised when database operation fails."""
    code = "PA9003"
    default_message = "Database operation failed"


# Export error code mapping for easy lookup
ERROR_CODES = {
    "PA1001": PostedTransactionError,
    "PA1002": MissingLineItemError,
    "PA1003": RedundantTransactionError,
    "PA1004": InvalidTransactionTypeError,
    "PA1005": InvalidTransactionDateError,
    "PA1006": UnbalancedTransactionError,
    "PA2001": InvalidAccountTypeError,
    "PA2002": InvalidCategoryAccountTypeError,
    "PA2003": HangingTransactionsError,
    "PA2004": DuplicateAccountError,
    "PA3001": InsufficientBalanceError,
    "PA3002": NegativeAmountError,
    "PA3003": InvalidBalanceTransactionError,
    "PA3004": AdjustingReportingPeriodError,
    "PA4001": ClosedReportingPeriodError,
    "PA4002": MissingReportingPeriodError,
    "PA4003": InvalidReportingPeriodError,
    "PA5001": MissingEntityError,
    "PA5002": InvalidAssignmentError,
    "PA5003": SelfAssignmentError,
    "PA5004": OverAssignmentError,
    "PA5005": InvalidExchangeRateError,
    "PA9001": IntegrityError,
    "PA9002": ConfigurationError,
    "PA9003": DatabaseError,
}


def get_error_by_code(code: str) -> type:
    """
    Get exception class by error code.
    
    Args:
        code: The error code (e.g., 'PA1001').
        
    Returns:
        The exception class.
        
    Raises:
        KeyError: If code is not found.
    """
    return ERROR_CODES[code]
