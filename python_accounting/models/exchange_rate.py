# models/exchange_rate.py
# Copyright (C) 2024 - 2028 the PythonAccounting authors and contributors
# <see AUTHORS file>
#
# This module is part of PythonAccounting and is released under
# the MIT License: https://www.opensource.org/licenses/mit-license.php

"""
Represents an exchange rate between two currencies for multi-currency support.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Numeric, DateTime, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from python_accounting.models.recyclable import Recyclable

if TYPE_CHECKING:
    from sqlalchemy.orm import Session
    from python_accounting.models import Currency


class ExchangeRate(Recyclable):
    """
    Represents an exchange rate between two currencies at a specific date.
    
    Attributes:
        from_currency_id: The source currency ID.
        to_currency_id: The target currency ID.
        rate: The exchange rate (1 from_currency = rate * to_currency).
        effective_date: The date from which this rate is effective.
    """
    
    __tablename__ = "exchange_rate"

    from_currency_id: Mapped[int] = mapped_column(ForeignKey("currency.id"), nullable=False)
    to_currency_id: Mapped[int] = mapped_column(ForeignKey("currency.id"), nullable=False)
    rate: Mapped[Decimal] = mapped_column(Numeric(precision=18, scale=8), nullable=False)
    effective_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # Relationships
    from_currency: Mapped["Currency"] = relationship(
        "Currency", foreign_keys=[from_currency_id], lazy="joined"
    )
    to_currency: Mapped["Currency"] = relationship(
        "Currency", foreign_keys=[to_currency_id], lazy="joined"
    )
    
    def __repr__(self) -> str:
        return f"{self.from_currency.code}/{self.to_currency.code}: {self.rate}"
    
    @classmethod
    def get_rate(
        cls,
        session: "Session",
        from_currency_id: int,
        to_currency_id: int,
        as_of_date: Optional[datetime] = None,
    ) -> Optional[Decimal]:
        """
        Get the exchange rate between two currencies as of a specific date.
        
        Args:
            session: The database session.
            from_currency_id: The source currency ID.
            to_currency_id: The target currency ID.
            as_of_date: The date for which to get the rate. Defaults to today.
            
        Returns:
            The exchange rate, or None if not found.
        """
        if from_currency_id == to_currency_id:
            return Decimal("1.0")
            
        if as_of_date is None:
            as_of_date = datetime.now()
            
        stmt = (
            select(cls)
            .where(
                cls.from_currency_id == from_currency_id,
                cls.to_currency_id == to_currency_id,
                cls.effective_date <= as_of_date,
                cls.entity_id == session.entity.id,
                cls.deleted == False,  # noqa: E712
            )
            .order_by(cls.effective_date.desc())
            .limit(1)
        )
        
        result = session.execute(stmt).scalar_one_or_none()
        return result.rate if result else None
    
    @classmethod
    def convert(
        cls,
        session: "Session",
        amount: Decimal,
        from_currency_id: int,
        to_currency_id: int,
        as_of_date: Optional[datetime] = None,
    ) -> Optional[Decimal]:
        """
        Convert an amount from one currency to another.
        
        Args:
            session: The database session.
            amount: The amount to convert.
            from_currency_id: The source currency ID.
            to_currency_id: The target currency ID.
            as_of_date: The date for the conversion rate.
            
        Returns:
            The converted amount, or None if no rate is available.
        """
        rate = cls.get_rate(session, from_currency_id, to_currency_id, as_of_date)
        if rate is None:
            # Try reverse rate
            reverse_rate = cls.get_rate(session, to_currency_id, from_currency_id, as_of_date)
            if reverse_rate is None:
                return None
            rate = Decimal("1.0") / reverse_rate
            
        return amount * rate
