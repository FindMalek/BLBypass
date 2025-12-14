"""Main CLI interface for BLBypass"""

import warnings
# Suppress urllib3 SSL warnings (common on macOS with LibreSSL)
warnings.filterwarnings('ignore', category=UserWarning, module='urllib3')
warnings.filterwarnings('ignore', message='.*urllib3.*')
warnings.filterwarnings('ignore', message='.*NotOpenSSLWarning.*')

import click
import logging
from rich.console import Console

from app.commands.generate import generate
from app.commands.batch import batch
from app.commands.full import full

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


# Register commands
main.add_command(generate)
main.add_command(batch)
main.add_command(full)


if __name__ == '__main__':
    main()