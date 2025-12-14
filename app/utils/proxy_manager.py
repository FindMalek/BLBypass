"""Proxy management utilities"""

import requests
import random
from typing import List, Optional
from rich.console import Console

console = Console()


class ProxyManager:
    """Manages proxy fetching and rotation"""
    
    PROXYSCRAPE_URL = "https://api.proxyscrape.com/v4/free-proxy-list/get"
    PUBPROXY_URL = "http://pubproxy.com/api/proxy"
    
    def __init__(self, source: str = "proxyscrape"):
        """
        Initialize proxy manager
        
        Args:
            source: Proxy source ('proxyscrape' or 'pubproxy')
        """
        self.source = source
        self.proxies: List[str] = []
        self.current_index = 0
    
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
            params = {
                "request": "displayproxies",
                "protocol": protocol,
                "timeout": timeout,
                "country": country,
                "ssl": ssl,
                "anonymity": "all",
                "limit": min(count, 2000)  # Max 2000
            }
            
            response = requests.get(self.PROXYSCRAPE_URL, params=params, timeout=10)
            response.raise_for_status()
            
            # ProxyScrape returns plain text, one proxy per line
            proxies = [
                line.strip() 
                for line in response.text.strip().split('\n') 
                if line.strip() and ':' in line.strip()
            ]
            
            console.print(f"[green]✓[/green] Fetched {len(proxies)} proxies from ProxyScrape")
            return proxies
            
        except Exception as e:
            console.print(f"[red]Error fetching proxies:[/red] {str(e)}")
            return []
    
    def _fetch_pubproxy(self, count: int) -> List[str]:
        """Fetch proxies from PubProxy"""
        proxies = []
        try:
            # PubProxy returns one proxy per request, so we need multiple requests
            for _ in range(min(count, 5)):  # Free tier limit
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
                
                # Small delay to avoid rate limiting
                import time
                time.sleep(0.5)
            
            console.print(f"[green]✓[/green] Fetched {len(proxies)} proxies from PubProxy")
            return proxies
            
        except Exception as e:
            console.print(f"[red]Error fetching proxies:[/red] {str(e)}")
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
    
    def get_working_proxy(self, max_attempts: int = 10) -> Optional[str]:
        """
        Get a working proxy by testing multiple proxies
        
        Args:
            max_attempts: Maximum number of proxies to test
            
        Returns:
            Working proxy string or None
        """
        if not self.proxies:
            return None
        
        tested = set()
        attempts = 0
        
        while attempts < max_attempts and len(tested) < len(self.proxies):
            proxy = self.get_random_proxy()
            if proxy in tested:
                continue
            
            tested.add(proxy)
            attempts += 1
            
            if self.test_proxy(proxy):
                console.print(f"[green]✓[/green] Found working proxy: {proxy}")
                return proxy
            else:
                console.print(f"[dim]Testing proxy {attempts}/{max_attempts}: {proxy}...[/dim]")
        
        return None