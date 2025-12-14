"""Full license command implementation (experimental)"""

import click
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

from app.core import BlackLightAPI

console = Console()


@click.command()
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