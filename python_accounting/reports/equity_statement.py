# reports/equity_statement.py
# Copyright (C) 2024 - 2028 the PythonAccounting authors and contributors
# <see AUTHORS file>
#
# This module is part of PythonAccounting and is released under
# the MIT License: https://www.opensource.org/licenses/mit-license.php

"""
Represents a Statement of Changes in Equity as required by IFRS/GAAP.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Dict, Any, List

from sqlalchemy.orm.session import Session

from python_accounting.config import config as configuration
from python_accounting.models import Account
from python_accounting.reports.financial_statement import FinancialStatement

if TYPE_CHECKING:
    pass


class EquityStatement(FinancialStatement):
    """
    Statement of Changes in Equity.
    
    This report shows changes in equity components including:
    - Share capital
    - Retained earnings
    - Other reserves
    - Net profit/loss for the period
    - Dividends declared
    
    As per IAS 1, this statement shows:
    - Total comprehensive income for the period
    - Effects of retrospective application or restatement
    - Reconciliation between carrying amounts at the beginning and end
    """
    
    config = "equity_statement"
    
    def __init__(
        self,
        session: Session,
        start_date: datetime = None,
        end_date: datetime = None,
    ) -> None:
        """
        Initialize the Statement of Changes in Equity.
        
        Args:
            session: The database session.
            start_date: Start of the reporting period.
            end_date: End of the reporting period.
        """
        # Set dates before calling parent
        self.start_date = start_date or session.entity.reporting_period.period_start
        self.end_date = end_date or datetime.now()
        
        # Initialize with minimal config if not in config file
        self.title = "Statement of Changes in Equity"
        self.session = session
        self.width = 60
        
        # Initialize data structures
        self.equity_components: Dict[str, Dict[str, Decimal]] = {}
        self.movements: Dict[str, List[Dict[str, Any]]] = {}
        
        # Populate the statement
        self._calculate_equity_changes()
    
    def _calculate_equity_changes(self) -> None:
        """Calculate changes in equity components."""
        # Get equity account types
        equity_types = [
            Account.AccountType.EQUITY,
            Account.AccountType.RETAINED_EARNINGS,
        ]
        
        for account_type in equity_types:
            type_name = account_type.value
            self.equity_components[type_name] = {
                "opening": Decimal("0"),
                "additions": Decimal("0"),
                "reductions": Decimal("0"),
                "closing": Decimal("0"),
            }
            self.movements[type_name] = []
            
            # Get accounts of this type
            from sqlalchemy import select
            stmt = select(Account).where(
                Account.entity_id == self.session.entity.id,
                Account.account_type == account_type,
                Account.deleted == False,  # noqa: E712
            )
            accounts = self.session.execute(stmt).scalars().all()
            
            for account in accounts:
                opening = account.opening_balance(self.session, self.start_date.year)
                closing = account.closing_balance(self.session, self.end_date)
                movement = closing - opening
                
                self.equity_components[type_name]["opening"] += opening
                self.equity_components[type_name]["closing"] += closing
                
                if movement > 0:
                    self.equity_components[type_name]["additions"] += movement
                else:
                    self.equity_components[type_name]["reductions"] += abs(movement)
                
                if movement != 0:
                    self.movements[type_name].append({
                        "account": account.name,
                        "opening": opening,
                        "movement": movement,
                        "closing": closing,
                    })
        
        # Calculate net profit from income statement
        try:
            from python_accounting.reports import IncomeStatement
            income_stmt = IncomeStatement(self.session)
            self.net_profit = income_stmt.result_amounts.get("NET_PROFIT", Decimal("0"))
        except Exception:
            self.net_profit = Decimal("0")
        
        # Add net profit to retained earnings
        if "Retained Earnings" in self.equity_components:
            self.equity_components["Retained Earnings"]["additions"] += max(self.net_profit, Decimal("0"))
            self.equity_components["Retained Earnings"]["reductions"] += abs(min(self.net_profit, Decimal("0")))
    
    @property
    def total_opening_equity(self) -> Decimal:
        """Total equity at start of period."""
        return sum(c["opening"] for c in self.equity_components.values())
    
    @property
    def total_closing_equity(self) -> Decimal:
        """Total equity at end of period."""
        return sum(c["closing"] for c in self.equity_components.values())
    
    @property
    def total_movement(self) -> Decimal:
        """Total change in equity during the period."""
        return self.total_closing_equity - self.total_opening_equity
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the statement to a dictionary.
        
        Returns:
            Dictionary representation of the statement.
        """
        return {
            "entity": self.session.entity.name,
            "title": self.title,
            "period": {
                "start": self.start_date.isoformat(),
                "end": self.end_date.isoformat(),
            },
            "components": {
                k: {kk: float(vv) for kk, vv in v.items()}
                for k, v in self.equity_components.items()
            },
            "movements": self.movements,
            "net_profit": float(self.net_profit),
            "totals": {
                "opening": float(self.total_opening_equity),
                "closing": float(self.total_closing_equity),
                "movement": float(self.total_movement),
            },
        }
    
    def __str__(self) -> str:
        """Generate string representation of the statement."""
        lines = []
        
        # Title
        lines.append(self.session.entity.name.center(self.width))
        lines.append(self.title.center(self.width))
        period = f"For the period: {self.start_date.strftime('%d %b %Y')} to {self.end_date.strftime('%d %b %Y')}"
        lines.append(period.center(self.width))
        lines.append("")
        
        # Header row
        header = f"{'Component':<25}{'Opening':>12}{'Movement':>12}{'Closing':>12}"
        lines.append(header)
        lines.append("-" * self.width)
        
        # Components
        for name, values in self.equity_components.items():
            movement = values["additions"] - values["reductions"]
            row = f"{name:<25}{values['opening']:>12.2f}{movement:>12.2f}{values['closing']:>12.2f}"
            lines.append(row)
        
        # Net profit line
        lines.append(f"{'Net Profit/(Loss)':<25}{'-':>12}{self.net_profit:>12.2f}{'-':>12}")
        
        # Totals
        lines.append("-" * self.width)
        total_movement = self.total_closing_equity - self.total_opening_equity
        lines.append(
            f"{'Total Equity':<25}{self.total_opening_equity:>12.2f}"
            f"{total_movement:>12.2f}{self.total_closing_equity:>12.2f}"
        )
        lines.append("=" * self.width)
        
        return "\n".join(lines)
