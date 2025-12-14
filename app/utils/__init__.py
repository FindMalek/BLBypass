"""Utility functions"""

from app.utils.clipboard import copy_to_clipboard, copy_step_by_step
from app.utils.display import display_license_table, format_license_output, generate_license_string
from app.utils.file_ops import save_to_file
from app.utils.fake_data import generate_fake_name, generate_fake_email

__all__ = [
    'copy_to_clipboard',
    'copy_step_by_step',
    'display_license_table',
    'format_license_output',
    'generate_license_string',
    'save_to_file',
    'generate_fake_name',
    'generate_fake_email',
]