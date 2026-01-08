# cli/__init__.py
# Copyright (C) 2024 - 2028 the PythonAccounting authors and contributors
# <see AUTHORS file>
#
# This module is part of PythonAccounting and is released under
# the MIT License: https://www.opensource.org/licenses/mit-license.php

"""
Command-line interface for Python Accounting.

Provides commands for database initialization, report generation, and common
accounting operations.
"""

from __future__ import annotations

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
from pathlib import Path

console = Console()


@click.group()
@click.version_option(version="2.0.0", prog_name="python-accounting")
def main():
    """Python Accounting CLI - Double Entry Bookkeeping made easy."""
    pass


@main.command()
@click.option(
    "--database-url", "-d",
    default="sqlite:///accounting.db",
    help="Database connection URL"
)
@click.option("--echo/--no-echo", default=False, help="Echo SQL statements")
def init(database_url: str, echo: bool):
    """Initialize a new accounting database."""
    from sqlalchemy import create_engine
    from python_accounting.models import Base
    
    with console.status("[bold green]Initializing database..."):
        try:
            engine = create_engine(database_url, echo=echo)
            Base.metadata.create_all(engine)
            console.print("[bold green]✓[/] Database initialized successfully!")
            console.print(f"  Database URL: {database_url}")
        except Exception as e:
            console.print(f"[bold red]✗[/] Error: {e}")
            raise click.Abort()


@main.group()
def entity():
    """Manage entities (companies)."""
    pass


@entity.command("create")
@click.argument("name")
@click.option("--currency", "-c", required=True, help="Default currency code (e.g., USD)")
@click.option("--currency-name", default=None, help="Currency name (e.g., US Dollars)")
@click.option("--database-url", "-d", default="sqlite:///accounting.db")
def entity_create(name: str, currency: str, currency_name: str, database_url: str):
    """Create a new entity with its default currency."""
    from sqlalchemy import create_engine
    from python_accounting.models import Entity, Currency, Base
    from python_accounting.database.session import get_session
    
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    
    with get_session(engine) as session:
        try:
            entity = Entity(name=name)
            session.add(entity)
            session.commit()
            
            currency_obj = Currency(
                name=currency_name or currency,
                code=currency.upper(),
                entity_id=entity.id
            )
            session.add(currency_obj)
            session.commit()
            
            console.print(f"[bold green]✓[/] Created entity: {name}")
            console.print(f"  Entity ID: {entity.id}")
            console.print(f"  Currency: {currency.upper()}")
        except Exception as e:
            console.print(f"[bold red]✗[/] Error: {e}")
            raise click.Abort()


@entity.command("list")
@click.option("--database-url", "-d", default="sqlite:///accounting.db")
def entity_list(database_url: str):
    """List all entities."""
    from sqlalchemy import create_engine, select
    from python_accounting.models import Entity, Base
    from python_accounting.database.session import get_session
    
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    
    with get_session(engine) as session:
        stmt = select(Entity).where(Entity.deleted == False)  # noqa: E712
        entities = session.execute(stmt).scalars().all()
        
        if not entities:
            console.print("[yellow]No entities found.[/]")
            return
        
        table = Table(title="Entities")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Created", style="blue")
        
        for e in entities:
            table.add_row(
                str(e.id),
                e.name,
                str(e.created_at) if hasattr(e, "created_at") else "N/A"
            )
        
        console.print(table)


@main.group()
def account():
    """Manage accounts."""
    pass


@account.command("list")
@click.option("--entity-id", "-e", required=True, type=int, help="Entity ID")
@click.option("--database-url", "-d", default="sqlite:///accounting.db")
def account_list(entity_id: int, database_url: str):
    """List all accounts for an entity."""
    from sqlalchemy import create_engine, select
    from python_accounting.models import Account, Entity, Base
    from python_accounting.database.session import get_session
    
    engine = create_engine(database_url)
    
    with get_session(engine) as session:
        # Set entity context
        entity = session.get(Entity, entity_id)
        if not entity:
            console.print(f"[bold red]✗[/] Entity {entity_id} not found")
            raise click.Abort()
        
        stmt = select(Account).where(
            Account.entity_id == entity_id,
            Account.deleted == False  # noqa: E712
        ).order_by(Account.account_type, Account.name)
        
        accounts = session.execute(stmt).scalars().all()
        
        if not accounts:
            console.print("[yellow]No accounts found.[/]")
            return
        
        table = Table(title=f"Accounts for {entity.name}")
        table.add_column("ID", style="cyan")
        table.add_column("Code", style="yellow")
        table.add_column("Name", style="green")
        table.add_column("Type", style="blue")
        
        for acc in accounts:
            table.add_row(
                str(acc.id),
                acc.code or "-",
                acc.name,
                str(acc.account_type.value) if hasattr(acc.account_type, "value") else str(acc.account_type)
            )
        
        console.print(table)


