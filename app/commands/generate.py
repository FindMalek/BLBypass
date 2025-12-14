"""Generate command implementation"""

import click
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

from app.core import BlackLightAPI, parse_license_data
from app.utils import (
    copy_to_clipboard,
    copy_step_by_step,
    display_license_table,
    generate_license_string,
    save_to_file,
    generate_fake_name,
    generate_fake_email,
)

console = Console()


@click.command()
@click.option('--name', '-n', help='Name for the license')
@click.option('--email', '-e', help='Email address for the license')
@click.option('--lang', '-l', default='en', help='Language code (default: en)')
@click.option('--copy', '-c', is_flag=True, help='Copy license code to clipboard')
@click.option('--output', '-o', help='Save license to file (JSON format)')
@click.option('--quiet', '-q', is_flag=True, help='Minimal output')
@click.option('--auto', is_flag=True, help='Auto-generate fake name/email and copy step-by-step')
@click.option('--delay', '-d', default=2.0, type=float, help='Delay between requests in seconds (default: 2.0)')
@click.option('--retries', '-r', default=3, type=int, help='Number of retry attempts (default: 3)')
@click.option('--retry-delay', default=5.0, type=float, help='Delay between retries in seconds (default: 5.0)')
@click.option('--proxy', help='Proxy URL (e.g., http://proxy:port)')
@click.option('--auto-proxy', is_flag=True, help='Automatically fetch and use proxies')
@click.option('--delay', '-d', default=5.0, type=float, help='Delay between requests in seconds (default: 5.0, recommended: 10+ for safety)')
@click.option('--proxy-source', default='proxyscrape', type=click.Choice(['proxyscrape', 'pubproxy']), 
              help='Proxy source for auto-proxy (default: proxyscrape)')
@click.pass_context
def generate(ctx, name: Optional[str], email: Optional[str], lang: str, copy: bool, 
             output: Optional[str], quiet: bool, auto: bool, delay: float, retries: int,
             retry_delay: float, proxy: Optional[str], auto_proxy: bool, proxy_source: str):
    """Generate a trial license for BlackLight 3"""
    
    debug = ctx.obj.get('debug', False)
    
    # Auto mode: generate fake data
    if auto:
        name = generate_fake_name()
        email = generate_fake_email(name)
        console.print(Panel.fit(
            f"[bold cyan]BLBypass[/bold cyan] - Auto Mode\n\n"
            f"[dim]Generated Name:[/dim] {name}\n"
            f"[dim]Generated Email:[/dim] {email}",
            border_style="cyan"
        ))
        console.print()
    
    # Interactive prompts if not provided and not auto mode
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
    
    # Request license with retry logic
    api = BlackLightAPI(
        lang=lang, 
        debug=debug, 
        delay=delay,
        retry_attempts=retries,
        retry_delay=retry_delay,
        proxy=proxy,
        auto_proxy=auto_proxy,
        proxy_source=proxy_source
    )
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
    
    # Auto mode: step-by-step clipboard copy
    if auto:
        copy_step_by_step(license_data, auto_mode=True)
    # Regular copy mode
    elif copy:
        license_string = generate_license_string(license_data)
        if copy_to_clipboard(license_string):
            console.print("[green]✓[/green] Copied to clipboard")
    
    # Save to file
    if output:
        save_to_file([license_data], output, format="json")
    
    # Success message
    if not quiet:
        if auto:
            console.print(Panel(
                f"[green]✓ License generated successfully![/green]\n\n"
                f"All information has been copied to your clipboard step by step.\n"
                f"Simply paste each field into BlackLight 3 as prompted.",
                title="Success",
                border_style="green"
            ))
        else:
            console.print(Panel(
                f"[green]✓ License generated successfully![/green]\n\n"
                f"Use this information to activate BlackLight 3:\n"
                f"• Name: {license_data.get('name', 'N/A')}\n"
                f"• Email: {license_data.get('email', 'N/A')}\n"
                f"• License Code: [bold]{license_data.get('license_code', 'N/A')}[/bold]",
                title="Success",
                border_style="green"
            ))