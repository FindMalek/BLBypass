"""Utility functions for clipboard, formatting, and file operations"""

import json
import pyperclip
from typing import Dict, Optional, List
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


def copy_to_clipboard(text: str) -> bool:
    """
    Copy text to system clipboard
    
    Args:
        text: Text to copy
        
    Returns:
        True if successful, False otherwise
    """
    try:
        pyperclip.copy(text)
        return True
    except Exception as e:
        console.print(f"[yellow]Warning:[/yellow] Could not copy to clipboard: {str(e)}")
        return False


def format_license_output(license_data: Dict) -> str:
    """
    Format license data as a readable string
    
    Args:
        license_data: Dictionary with license information
        
    Returns:
        Formatted string
    """
    lines = []
    lines.append("=" * 50)
    lines.append("BlackLight 3 License")
    lines.append("=" * 50)
    
    if license_data.get("name"):
        lines.append(f"Name: {license_data['name']}")
    if license_data.get("email"):
        lines.append(f"Email: {license_data['email']}")
    if license_data.get("license_code"):
        lines.append(f"License Code: {license_data['license_code']}")
    if license_data.get("expiry_date"):
        lines.append(f"Expires: {license_data['expiry_date']}")
    
    lines.append("=" * 50)
    return "\n".join(lines)


def display_license_table(license_data: Dict):
    """
    Display license information in a formatted table
    
    Args:
        license_data: Dictionary with license information
    """
    table = Table(title="BlackLight 3 License", show_header=True, header_style="bold magenta")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="green")
    
    if license_data.get("name"):
        table.add_row("Name", license_data["name"])
    if license_data.get("email"):
        table.add_row("Email", license_data["email"])
    if license_data.get("license_code"):
        table.add_row("License Code", f"[bold]{license_data['license_code']}[/bold]")
    if license_data.get("expiry_date"):
        table.add_row("Expires", str(license_data["expiry_date"]))
    
    console.print(table)


def save_to_file(licenses: List[Dict], filepath: str, format: str = "json"):
    """
    Save licenses to a file
    
    Args:
        licenses: List of license dictionaries
        filepath: Path to save file
        format: File format ('json' or 'csv')
    """
    path = Path(filepath)
    
    try:
        if format.lower() == "json":
            with open(path, 'w') as f:
                json.dump(licenses, f, indent=2, default=str)
            console.print(f"[green]✓[/green] Saved {len(licenses)} license(s) to {filepath}")
        elif format.lower() == "csv":
            import csv
            if not licenses:
                return
            
            with open(path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=licenses[0].keys())
                writer.writeheader()
                writer.writerows(licenses)
            console.print(f"[green]✓[/green] Saved {len(licenses)} license(s) to {filepath}")
        else:
            console.print(f"[red]Error:[/red] Unsupported format: {format}")
    except Exception as e:
        console.print(f"[red]Error saving file:[/red] {str(e)}")


def generate_license_string(license_data: Dict) -> str:
    """
    Generate a single-line license string for easy copying
    
    Args:
        license_data: Dictionary with license information
        
    Returns:
        Formatted string with name, email, and license code
    """
    parts = []
    if license_data.get("name"):
        parts.append(license_data["name"])
    if license_data.get("email"):
        parts.append(license_data["email"])
    if license_data.get("license_code"):
        parts.append(license_data["license_code"])
    
    return " | ".join(parts)