@main.group()
def report():
    """Generate financial reports."""
    pass


@report.command("income-statement")
@click.option("--entity-id", "-e", required=True, type=int, help="Entity ID")
@click.option("--database-url", "-d", default="sqlite:///accounting.db")
@click.option("--export", "-x", type=click.Choice(["csv", "json", "excel", "pdf"]), help="Export format")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
def income_statement(entity_id: int, database_url: str, export: str, output: str):
    """Generate an Income Statement (Profit & Loss)."""
    from sqlalchemy import create_engine
    from python_accounting.models import Entity, Base
    from python_accounting.reports import IncomeStatement
    from python_accounting.database.session import get_session
    
    engine = create_engine(database_url)
    
    with get_session(engine) as session:
        entity = session.get(Entity, entity_id)
        if not entity:
            console.print(f"[bold red]✗[/] Entity {entity_id} not found")
            raise click.Abort()
        
        session.entity = entity
        
        try:
            report = IncomeStatement(session)
            
            if export and output:
                from python_accounting.exporters import export_report
                filepath = export_report(report, output, export)
                console.print(f"[bold green]✓[/] Report exported to: {filepath}")
            else:
                console.print(Panel(str(report), title="Income Statement"))
        except Exception as e:
            console.print(f"[bold red]✗[/] Error generating report: {e}")
            raise click.Abort()


@report.command("balance-sheet")
@click.option("--entity-id", "-e", required=True, type=int, help="Entity ID")
@click.option("--database-url", "-d", default="sqlite:///accounting.db")
@click.option("--export", "-x", type=click.Choice(["csv", "json", "excel", "pdf"]), help="Export format")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
def balance_sheet(entity_id: int, database_url: str, export: str, output: str):
    """Generate a Balance Sheet."""
    from sqlalchemy import create_engine
    from python_accounting.models import Entity, Base
    from python_accounting.reports import BalanceSheet
    from python_accounting.database.session import get_session
    
    engine = create_engine(database_url)
    
    with get_session(engine) as session:
        entity = session.get(Entity, entity_id)
        if not entity:
            console.print(f"[bold red]✗[/] Entity {entity_id} not found")
            raise click.Abort()
        
        session.entity = entity
        
        try:
            report = BalanceSheet(session)
            
            if export and output:
                from python_accounting.exporters import export_report
                filepath = export_report(report, output, export)
                console.print(f"[bold green]✓[/] Report exported to: {filepath}")
            else:
                console.print(Panel(str(report), title="Balance Sheet"))
        except Exception as e:
            console.print(f"[bold red]✗[/] Error generating report: {e}")
            raise click.Abort()


@report.command("cashflow")
@click.option("--entity-id", "-e", required=True, type=int, help="Entity ID")
@click.option("--database-url", "-d", default="sqlite:///accounting.db")
@click.option("--export", "-x", type=click.Choice(["csv", "json", "excel", "pdf"]), help="Export format")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
def cashflow_statement(entity_id: int, database_url: str, export: str, output: str):
    """Generate a Cashflow Statement."""
    from sqlalchemy import create_engine
    from python_accounting.models import Entity, Base
    from python_accounting.reports import CashflowStatement
    from python_accounting.database.session import get_session
    
    engine = create_engine(database_url)
    
    with get_session(engine) as session:
        entity = session.get(Entity, entity_id)
        if not entity:
            console.print(f"[bold red]✗[/] Entity {entity_id} not found")
            raise click.Abort()
        
        session.entity = entity
        
        try:
            report = CashflowStatement(session)
            
            if export and output:
                from python_accounting.exporters import export_report
                filepath = export_report(report, output, export)
                console.print(f"[bold green]✓[/] Report exported to: {filepath}")
            else:
                console.print(Panel(str(report), title="Cashflow Statement"))
        except Exception as e:
            console.print(f"[bold red]✗[/] Error generating report: {e}")
            raise click.Abort()


@main.command()
def interactive():
    """Start an interactive accounting shell."""
    rprint("[bold blue]Python Accounting Interactive Shell[/]")
    rprint("Type 'help' for available commands, 'exit' to quit.\n")
    
    from prompt_toolkit import prompt
    from prompt_toolkit.history import InMemoryHistory
    
    history = InMemoryHistory()
    
    while True:
        try:
            user_input = prompt("pyaccount> ", history=history)
            
            if user_input.lower() in ("exit", "quit", "q"):
                rprint("[yellow]Goodbye![/]")
                break
            elif user_input.lower() == "help":
                rprint("""
[bold]Available Commands:[/]
  help          - Show this help
  exit/quit     - Exit the shell
  
[bold]To use CLI commands, run:[/]
  pyaccount --help
                """)
            else:
                rprint(f"[yellow]Unknown command: {user_input}[/]")
        except KeyboardInterrupt:
            continue
        except EOFError:
            break


if __name__ == "__main__":
    main()
