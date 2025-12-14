"""HTML parsing utilities for extracting license information"""

import re
from typing import Optional, Dict
from datetime import datetime
from bs4 import BeautifulSoup
from dateutil import parser as date_parser


def parse_license_code(html_message: str) -> Optional[str]:
    """
    Extract license code from HTML response
    
    Args:
        html_message: HTML string from API response
        
    Returns:
        License code string or None if not found
    """
    # Try regex first (faster)
    match = re.search(r'<b>License Code:</b>\s*([A-Z0-9-]+)', html_message)
    if match:
        return match.group(1)
    
    # Fallback to BeautifulSoup
    try:
        soup = BeautifulSoup(html_message, 'html.parser')
        # Look for text containing "License Code:"
        for tag in soup.find_all(['b', 'strong']):
            if 'License Code' in tag.get_text():
                next_sibling = tag.next_sibling
                if next_sibling:
                    code = next_sibling.strip()
                    if re.match(r'^[A-Z0-9-]+$', code):
                        return code
    except Exception:
        pass
    
    return None


def parse_license_name(html_message: str) -> Optional[str]:
    """Extract name from HTML response"""
    match = re.search(r'<b>Name:</b>\s*([^<]+)', html_message)
    if match:
        return match.group(1).strip()
    return None


def parse_license_email(html_message: str) -> Optional[str]:
    """Extract email from HTML response"""
    match = re.search(r'<b>Email:</b>\s*([^<]+)', html_message)
    if match:
        return match.group(1).strip()
    return None


def parse_expiry_date(html_message: str) -> Optional[datetime]:
    """
    Extract expiry date from HTML response
    
    Args:
        html_message: HTML string from API response
        
    Returns:
        Datetime object or None if not found
    """
    # Look for "valid until" pattern
    patterns = [
        r'valid until\s+([^<]+)',
        r'expires?\s+([^<]+)',
        r'valid until\s+([A-Za-z]+\s+\d{1,2},\s+\d{4}[^<]*)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, html_message, re.IGNORECASE)
        if match:
            date_str = match.group(1).strip()
            try:
                # Try to parse the date
                return date_parser.parse(date_str, fuzzy=True)
            except (ValueError, TypeError):
                continue
    
    return None


def parse_license_data(html_message: str) -> Dict[str, Optional[str]]:
    """
    Parse all license information from HTML response
    
    Args:
        html_message: HTML string from API response
        
    Returns:
        Dictionary with license data
    """
    return {
        "name": parse_license_name(html_message),
        "email": parse_license_email(html_message),
        "license_code": parse_license_code(html_message),
        "expiry_date": parse_expiry_date(html_message),
        "raw_html": html_message
    }