"""Clipboard operations"""

import pyperclip
from rich.console import Console

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


def copy_step_by_step(license_data: dict, auto_mode: bool = False):
    """
    Copy license information to clipboard step by step with prompts
    
    Args:
        license_data: Dictionary with license information
        auto_mode: If True, auto-advance through steps
    """
    import time
    
    name = license_data.get("name", "")
    email = license_data.get("email", "")
    license_code = license_data.get("license_code", "")
    
    if not all([name, email, license_code]):
        console.print("[red]Error:[/red] Missing license data")
        return
    
    steps = [
        ("Name", name, "Copy the name to the clipboard"),
        ("Email", email, "Copy the email to the clipboard"),
        ("License Code", license_code, "Copy the license code to the clipboard"),
    ]
    
    console.print("\n[bold cyan]Step-by-step clipboard copy:[/bold cyan]\n")
    
    for step_num, (field_name, value, instruction) in enumerate(steps, 1):
        console.print(f"[cyan]Step {step_num}/3:[/cyan] {instruction}")
        console.print(f"[dim]Value:[/dim] [bold]{value}[/bold]\n")
        
        if copy_to_clipboard(value):
            console.print(f"[green]✓[/green] {field_name} copied to clipboard!")
        else:
            console.print(f"[yellow]⚠[/yellow] Could not copy {field_name} automatically")
            console.print(f"[dim]Please copy manually:[/dim] {value}")
        
        if step_num < len(steps):
            if auto_mode:
                time.sleep(1)  # Brief pause between steps
            else:
                input("\n[dim]Press Enter to continue to next step...[/dim]")
            console.print()
    
    console.print("[green]✓[/green] All steps completed!\n")