# reports/budget_report.py
# Copyright (C) 2024 - 2028 the PythonAccounting authors and contributors
# <see AUTHORS file>
#
# This module is part of PythonAccounting and is released under
# the MIT License: https://www.opensource.org/licenses/mit-license.php

"""
Budget vs Actual Report for variance analysis.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Dict, Any, List, Optional

from sqlalchemy import select
from sqlalchemy.orm.session import Session

if TYPE_CHECKING:
    pass


class BudgetReport:
    """
    Budget vs Actual Comparison Report.
    
    This report compares budgeted amounts against actual transaction amounts
    to identify variances and provide insights for financial management.
    
    Features:
    - Budget vs Actual comparison by account
    - Variance analysis (absolute and percentage)
    - Categorization by account type
    - Favorable/Unfavorable variance indicators
    """
    
    def __init__(
        self,
        session: Session,
        reporting_period_id: Optional[int] = None,
    ) -> None:
        """
        Initialize the Budget Report.
        
        Args:
            session: The database session.
            reporting_period_id: Optional reporting period ID. Defaults to current period.
        """
        self.session = session
        self.title = "Budget vs Actual Report"
        self.width = 80
        self.generated_at = datetime.now()
        
        # Get reporting period
        from python_accounting.models import ReportingPeriod
        
        if reporting_period_id:
            self.reporting_period = session.get(ReportingPeriod, reporting_period_id)
        else:
            self.reporting_period = ReportingPeriod.current_period(session)
        
        if not self.reporting_period:
            raise ValueError("No reporting period found")
        
        # Initialize data structures
        self.budget_lines: List[Dict[str, Any]] = []
        self.summaries: Dict[str, Dict[str, Decimal]] = {}
        
        # Calculate the report
        self._calculate_report()
    
    def _calculate_report(self) -> None:
        """Calculate budget vs actual comparisons."""
        from python_accounting.models import Budget, Account
        
        # Get all budgets for the period
        stmt = select(Budget).where(
            Budget.entity_id == self.session.entity.id,
            Budget.reporting_period_id == self.reporting_period.id,
            Budget.deleted == False,  # noqa: E712
        )
        budgets = self.session.execute(stmt).scalars().all()
        
        # Track summaries by account type
        type_summaries: Dict[str, Dict[str, Decimal]] = {}
        
        for budget in budgets:
            actual = budget.actual_amount(self.session)
            variance = budget.variance(self.session)
            variance_pct = budget.variance_percentage(self.session)
            
            # Determine if favorable
            # For expenses: under budget is favorable (positive variance)
            # For revenue: over budget is favorable (positive variance)
            favorable = variance >= 0
            
            account_type = str(budget.account.account_type.value)
            
            line = {
                "account_name": budget.account.name,
                "account_type": account_type,
                "budget_name": budget.name or budget.account.name,
                "budgeted": budget.amount,
                "actual": actual,
                "variance": variance,
                "variance_pct": variance_pct,
                "favorable": favorable,
            }
            self.budget_lines.append(line)
            
            # Update type summaries
            if account_type not in type_summaries:
                type_summaries[account_type] = {
                    "budgeted": Decimal("0"),
                    "actual": Decimal("0"),
                    "variance": Decimal("0"),
                }
            
            type_summaries[account_type]["budgeted"] += budget.amount
            type_summaries[account_type]["actual"] += actual
            type_summaries[account_type]["variance"] += variance
        
        self.summaries = type_summaries
        
        # Sort budget lines by account type then name
        self.budget_lines.sort(key=lambda x: (x["account_type"], x["account_name"]))
    
    @property
    def total_budgeted(self) -> Decimal:
        """Total budgeted amount across all accounts."""
        return sum(s["budgeted"] for s in self.summaries.values())
    
    @property
    def total_actual(self) -> Decimal:
        """Total actual amount across all accounts."""
        return sum(s["actual"] for s in self.summaries.values())
    
    @property
    def total_variance(self) -> Decimal:
        """Total variance across all accounts."""
        return sum(s["variance"] for s in self.summaries.values())
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the report to a dictionary.
        
        Returns:
            Dictionary representation of the report.
        """
        return {
            "entity": self.session.entity.name,
            "title": self.title,
            "reporting_period": {
                "id": self.reporting_period.id,
                "start": self.reporting_period.period_start.isoformat(),
                "end": self.reporting_period.period_end.isoformat(),
            },
            "generated_at": self.generated_at.isoformat(),
            "budget_lines": [
                {k: float(v) if isinstance(v, Decimal) else v for k, v in line.items()}
                for line in self.budget_lines
            ],
            "summaries": {
                k: {kk: float(vv) for kk, vv in v.items()}
                for k, v in self.summaries.items()
            },
            "totals": {
                "budgeted": float(self.total_budgeted),
                "actual": float(self.total_actual),
                "variance": float(self.total_variance),
            },
        }
    
    def __str__(self) -> str:
        """Generate string representation of the report."""
        lines = []
        
        # Title
        lines.append(self.session.entity.name.center(self.width))
        lines.append(self.title.center(self.width))
        period = (
            f"Period: {self.reporting_period.period_start.strftime('%d %b %Y')} "
            f"to {self.reporting_period.period_end.strftime('%d %b %Y')}"
        )
        lines.append(period.center(self.width))
        lines.append("")
        
        # Header
        header = f"{'Account':<30}{'Budget':>12}{'Actual':>12}{'Variance':>12}{'Var %':>8}{'':>6}"
        lines.append(header)
        lines.append("-" * self.width)
        
        # Group by account type
        current_type = None
        
        for line in self.budget_lines:
            if line["account_type"] != current_type:
                if current_type is not None:
                    lines.append("")
                current_type = line["account_type"]
                lines.append(f"[{current_type}]")
            
            indicator = "✓" if line["favorable"] else "✗"
            row = (
                f"  {line['account_name']:<28}"
                f"{line['budgeted']:>12.2f}"
                f"{line['actual']:>12.2f}"
                f"{line['variance']:>12.2f}"
                f"{line['variance_pct']:>7.1f}%"
                f"  {indicator}"
            )
            lines.append(row)
        
        # Totals
        lines.append("")
        lines.append("=" * self.width)
        lines.append(
            f"{'TOTAL':<30}"
            f"{self.total_budgeted:>12.2f}"
            f"{self.total_actual:>12.2f}"
            f"{self.total_variance:>12.2f}"
        )
        lines.append("=" * self.width)
        
        # Legend
        lines.append("")
        lines.append("✓ = Favorable variance | ✗ = Unfavorable variance")
        
        return "\n".join(lines)
