"""CLI commands"""

from app.commands.generate import generate
from app.commands.batch import batch
from app.commands.full import full

__all__ = ['generate', 'batch', 'full']