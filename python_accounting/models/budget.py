# models/budget.py
# Copyright (C) 2024 - 2028 the PythonAccounting authors and contributors
# <see AUTHORS file>
#
# This module is part of PythonAccounting and is released under
# the MIT License: https://www.opensource.org/licenses/mit-license.php

"""
Represents a budget for financial planning and variance analysis.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional, Dict, Any

from sqlalchemy import ForeignKey, Numeric, DateTime, String, select, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from python_accounting.models.recyclable import Recyclable

if TYPE_CHECKING:
    from sqlalchemy.orm import Session
    from python_accounting.models import Account, ReportingPeriod


class Budget(Recyclable):
    """
    Represents a budget allocation for a specific account and period.
    
    Budgets can be used to track planned vs actual spending/revenue
    and generate variance analysis reports.
    
    Attributes:
        account_id: The account this budget applies to.
        reporting_period_id: The reporting period for this budget.
        amount: The budgeted amount.
        name: Optional name/description for this budget line.
        budget_type: Type of budget (ANNUAL, QUARTERLY, MONTHLY).
    """
    
    __tablename__ = "budget"

    account_id: Mapped[int] = mapped_column(ForeignKey("account.id"), nullable=False)
    reporting_period_id: Mapped[int] = mapped_column(
        ForeignKey("reporting_period.id"), nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(precision=18, scale=4), nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    budget_type: Mapped[str] = mapped_column(String(20), default="ANNUAL")
    
    # Relationships
    account: Mapped["Account"] = relationship("Account", lazy="joined")
    reporting_period: Mapped["ReportingPeriod"] = relationship("ReportingPeriod", lazy="joined")
    
    def __repr__(self) -> str:
        return f"Budget({self.name or self.account.name}: {self.amount})"
    
    def actual_amount(self, session: "Session") -> Decimal:
        """
        Get the actual amount spent/received for this budget's account and period.
        
        Args:
            session: The database session.
            
        Returns:
            The actual amount from transactions.
        """
        from python_accounting.models import Ledger
        
        start_date = self.reporting_period.period_start
        end_date = self.reporting_period.period_end
        
        return self.account.closing_balance(session, end_date) - \
               self.account.opening_balance(session, start_date.year)
    
    def variance(self, session: "Session") -> Decimal:
        """
        Calculate the variance between budget and actual.
        
        Positive variance means under budget, negative means over budget
        for expense accounts. For revenue accounts, positive means
        exceeded target.
        
        Args:
            session: The database session.
            
        Returns:
            The variance amount (budget - actual for expenses, actual - budget for revenue).
        """
        actual = self.actual_amount(session)
        
        # Check if this is an expense or revenue account
        from python_accounting.models import Account
        expense_types = [
            Account.AccountType.OPERATING_EXPENSE,
            Account.AccountType.DIRECT_EXPENSE,
            Account.AccountType.OVERHEAD_EXPENSE,
            Account.AccountType.OTHER_EXPENSE,
        ]
        
        if self.account.account_type in expense_types:
            return self.amount - actual  # Positive = under budget (good)
        else:
            return actual - self.amount  # Positive = exceeded target (good)
    
    def variance_percentage(self, session: "Session") -> Decimal:
        """
        Calculate the variance as a percentage of the budget.
        
        Args:
            session: The database session.
            
        Returns:
            The variance as a percentage.
        """
        if self.amount == 0:
            return Decimal("0")
        return (self.variance(session) / abs(self.amount)) * 100
    
    @classmethod
    def get_summary(
        cls,
        session: "Session",
        reporting_period_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Get a summary of all budgets for a reporting period.
        
        Args:
            session: The database session.
            reporting_period_id: Optional period ID. Defaults to current period.
            
        Returns:
            Dictionary with budget summary including totals and variances.
        """
        from python_accounting.models import ReportingPeriod
        
        if reporting_period_id is None:
            period = ReportingPeriod.current_period(session)
            if period:
                reporting_period_id = period.id
            else:
                return {"error": "No current reporting period found"}
        
        stmt = select(cls).where(
            cls.reporting_period_id == reporting_period_id,
            cls.entity_id == session.entity.id,
            cls.deleted == False,  # noqa: E712
        )
        
        budgets = session.execute(stmt).scalars().all()
        
        total_budgeted = Decimal("0")
        total_actual = Decimal("0")
        total_variance = Decimal("0")
        
        details = []
        for budget in budgets:
            actual = budget.actual_amount(session)
            variance = budget.variance(session)
            
            total_budgeted += budget.amount
            total_actual += actual
            total_variance += variance
            
            details.append({
                "account": budget.account.name,
                "budgeted": budget.amount,
                "actual": actual,
                "variance": variance,
                "variance_pct": budget.variance_percentage(session),
            })
        
        return {
            "period_id": reporting_period_id,
            "total_budgeted": total_budgeted,
            "total_actual": total_actual,
            "total_variance": total_variance,
            "details": details,
        }
