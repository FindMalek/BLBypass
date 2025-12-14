"""API client for BlackLight endpoints"""

import warnings
import urllib3
import time
import random
# Disable urllib3 warnings completely
urllib3.disable_warnings(urllib3.exceptions.NotOpenSSLWarning)

import requests
import logging
from typing import Dict, Optional, List
from rich.console import Console
from app.utils.proxy_manager import ProxyManager

console = Console()
logger = logging.getLogger(__name__)


class BlackLightAPI:
    """Client for interacting with BlackLight license endpoints"""
    
    BASE_URL = "https://michelf.ca/processus"
    
    # User agents to rotate through
    USER_AGENTS = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
    ]
    
    def __init__(self, lang: str = "en", debug: bool = False, delay: float = 2.0, 
                retry_attempts: int = 3, retry_delay: float = 5.0, proxy: Optional[str] = None,
                auto_proxy: bool = False, proxy_source: str = "proxyscrape"):
        self.lang = lang
        self.debug = debug
        self.delay = delay
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.proxy = proxy
        self.auto_proxy = auto_proxy
        self.proxy_source = proxy_source
        
        # Initialize proxy manager if auto_proxy is enabled
        if self.auto_proxy:
            self.proxy_manager = ProxyManager(source=proxy_source)
            if not self.proxy:
                # Fetch proxies automatically
                self.proxy_manager.proxies = self.proxy_manager.fetch_proxies(
                    count=50,
                    protocol="http",
                    ssl="yes"
                )
                if self.proxy_manager.proxies:
                    self.proxy = self.proxy_manager.get_working_proxy(max_attempts=5)
                    if self.proxy:
                        console.print(f"[green]✓[/green] Using auto-fetched proxy: {self.proxy}")
        
        self._rotate_user_agent()
        self._setup_session()
        
        if self.debug:
            logging.basicConfig(
                level=logging.DEBUG,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            # Enable requests debug logging
            import http.client
            http.client.HTTPConnection.debuglevel = 1
    
    def _rotate_user_agent(self):
        """Rotate to a random user agent"""
        self.user_agent = random.choice(self.USER_AGENTS)
    
    def _setup_session(self):
        """Setup a new session with fresh headers"""
        self.session = requests.Session()
        
        # Rotate user agent
        self._rotate_user_agent()
        
        self.session.headers.update({
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "application/json",
            "Origin": "https://michelf.ca",
            "Referer": "https://michelf.ca/projects/black-light/trial/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": self.user_agent,
            "sec-ch-ua": '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
        })
        
        # Set proxy if provided
        if self.proxy:
            self.session.proxies = {
                'http': self.proxy,
                'https': self.proxy
            }
    
    def _is_rate_limited(self, data: Dict) -> bool:
        """Check if response indicates rate limiting"""
        if not isinstance(data, dict):
            return False
        
        error_msg = str(data.get('message', '')).lower()
        error_list = data.get('error', [])
        
        rate_limit_indicators = [
            'rate limit',
            'too many requests',
            'please retry',
            'try again later',
            'unable to process',
            'temporarily unavailable'
        ]
        
        # Check message field
        if any(indicator in error_msg for indicator in rate_limit_indicators):
            return True
        
        # Check error list
        if isinstance(error_list, list):
            error_str = ' '.join(str(e) for e in error_list).lower()
            if any(indicator in error_str for indicator in rate_limit_indicators):
                return True
        
        return False
    
    def _wait_with_jitter(self, base_delay: float):
        """Wait with random jitter to avoid synchronized requests"""
        jitter = random.uniform(0.5, 1.5)  # 50% to 150% of base delay
        wait_time = base_delay * jitter
        if self.debug:
            console.print(f"[dim]Waiting {wait_time:.2f}s before retry...[/dim]")
        time.sleep(wait_time)
    
    def request_trial_license(
        self, 
        name: str, 
        email: str,
        retry_count: int = 0
    ) -> Optional[Dict]:
        """
        Request a trial license for BlackLight 3 with retry logic
        
        Args:
            name: Name for the license
            email: Email address for the license
            retry_count: Internal retry counter
            
        Returns:
            Response dictionary with success status and message, or None on error
        """
        url = f"{self.BASE_URL}/trial.php?lang={self.lang}"
        payload = {
            "sku": "BLACK-L.3:TRIAL",
            "name": name,
            "email": email
        }
        
        if self.debug:
            logger.debug(f"Request URL: {url}")
            logger.debug(f"Request payload: {payload}")
            logger.debug(f"User-Agent: {self.user_agent}")
            console.print(f"[dim]DEBUG:[/dim] POST {url}")
            console.print(f"[dim]DEBUG:[/dim] Payload: {payload}")
            if retry_count > 0:
                console.print(f"[dim]DEBUG:[/dim] Retry attempt {retry_count}/{self.retry_attempts}")
        
        # Add random delay before request (helps avoid rate limits)
        if retry_count == 0 and self.delay > 0:
            self._wait_with_jitter(self.delay)
        
        try:
            response = self.session.post(url, json=payload, timeout=15)
            
            if self.debug:
                logger.debug(f"Response status: {response.status_code}")
                logger.debug(f"Response headers: {dict(response.headers)}")
                logger.debug(f"Response text: {response.text[:500]}")
                console.print(f"[dim]DEBUG:[/dim] Status: {response.status_code}")
                console.print(f"[dim]DEBUG:[/dim] Headers: {dict(response.headers)}")
            
            response.raise_for_status()
            
            try:
                data = response.json()
            except ValueError as json_error:
                if self.debug:
                    console.print(f"[red]DEBUG:[/red] JSON decode error: {json_error}")
                    console.print(f"[red]DEBUG:[/red] Response text: {response.text}")
                console.print(f"[red]Invalid JSON response:[/red] {response.text[:200]}")
                return None
            
            if self.debug:
                logger.debug(f"Response data: {data}")
                console.print(f"[dim]DEBUG:[/dim] Response data: {data}")
            
            # Check for rate limiting
            if self._is_rate_limited(data):
                if retry_count < self.retry_attempts:
                    console.print(f"[yellow]Rate limited. Retrying in {self.retry_delay}s...[/yellow]")
                    # Rotate user agent and create new session
                    self._setup_session()
                    self._wait_with_jitter(self.retry_delay)
                    return self.request_trial_license(name, email, retry_count + 1)
                else:
                    console.print("[red]Error:[/red] Rate limited. Max retries exceeded.")
                    return None
            
            # Check for error response format: {"error": ["message", "error text"]}
            if "error" in data:
                error_list = data.get("error", [])
                if isinstance(error_list, list) and len(error_list) >= 2:
                    error_msg = error_list[1]  # Second element is the error message
                else:
                    error_msg = str(error_list)
                if self.debug:
                    console.print(f"[red]DEBUG:[/red] Error response: {data}")
                console.print(f"[red]Error:[/red] {error_msg}")
                return None
            
            # Check for success response
            if data.get("success"):
                return data
            else:
                # Try to get error message from various possible formats
                error_msg = (
                    data.get('message') or 
                    data.get('error') or 
                    str(data.get('error', 'Unknown error'))
                )
                if self.debug:
                    console.print(f"[red]DEBUG:[/red] Full response: {data}")
                console.print(f"[red]Error:[/red] {error_msg}")
                return None
                
        except requests.exceptions.Timeout as e:
            if retry_count < self.retry_attempts:
                console.print(f"[yellow]Timeout. Retrying in {self.retry_delay}s...[/yellow]")
                self._setup_session()
                self._wait_with_jitter(self.retry_delay)
                return self.request_trial_license(name, email, retry_count + 1)
            error_msg = f"Request timed out after 15 seconds: {str(e)}"
            if self.debug:
                logger.exception("Timeout error")
            console.print(f"[red]Network error:[/red] {error_msg}")
            return None
        except requests.exceptions.ConnectionError as e:
            if retry_count < self.retry_attempts:
                console.print(f"[yellow]Connection error. Retrying in {self.retry_delay}s...[/yellow]")
                self._setup_session()
                self._wait_with_jitter(self.retry_delay)
                return self.request_trial_license(name, email, retry_count + 1)
            error_msg = f"Connection error: {str(e)}"
            if self.debug:
                logger.exception("Connection error")
            console.print(f"[red]Network error:[/red] {error_msg}")
            return None
        except requests.exceptions.HTTPError as e:
            # Retry on 429 (Too Many Requests) or 503 (Service Unavailable)
            if e.response.status_code in [429, 503] and retry_count < self.retry_attempts:
                console.print(f"[yellow]HTTP {e.response.status_code}. Retrying in {self.retry_delay}s...[/yellow]")
                self._setup_session()
                self._wait_with_jitter(self.retry_delay)
                return self.request_trial_license(name, email, retry_count + 1)
            error_msg = f"HTTP {e.response.status_code}: {str(e)}"
            if self.debug:
                logger.exception("HTTP error")
                console.print(f"[red]DEBUG:[/red] Response text: {e.response.text[:500]}")
            console.print(f"[red]HTTP error:[/red] {error_msg}")
            if self.debug and hasattr(e, 'response'):
                console.print(f"[dim]DEBUG:[/dim] Response body: {e.response.text[:500]}")
            return None
        except requests.exceptions.RequestException as e:
            if retry_count < self.retry_attempts:
                console.print(f"[yellow]Request failed. Retrying in {self.retry_delay}s...[/yellow]")
                self._setup_session()
                self._wait_with_jitter(self.retry_delay)
                return self.request_trial_license(name, email, retry_count + 1)
            error_msg = f"Request failed: {str(e)}"
            if self.debug:
                logger.exception("Request exception")
            console.print(f"[red]Network error:[/red] {error_msg}")
            return None
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            if self.debug:
                logger.exception("Unexpected error")
            console.print(f"[red]Error:[/red] {error_msg}")
            return None
    
    def request_full_license(
        self,
        name: str,
        email: str,
        payment_intent_id: Optional[str] = None,
        payment_secret: Optional[str] = None,
        payment_session: Optional[str] = None,
        **kwargs
    ) -> Optional[Dict]:
        """
        Attempt to request a full license (experimental/research)
        
        Note: This requires valid Stripe payment intents and may not work
        without actual payment processing.
        
        Args:
            name: Name for the license
            email: Email address for the license
            payment_intent_id: Stripe payment intent ID
            payment_secret: Stripe payment intent client secret
            payment_session: Payment session ID
            **kwargs: Additional parameters
            
        Returns:
            Response dictionary or None on error
        """
        url = f"{self.BASE_URL}/co.php?lang={self.lang}"
        
        payload = {
            "currency": kwargs.get("currency", "USD"),
            "items": [{
                "sku": "BLACK-L.3",
                "vars": {
                    "name": name,
                    "email": email,
                    "qty": "1"
                },
                "price": kwargs.get("price", 1899)
            }],
            "subtotal": kwargs.get("subtotal", 1899),
            "tax": [],
            "total": kwargs.get("total", 1899),
            "donation": None,
            "pmeth": kwargs.get("pmeth", "pi"),
            "billing": {
                "name": name,
                "email": email,
                "company": kwargs.get("company", ""),
                "address1": kwargs.get("address1", ""),
                "address2": kwargs.get("address2", ""),
                "city": kwargs.get("city", ""),
                "zip": kwargs.get("zip", ""),
                "country": kwargs.get("country", "US"),
                "state": kwargs.get("state", None)
            },
            "ps": payment_session or kwargs.get("ps", ""),
            "pi": payment_intent_id or kwargs.get("pi", ""),
            "pics": payment_secret or kwargs.get("pics", ""),
            "tz-offset": kwargs.get("tz_offset", -60),
            "invoice_no": None
        }
        
        if self.debug:
            logger.debug(f"Request URL: {url}")
            logger.debug(f"Request payload: {payload}")
            console.print(f"[dim]DEBUG:[/dim] POST {url}")
            console.print(f"[dim]DEBUG:[/dim] Payload: {payload}")
        
        try:
            response = self.session.post(url, json=payload, timeout=10)
            
            if self.debug:
                logger.debug(f"Response status: {response.status_code}")
                logger.debug(f"Response text: {response.text[:500]}")
                console.print(f"[dim]DEBUG:[/dim] Status: {response.status_code}")
                console.print(f"[dim]DEBUG:[/dim] Response: {response.text[:500]}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if self.debug:
                logger.exception("Request exception")
            console.print(f"[red]Network error:[/red] {str(e)}")
            return None
        except ValueError as e:
            if self.debug:
                logger.exception("JSON decode error")
            console.print(f"[red]Invalid response:[/red] {str(e)}")
            return None