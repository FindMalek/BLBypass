"""Batch command implementation"""

import click
from rich.console import Console
from rich.prompt import Prompt

from app.core import BlackLightAPI, parse_license_data
from app.utils import save_to_file

console = Console()


@click.command()
@click.option('--count', '-c', default=1, help='Number of licenses to generate')
@click.option('--lang', '-l', default='en', help='Language code')
@click.option('--output', '-o', required=True, help='Output file path')
@click.option('--format', '-f', default='json', type=click.Choice(['json', 'csv']), help='Output format')
@click.pass_context
def batch(ctx, count: int, lang: str, output: str, format: str):
    """Generate multiple licenses in batch mode"""
    
    debug = ctx.obj.get('debug', False)
    
    console.print(f"[cyan]Generating {count} license(s)...[/cyan]\n")
    
    licenses = []
    api = BlackLightAPI(lang=lang, debug=debug)
    
    for i in range(count):
        console.print(f"[dim]Generating license {i+1}/{count}...[/dim]")
        
        name = Prompt.ask(f"  Name [{i+1}]")
        email = Prompt.ask(f"  Email [{i+1}]")
        
        response = api.request_trial_license(name, email)
        if response:
            license_data = parse_license_data(response.get("message", ""))
            if license_data.get("license_code"):
                licenses.append(license_data)
                console.print(f"  [green]✓[/green] Generated")
            else:
                console.print(f"  [red]✗[/red] Failed to parse")
        else:
            console.print(f"  [red]✗[/red] Request failed")
        
        console.print()
    
    if licenses:
        save_to_file(licenses, output, format=format)
        console.print(f"[green]✓[/green] Generated {len(licenses)}/{count} license(s)")
    else:
        console.print("[red]✗ No licenses were generated[/red]")