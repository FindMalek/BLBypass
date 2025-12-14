"""File operations"""

import json
import csv
from typing import List, Dict
from pathlib import Path
from rich.console import Console

console = Console()


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