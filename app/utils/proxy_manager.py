"""Proxy management utilities"""

import requests
import random
import time
from typing import List, Optional
from rich.console import Console

console = Console()


class ProxyManager:
    """Manages proxy fetching and rotation"""
    
    PROXYSCRAPE_URL = "https://api.proxyscrape.com/v4/free-proxy-list/get"
    PUBPROXY_URL = "http://pubproxy.com/api/proxy"
    
    def __init__(self, source: str = "proxyscrape", debug: bool = False):
        """
        Initialize proxy manager
        
        Args:
            source: Proxy source ('proxyscrape' or 'pubproxy')
            debug: Enable debug output
        """
        self.source = source
        self.proxies: List[str] = []
        self.current_index = 0
        self.debug = debug
    
    def fetch_proxies(
        self, 
        count: int = 50,
        protocol: str = "http",
        country: str = "all",
        timeout: int = 10000,
        ssl: str = "yes"
    ) -> List[str]:
        """
        Fetch proxies from the configured source
        
        Args:
            count: Number of proxies to fetch
            protocol: Proxy protocol (http, socks4, socks5)
            country: Country code or 'all'
            timeout: Maximum timeout in milliseconds
            ssl: SSL support ('yes', 'no', 'all')
            
        Returns:
            List of proxy strings in format 'ip:port'
        """
        if self.source == "proxyscrape":
            return self._fetch_proxyscrape(count, protocol, country, timeout, ssl)
        elif self.source == "pubproxy":
            return self._fetch_pubproxy(count)
        else:
            console.print(f"[red]Error:[/red] Unknown proxy source: {self.source}")
            return []
    
    def _fetch_proxyscrape(
        self,
        count: int,
        protocol: str,
        country: str,
        timeout: int,
        ssl: str
    ) -> List[str]:
        """Fetch proxies from ProxyScrape"""
        try:
            # Try without SSL filter first (more proxies available)
            params = {
                "request": "displayproxies",
                "protocol": protocol,
                "timeout": timeout,
                "country": country,
                "anonymity": "all",
                "limit": min(count, 2000)  # Max 2000
            }
            
            # Only add SSL param for HTTP protocol
            if protocol == "http":
                params["ssl"] = ssl
            
            if self.debug:
                console.print(f"[dim]Fetching proxies from ProxyScrape with params: {params}[/dim]")
            
            response = requests.get(self.PROXYSCRAPE_URL, params=params, timeout=15)
            response.raise_for_status()
            
            if self.debug:
                console.print(f"[dim]Response status: {response.status_code}[/dim]")
                console.print(f"[dim]Response length: {len(response.text)}[/dim]")
                console.print(f"[dim]First 500 chars: {response.text[:500]}[/dim]")
            
            # ProxyScrape returns plain text, one proxy per line
            # Handle both empty response and actual proxy list
            text = response.text.strip()
            if not text:
                console.print("[yellow]Warning:[/yellow] ProxyScrape returned empty response")
                # Try without SSL requirement
                if ssl == "yes":
                    console.print("[dim]Retrying without SSL requirement...[/dim]")
                    params.pop("ssl", None)
                    response = requests.get(self.PROXYSCRAPE_URL, params=params, timeout=15)
                    text = response.text.strip()
            
            proxies = [
                line.strip() 
                for line in text.split('\n') 
                if line.strip() and ':' in line.strip() and self._is_valid_proxy_format(line.strip())
            ]
            
            if self.debug:
                console.print(f"[dim]Parsed {len(proxies)} proxies[/dim]")
                if proxies:
                    console.print(f"[dim]Sample proxies: {proxies[:3]}[/dim]")
            
            if proxies:
                console.print(f"[green]✓[/green] Fetched {len(proxies)} proxies from ProxyScrape")
            else:
                console.print("[yellow]Warning:[/yellow] No proxies found. The service might be temporarily unavailable.")
            
            return proxies
            
        except requests.exceptions.RequestException as e:
            console.print(f"[red]Error fetching proxies from ProxyScrape:[/red] {str(e)}")
            if self.debug:
                import traceback
                console.print(f"[dim]{traceback.format_exc()}[/dim]")
            return []
        except Exception as e:
            console.print(f"[red]Unexpected error fetching proxies:[/red] {str(e)}")
            if self.debug:
                import traceback
                console.print(f"[dim]{traceback.format_exc()}[/dim]")
            return []
    
    def _is_valid_proxy_format(self, proxy: str) -> bool:
        """Validate proxy format (ip:port)"""
        if ':' not in proxy:
            return False
        
        parts = proxy.split(':')
        if len(parts) != 2:
            return False
        
        ip, port = parts
        # Basic validation
        if not port.isdigit():
            return False
        
        # Check IP format (basic check)
        ip_parts = ip.split('.')
        if len(ip_parts) != 4:
            return False
        
        return all(part.isdigit() and 0 <= int(part) <= 255 for part in ip_parts)
    
    def _fetch_pubproxy(self, count: int) -> List[str]:
        """Fetch proxies from PubProxy"""
        proxies = []
        try:
            # PubProxy returns one proxy per request, so we need multiple requests
            max_requests = min(count, 5)  # Free tier limit
            
            if self.debug:
                console.print(f"[dim]Fetching {max_requests} proxies from PubProxy...[/dim]")
            
            for i in range(max_requests):
                params = {
                    "format": "json",
                    "type": "http",
                    "level": "elite",
                    "https": "true",
                    "limit": 1
                }
                
                response = requests.get(self.PUBPROXY_URL, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                if data.get('data'):
                    proxy_data = data['data'][0]
                    ip_port = proxy_data.get('ipPort', '')
                    if ip_port:
                        proxies.append(ip_port)
                        if self.debug:
                            console.print(f"[dim]Fetched proxy {i+1}/{max_requests}: {ip_port}[/dim]")
                
                # Small delay to avoid rate limiting
                if i < max_requests - 1:
                    time.sleep(0.5)
            
            if proxies:
                console.print(f"[green]✓[/green] Fetched {len(proxies)} proxies from PubProxy")
            else:
                console.print("[yellow]Warning:[/yellow] No proxies found from PubProxy")
            
            return proxies
            
        except Exception as e:
            console.print(f"[red]Error fetching proxies from PubProxy:[/red] {str(e)}")
            if self.debug:
                import traceback
                console.print(f"[dim]{traceback.format_exc()}[/dim]")
            return []
    
    def get_next_proxy(self) -> Optional[str]:
        """Get next proxy in rotation"""
        if not self.proxies:
            return None
        
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        return proxy
    
    def get_random_proxy(self) -> Optional[str]:
        """Get a random proxy from the list"""
        if not self.proxies:
            return None
        return random.choice(self.proxies)
    
    def test_proxy(self, proxy: str, timeout: int = 5) -> bool:
        """
        Test if a proxy is working
        
        Args:
            proxy: Proxy string in format 'ip:port'
            timeout: Timeout in seconds
            
        Returns:
            True if proxy is working, False otherwise
        """
        try:
            proxies = {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }
            
            response = requests.get(
                'https://httpbin.org/ip',
                proxies=proxies,
                timeout=timeout
            )
            return response.status_code == 200
        except:
            return False
    
    def get_working_proxy(self, max_attempts: int = 10, skip_test: bool = False) -> Optional[str]:
        """
        Get a working proxy by testing multiple proxies
        
        Args:
            max_attempts: Maximum number of proxies to test
            skip_test: If True, return first proxy without testing
            
        Returns:
            Working proxy string or None
        """
        if not self.proxies:
            return None
        
        if skip_test:
            # Just return the first proxy without testing
            return self.proxies[0]
        
        tested = set()
        attempts = 0
        
        while attempts < max_attempts and len(tested) < len(self.proxies):
            proxy = self.get_random_proxy()
            if proxy in tested:
                continue
            
            tested.add(proxy)
            attempts += 1
            
            if self.debug:
                console.print(f"[dim]Testing proxy {attempts}/{max_attempts}: {proxy}...[/dim]")
            
            if self.test_proxy(proxy):
                console.print(f"[green]✓[/green] Found working proxy: {proxy}")
                return proxy
        
        # If no working proxy found, return a random one anyway
        if self.proxies:
            console.print(f"[yellow]Warning:[/yellow] No tested proxies worked. Using random proxy: {self.proxies[0]}")
            return self.proxies[0]
        
        return None