# utils/batch.py
# Copyright (C) 2024 - 2028 the PythonAccounting authors and contributors
# <see AUTHORS file>
#
# This module is part of PythonAccounting and is released under
# the MIT License: https://www.opensource.org/licenses/mit-license.php

"""
Batch operations for improved performance when handling large datasets.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Dict, Any, TypeVar, Generic, Callable
from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime

if TYPE_CHECKING:
    from sqlalchemy.orm import Session
    from python_accounting.models import Account, Transaction, LineItem


T = TypeVar("T")


@dataclass
class BatchResult(Generic[T]):
    """Result of a batch operation."""
    
    successful: List[T]
    """Successfully processed items."""
    
    failed: List[Dict[str, Any]]
    """Failed items with error details."""
    
    total: int
    """Total number of items processed."""
    
    @property
    def success_count(self) -> int:
        """Number of successful operations."""
        return len(self.successful)
    
    @property
    def failure_count(self) -> int:
        """Number of failed operations."""
        return len(self.failed)
    
    @property
    def success_rate(self) -> float:
        """Success rate as a percentage."""
        if self.total == 0:
            return 0.0
        return (self.success_count / self.total) * 100


class BatchProcessor:
    """
    Handles batch operations for improved performance.
    
    This class provides methods for bulk inserting, updating, and 
    processing accounting records efficiently.
    """
    
    def __init__(self, session: "Session", batch_size: int = 100):
        """
        Initialize the batch processor.
        
        Args:
            session: The database session.
            batch_size: Number of records to process in each batch.
        """
        self.session = session
        self.batch_size = batch_size
    
    def bulk_create_accounts(
        self,
        accounts_data: List[Dict[str, Any]],
    ) -> BatchResult["Account"]:
        """
        Create multiple accounts in a batch.
        
        Args:
            accounts_data: List of account data dictionaries with keys:
                - name: Account name
                - account_type: Account type (string or enum)
                - currency_id: Currency ID
                - category_id: Optional category ID
                - description: Optional description
                
        Returns:
            BatchResult with successful and failed accounts.
        """
        from python_accounting.models import Account
        
        successful = []
        failed = []
        
        for i, data in enumerate(accounts_data):
            try:
                # Convert account_type string to enum if needed
                account_type = data.get("account_type")
                if isinstance(account_type, str):
                    account_type = Account.AccountType[account_type]
                
                account = Account(
                    name=data["name"],
                    account_type=account_type,
                    currency_id=data["currency_id"],
                    entity_id=self.session.entity.id,
                    category_id=data.get("category_id"),
                    description=data.get("description"),
                )
                self.session.add(account)
                
                # Commit in batches
                if (i + 1) % self.batch_size == 0:
                    self.session.commit()
                    
                successful.append(account)
                
            except Exception as e:
                failed.append({
                    "index": i,
                    "data": data,
                    "error": str(e),
                })
        
        # Final commit
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            # Mark remaining as failed
            for item in successful[-self.batch_size:]:
                failed.append({
                    "data": {"name": item.name},
                    "error": f"Batch commit failed: {e}",
                })
        
        return BatchResult(
            successful=successful,
            failed=failed,
            total=len(accounts_data),
        )
    
    def bulk_create_transactions(
        self,
        transactions_data: List[Dict[str, Any]],
        auto_post: bool = True,
    ) -> BatchResult["Transaction"]:
        """
        Create multiple transactions in a batch.
        
        Args:
            transactions_data: List of transaction data dictionaries with keys:
                - transaction_type: Type of transaction (e.g., 'CashSale')
                - narration: Transaction description
                - transaction_date: Date of transaction
                - account_id: Main account ID
                - line_items: List of line item dictionaries
                
        Returns:
            BatchResult with successful and failed transactions.
        """
        from python_accounting.models import Transaction, LineItem
        from python_accounting.transactions import (
            CashSale, ClientInvoice, CashPurchase, SupplierBill,
            ClientReceipt, SupplierPayment, JournalEntry
        )
        
        transaction_classes = {
            "CashSale": CashSale,
            "ClientInvoice": ClientInvoice,
            "CashPurchase": CashPurchase,
            "SupplierBill": SupplierBill,
            "ClientReceipt": ClientReceipt,
            "SupplierPayment": SupplierPayment,
            "JournalEntry": JournalEntry,
        }
        
        successful = []
        failed = []
        
        for i, data in enumerate(transactions_data):
            try:
                # Get transaction class
                tx_type = data.get("transaction_type", "JournalEntry")
                tx_class = transaction_classes.get(tx_type, JournalEntry)
                
                # Create transaction
                transaction = tx_class(
                    narration=data["narration"],
                    transaction_date=data.get("transaction_date", datetime.now()),
                    account_id=data["account_id"],
                    entity_id=self.session.entity.id,
                )
                self.session.add(transaction)
                self.session.flush()
                
                # Add line items
                for li_data in data.get("line_items", []):
                    line_item = LineItem(
                        narration=li_data.get("narration", data["narration"]),
                        account_id=li_data["account_id"],
                        amount=Decimal(str(li_data["amount"])),
                        quantity=li_data.get("quantity", 1),
                        tax_id=li_data.get("tax_id"),
                        entity_id=self.session.entity.id,
                    )
                    self.session.add(line_item)
                    self.session.flush()
                    transaction.line_items.add(line_item)
                
                # Post if requested
                if auto_post:
                    transaction.post(self.session)
                
                successful.append(transaction)
                
                # Commit in batches
                if (i + 1) % self.batch_size == 0:
                    self.session.commit()
                    
            except Exception as e:
                self.session.rollback()
                failed.append({
                    "index": i,
                    "data": data,
                    "error": str(e),
                })
        
        # Final commit
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
        
        return BatchResult(
            successful=successful,
            failed=failed,
            total=len(transactions_data),
        )
    
    def bulk_balance_query(
        self,
        account_ids: List[int],
        as_of_date: datetime = None,
    ) -> Dict[int, Decimal]:
        """
        Get balances for multiple accounts efficiently.
        
        Args:
            account_ids: List of account IDs to query.
            as_of_date: Optional date for balance calculation.
            
        Returns:
            Dictionary mapping account ID to balance.
        """
        from python_accounting.models import Account
        from sqlalchemy import select
        
        if as_of_date is None:
            as_of_date = datetime.now()
        
        balances = {}
        
        # Fetch accounts in batches
        for i in range(0, len(account_ids), self.batch_size):
            batch_ids = account_ids[i:i + self.batch_size]
            
            stmt = select(Account).where(
                Account.id.in_(batch_ids),
                Account.entity_id == self.session.entity.id,
            )
            accounts = self.session.execute(stmt).scalars().all()
            
            for account in accounts:
                balances[account.id] = account.closing_balance(self.session, as_of_date)
        
        return balances
    
    def process_items(
        self,
        items: List[T],
        processor: Callable[[T], Any],
        error_handler: Callable[[T, Exception], None] = None,
    ) -> BatchResult:
        """
        Process a list of items with a custom function.
        
        Args:
            items: List of items to process.
            processor: Function to apply to each item.
            error_handler: Optional function to handle errors.
            
        Returns:
            BatchResult with results.
        """
        successful = []
        failed = []
        
        for i, item in enumerate(items):
            try:
                result = processor(item)
                successful.append(result)
                
                if (i + 1) % self.batch_size == 0:
                    self.session.commit()
                    
            except Exception as e:
                if error_handler:
                    error_handler(item, e)
                failed.append({
                    "index": i,
                    "item": str(item),
                    "error": str(e),
                })
        
        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
        
        return BatchResult(
            successful=successful,
            failed=failed,
            total=len(items),
        )
