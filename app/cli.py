"""Main CLI interface for BLBypass"""

import warnings
# Suppress urllib3 SSL warnings (common on macOS with LibreSSL)
# Must be done before any urllib3/requests imports
warnings.filterwarnings('ignore', category=UserWarning, module='urllib3')
warnings.filterwarnings('ignore', message='.*urllib3.*')
warnings.filterwarnings('ignore', message='.*NotOpenSSLWarning.*')

import click
import logging
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

from app.api import BlackLightAPI
from app.parser import parse_license_data
from app.utils import (
    copy_to_clipboard,
    display_license_table,
    save_to_file,
    generate_license_string
)

console = Console()


@click.group()
@click.version_option(version="0.1.0")
@click.option('--debug', is_flag=True, help='Enable debug logging')
@click.pass_context
def main(ctx, debug):
    """BLBypass - BlackLight 3 License Bypass Tool"""
    ctx.ensure_object(dict)
    ctx.obj['debug'] = debug
    
    if debug:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console.print("[yellow]Debug mode enabled[/yellow]")


@main.command()
@click.option('--name', '-n', help='Name for the license')
@click.option('--email', '-e', help='Email address for the license')
@click.option('--lang', '-l', default='en', help='Language code (default: en)')
@click.option('--copy', '-c', is_flag=True, help='Copy license code to clipboard')
@click.option('--output', '-o', help='Save license to file (JSON format)')
@click.option('--quiet', '-q', is_flag=True, help='Minimal output')
@click.pass_context
def generate(ctx, name: Optional[str], email: Optional[str], lang: str, copy: bool, output: Optional[str], quiet: bool):
    """Generate a trial license for BlackLight 3"""
    
    debug = ctx.obj.get('debug', False)
    
    # Interactive prompts if not provided
    if not name:
        name = Prompt.ask("Enter name")
    if not email:
        email = Prompt.ask("Enter email")
    
    # Validate inputs
    if not name or not email:
        console.print("[red]Error:[/red] Name and email are required")
        return
    
    if '@' not in email:
        console.print("[yellow]Warning:[/yellow] Email format looks invalid")
        if not Confirm.ask("Continue anyway?"):
            return
    
    # Show banner
    if not quiet:
        console.print(Panel.fit(
            "[bold cyan]BLBypass[/bold cyan] - Generating trial license...",
            border_style="cyan"
        ))
    
    # Request license
    api = BlackLightAPI(lang=lang, debug=debug)
    response = api.request_trial_license(name, email)
    
    if not response:
        console.print("[red]✗ Failed to generate license[/red]")
        if debug:
            console.print("[dim]DEBUG:[/dim] No response received from API")
        return
    
    # Parse license data
    license_data = parse_license_data(response.get("message", ""))
    
    if debug:
        console.print(f"[dim]DEBUG:[/dim] Parsed license data: {license_data}")
    
    if not license_data.get("license_code"):
        console.print("[red]✗ Could not extract license code from response[/red]")
        if not quiet or debug:
            console.print(f"[dim]Response: {response.get('message', '')[:500]}...[/dim]")
        return
    
    # Display results
    if not quiet:
        display_license_table(license_data)
        console.print()
    
    # Copy to clipboard
    if copy:
        license_string = generate_license_string(license_data)
        if copy_to_clipboard(license_string):
            console.print("[green]✓[/green] Copied to clipboard")
    
    # Save to file
    if output:
        save_to_file([license_data], output, format="json")
    
    # Success message
    if not quiet:
        console.print(Panel(
            f"[green]✓ License generated successfully![/green]\n\n"
            f"Use this information to activate BlackLight 3:\n"
            f"• Name: {license_data.get('name', 'N/A')}\n"
            f"• Email: {license_data.get('email', 'N/A')}\n"
            f"• License Code: [bold]{license_data.get('license_code', 'N/A')}[/bold]",
            title="Success",
            border_style="green"
        ))


@main.command()
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


@main.command()
@click.option('--name', '-n', required=True, help='Name for the license')
@click.option('--email', '-e', required=True, help='Email address')
@click.option('--pi', help='Payment Intent ID (experimental)')
@click.option('--pics', help='Payment Intent Client Secret (experimental)')
@click.option('--ps', help='Payment Session ID (experimental)')
@click.pass_context
def full(ctx, name: str, email: str, pi: Optional[str], pics: Optional[str], ps: Optional[str]):
    """Attempt to generate a full license (EXPERIMENTAL/RESEARCH ONLY)"""
    
    debug = ctx.obj.get('debug', False)
    
    console.print(Panel(
        "[yellow]⚠ WARNING: EXPERIMENTAL FEATURE[/yellow]\n\n"
        "This command attempts to interact with the full license endpoint.\n"
        "It requires valid Stripe payment intents and may not work without\n"
        "actual payment processing. Use for research purposes only.",
        title="Experimental",
        border_style="yellow"
    ))
    
    if not Confirm.ask("\nContinue?"):
        return
    
    api = BlackLightAPI(debug=debug)
    response = api.request_full_license(
        name=name,
        email=email,
        payment_intent_id=pi,
        payment_secret=pics,
        payment_session=ps
    )
    
    if response:
        console.print("[green]Response received:[/green]")
        console.print_json(str(response))
    else:
        console.print("[red]Request failed[/red]")


if __name__ == '__main__':
    main()