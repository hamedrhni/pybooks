# events/__init__.py
# Copyright (C) 2024 - 2028 the PythonAccounting authors and contributors
# <see AUTHORS file>
#
# This module is part of PythonAccounting and is released under
# the MIT License: https://www.opensource.org/licenses/mit-license.php

"""
Event system for accounting hooks and callbacks.

This module provides an event system that allows external code to hook into
accounting operations like transaction posting, balance changes, and period closures.

Usage:
    from python_accounting.events import EventManager, EventType
    
    def on_transaction_posted(event_data):
        print(f"Transaction {event_data['transaction_id']} was posted")
    
    EventManager.subscribe(EventType.TRANSACTION_POSTED, on_transaction_posted)
"""

from __future__ import annotations

from enum import Enum
from typing import Callable, Dict, List, Any
from dataclasses import dataclass, field
from datetime import datetime


class EventType(Enum):
    """Types of events that can be subscribed to."""
    
    # Transaction events
    TRANSACTION_CREATED = "transaction.created"
    TRANSACTION_POSTED = "transaction.posted"
    TRANSACTION_DELETED = "transaction.deleted"
    
    # Balance events
    BALANCE_CHANGED = "balance.changed"
    BALANCE_OPENED = "balance.opened"
    
    # Period events
    PERIOD_OPENED = "period.opened"
    PERIOD_CLOSED = "period.closed"
    
    # Account events
    ACCOUNT_CREATED = "account.created"
    ACCOUNT_UPDATED = "account.updated"
    ACCOUNT_DELETED = "account.deleted"
    
    # Assignment events
    ASSIGNMENT_CREATED = "assignment.created"
    ASSIGNMENT_DELETED = "assignment.deleted"
    
    # Report events
    REPORT_GENERATED = "report.generated"


@dataclass
class Event:
    """Represents an event that occurred in the accounting system."""
    
    event_type: EventType
    timestamp: datetime
    entity_id: int
    data: Dict[str, Any] = field(default_factory=dict)
    
    def __repr__(self) -> str:
        return f"Event({self.event_type.value} at {self.timestamp})"


class EventManager:
    """
    Manages event subscriptions and dispatching.
    
    This is a singleton-style manager that handles all event subscriptions
    across the application.
    """
    
    _subscribers: Dict[EventType, List[Callable[[Event], None]]] = {}
    _enabled: bool = True
    _event_history: List[Event] = []
    _max_history: int = 1000
    
    @classmethod
    def subscribe(
        cls,
        event_type: EventType,
        callback: Callable[[Event], None],
    ) -> None:
        """
        Subscribe to an event type.
        
        Args:
            event_type: The type of event to subscribe to.
            callback: Function to call when the event occurs.
        """
        if event_type not in cls._subscribers:
            cls._subscribers[event_type] = []
        cls._subscribers[event_type].append(callback)
    
    @classmethod
    def unsubscribe(
        cls,
        event_type: EventType,
        callback: Callable[[Event], None],
    ) -> bool:
        """
        Unsubscribe from an event type.
        
        Args:
            event_type: The type of event to unsubscribe from.
            callback: The callback function to remove.
            
        Returns:
            True if the callback was found and removed, False otherwise.
        """
        if event_type in cls._subscribers:
            try:
                cls._subscribers[event_type].remove(callback)
                return True
            except ValueError:
                pass
        return False
    
    @classmethod
    def emit(
        cls,
        event_type: EventType,
        entity_id: int,
        data: Dict[str, Any] = None,
    ) -> Event:
        """
        Emit an event to all subscribers.
        
        Args:
            event_type: The type of event to emit.
            entity_id: The entity ID associated with this event.
            data: Additional data to include with the event.
            
        Returns:
            The Event object that was emitted.
        """
        event = Event(
            event_type=event_type,
            timestamp=datetime.now(),
            entity_id=entity_id,
            data=data or {},
        )
        
        # Store in history
        cls._event_history.append(event)
        if len(cls._event_history) > cls._max_history:
            cls._event_history.pop(0)
        
        # Notify subscribers if enabled
        if cls._enabled and event_type in cls._subscribers:
            for callback in cls._subscribers[event_type]:
                try:
                    callback(event)
                except Exception as e:
                    # Log error but don't stop other callbacks
                    print(f"Error in event callback: {e}")
        
        return event
    
    @classmethod
    def enable(cls) -> None:
        """Enable event dispatching."""
        cls._enabled = True
    
    @classmethod
    def disable(cls) -> None:
        """Disable event dispatching (events are still recorded)."""
        cls._enabled = False
    
    @classmethod
    def is_enabled(cls) -> bool:
        """Check if event dispatching is enabled."""
        return cls._enabled
    
    @classmethod
    def get_history(
        cls,
        event_type: EventType = None,
        limit: int = 100,
    ) -> List[Event]:
        """
        Get recent event history.
        
        Args:
            event_type: Optional filter by event type.
            limit: Maximum number of events to return.
            
        Returns:
            List of recent events.
        """
        events = cls._event_history
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        return events[-limit:]
    
    @classmethod
    def clear_history(cls) -> None:
        """Clear the event history."""
        cls._event_history.clear()
    
    @classmethod
    def clear_subscribers(cls) -> None:
        """Clear all subscribers (useful for testing)."""
        cls._subscribers.clear()


# Convenience function for emitting events
def emit_event(
    event_type: EventType,
    entity_id: int,
    **data: Any,
) -> Event:
    """
    Convenience function to emit an event.
    
    Args:
        event_type: The type of event to emit.
        entity_id: The entity ID associated with this event.
        **data: Keyword arguments to include as event data.
        
        Returns:
        The Event object that was emitted.
    """
    return EventManager.emit(event_type, entity_id, data)
