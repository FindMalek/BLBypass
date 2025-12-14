"""Display and formatting utilities"""

from typing import Dict
from rich.console import Console
from rich.table import Table

console = Console()


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