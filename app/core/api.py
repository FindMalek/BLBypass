"""API client for BlackLight endpoints"""

import warnings
import urllib3
import time
import random
# Disable urllib3 warnings completely
urllib3.disable_warnings(urllib3.exceptions.NotOpenSSLWarning)

import requests
import logging
from typing import Dict, Optional, List, Tuple
from rich.console import Console
from app.utils.proxy_manager import ProxyManager

console = Console()
logger = logging.getLogger(__name__)


class BlackLightAPI:
    """Client for interacting with BlackLight license endpoints"""
    
    BASE_URL = "https://michelf.ca/processus"
    
    # Realistic browser fingerprints with matching headers
    BROWSER_PROFILES = [
        {
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "sec_ch_ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "sec_ch_ua_mobile": "?0",
            "sec_ch_ua_platform": '"macOS"',
            "accept_language": "en-US,en;q=0.9",
            "accept_encoding": "gzip, deflate, br, zstd"
        },
        {
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "sec_ch_ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "sec_ch_ua_mobile": "?0",
            "sec_ch_ua_platform": '"Windows"',
            "accept_language": "en-US,en;q=0.9",
            "accept_encoding": "gzip, deflate, br, zstd"
        },
        {
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
            "sec_ch_ua": None,  # Safari doesn't use sec-ch-ua
            "sec_ch_ua_mobile": None,
            "sec_ch_ua_platform": None,
            "accept_language": "en-US,en;q=0.9",
            "accept_encoding": "gzip, deflate, br"
        },
        {
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "sec_ch_ua": None,  # Firefox doesn't use sec-ch-ua
            "sec_ch_ua_mobile": None,
            "sec_ch_ua_platform": None,
            "accept_language": "en-US,en;q=0.5",
            "accept_encoding": "gzip, deflate, br"
        },
        {
            "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "sec_ch_ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "sec_ch_ua_mobile": "?0",
            "sec_ch_ua_platform": '"Linux"',
            "accept_language": "en-US,en;q=0.9",
            "accept_encoding": "gzip, deflate, br, zstd"
        },
    ]
    
    def __init__(self, lang: str = "en", debug: bool = False, delay: float = 3.0, 
                retry_attempts: int = 3, retry_delay: float = 10.0, proxy: Optional[str] = None,
                auto_proxy: bool = False, proxy_source: str = "proxyscrape"):
        self.lang = lang
        self.debug = debug
        self.delay = delay
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.proxy = proxy
        self.auto_proxy = auto_proxy
        self.proxy_source = proxy_source
        self.proxy_failures = 0
        self.max_proxy_failures = 3
        self.rate_limit_backoff = 0  # Track rate limit backoff time
        self.last_request_time = 0  # Track timing between requests
        
        # Initialize proxy manager if auto_proxy is enabled
        if self.auto_proxy:
            self.proxy_manager = ProxyManager(source=proxy_source, debug=debug)
            if not self.proxy:
                console.print("[cyan]Fetching proxies...[/cyan]")
                self.proxy_manager.proxies = self.proxy_manager.fetch_proxies(
                    count=50,
                    protocol="http",
                    ssl="all"
                )
                if self.proxy_manager.proxies:
                    self.proxy = self.proxy_manager.get_working_proxy(
                        max_attempts=3, 
                        skip_test=False
                    )
                    if self.proxy:
                        console.print(f"[green]✓[/green] Using auto-fetched proxy: {self.proxy}")
                    else:
                        console.print("[yellow]Warning:[/yellow] No working proxy found. Continuing without proxy.")
                else:
                    console.print("[yellow]Warning:[/yellow] Could not fetch proxies. Continuing without proxy.")
        
        self._select_browser_profile()
        self._setup_session()
        
        if self.debug:
            logging.basicConfig(
                level=logging.DEBUG,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            import http.client
            http.client.HTTPConnection.debuglevel = 1
    
    def _select_browser_profile(self):
        """Select a random browser profile for realistic fingerprinting"""
        self.browser_profile = random.choice(self.BROWSER_PROFILES)
        self.user_agent = self.browser_profile["user_agent"]
    
    def _get_realistic_headers(self) -> Dict[str, str]:
        """Generate realistic headers based on browser profile"""
        headers = {
            "Accept": "*/*",
            "Accept-Language": self.browser_profile["accept_language"],
            "Accept-Encoding": self.browser_profile["accept_encoding"],
            "Content-Type": "application/json",
            "Origin": "https://michelf.ca",
            "Referer": "https://michelf.ca/projects/black-light/trial/",
            "User-Agent": self.user_agent,
        }
        
        # Add sec-ch-ua headers only for Chromium-based browsers
        if self.browser_profile["sec_ch_ua"]:
            headers.update({
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "sec-ch-ua": self.browser_profile["sec_ch_ua"],
                "sec-ch-ua-mobile": self.browser_profile["sec_ch_ua_mobile"],
                "sec-ch-ua-platform": self.browser_profile["sec_ch_ua_platform"],
            })
        
        return headers
    
    def _setup_session(self):
        """Setup a new session with fresh headers"""
        self.session = requests.Session()
        
        # Select new browser profile for each session
        self._select_browser_profile()
        
        # Get realistic headers
        headers = self._get_realistic_headers()
        self.session.headers.update(headers)
        
        if self.proxy:
            self.session.proxies = {
                'http': f'http://{self.proxy}',
                'https': f'http://{self.proxy}'
            }
            if self.debug:
                console.print(f"[dim]DEBUG:[/dim] Using proxy: {self.proxy}")
        else:
            self.session.proxies = {}
            if self.debug:
                console.print(f"[dim]DEBUG:[/dim] Using direct connection (no proxy)")
    
    def _is_rate_limited(self, data: Dict) -> bool:
        """Check if response indicates rate limiting"""
        if not isinstance(data, dict):
            return False
        
        # Check for retry flag
        if data.get('retry') is True:
            return True
        
        # Check error message
        error_data = data.get('error', {})
        if isinstance(error_data, dict):
            error_msg = str(error_data.get('message', '')).lower()
        else:
            error_msg = str(data.get('message', '')).lower()
        
        rate_limit_indicators = [
            'rate limit',
            'too many requests',
            'please retry',
            'try again later',
            'unable to process',
            'temporarily unavailable',
            'retry at later time'
        ]
        
        if any(indicator in error_msg for indicator in rate_limit_indicators):
            return True
        
        return False
    
    def _wait_with_jitter(self, base_delay: float):
        """Wait with random jitter to avoid synchronized requests"""
        jitter = random.uniform(0.8, 1.5)  # 80% to 150% of base delay
        wait_time = base_delay * jitter
        
        # Add human-like delay (humans don't make requests instantly)
        human_delay = random.uniform(0.5, 2.0)
        total_wait = wait_time + human_delay
        
        if self.debug:
            console.print(f"[dim]Waiting {total_wait:.2f}s before request...[/dim]")
        time.sleep(total_wait)
    
    def _calculate_rate_limit_backoff(self, retry_count: int) -> float:
        """Calculate exponential backoff for rate limits"""
        # Exponential backoff: 30s, 60s, 120s, etc.
        base_backoff = 30
        backoff_time = base_backoff * (2 ** retry_count)
        
        # Add jitter to avoid synchronized retries
        jitter = random.uniform(0.8, 1.2)
        return backoff_time * jitter
    
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
            logger.debug(f"Browser Profile: {self.browser_profile.get('user_agent', 'Unknown')}")
            console.print(f"[dim]DEBUG:[/dim] POST {url}")
            console.print(f"[dim]DEBUG:[/dim] Payload: {payload}")
            if retry_count > 0:
                console.print(f"[dim]DEBUG:[/dim] Retry attempt {retry_count}/{self.retry_attempts}")
        
        # Respect rate limit backoff
        if self.rate_limit_backoff > 0:
            console.print(f"[yellow]Rate limit backoff: waiting {self.rate_limit_backoff:.0f}s...[/yellow]")
            time.sleep(self.rate_limit_backoff)
            self.rate_limit_backoff = 0
        
        # Add realistic delay before request
        if retry_count == 0:
            self._wait_with_jitter(self.delay)
        
        # Human-like timing between requests
        current_time = time.time()
        if self.last_request_time > 0:
            time_since_last = current_time - self.last_request_time
            if time_since_last < 2.0:  # Minimum 2 seconds between requests
                time.sleep(2.0 - time_since_last + random.uniform(0, 1))
        
        try:
            response = self.session.post(url, json=payload, timeout=15)
            self.last_request_time = time.time()
            
            if self.debug:
                logger.debug(f"Response status: {response.status_code}")
                logger.debug(f"Response headers: {dict(response.headers)}")
                logger.debug(f"Response text: {response.text[:500]}")
                console.print(f"[dim]DEBUG:[/dim] Status: {response.status_code}")
            
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
            
            # Check for rate limiting with exponential backoff
            if self._is_rate_limited(data):
                if retry_count < self.retry_attempts:
                    backoff_time = self._calculate_rate_limit_backoff(retry_count)
                    self.rate_limit_backoff = backoff_time
                    console.print(f"[yellow]⚠ Rate limited. Waiting {backoff_time:.0f}s before retry...[/yellow]")
                    # Rotate browser profile and create new session
                    self._select_browser_profile()
                    self._setup_session()
                    time.sleep(backoff_time)
                    return self.request_trial_license(name, email, retry_count + 1)
                else:
                    console.print("[red]Error:[/red] Rate limited. Max retries exceeded. Your IP may be temporarily banned.")
                    console.print("[yellow]Suggestion:[/yellow] Wait 5-10 minutes or use --auto-proxy to use a proxy.")
                    return None
            
            # Check for error response format
            if "error" in data:
                error_data = data.get("error", {})
                if isinstance(error_data, dict):
                    error_msg = error_data.get('message', 'Unknown error')
                elif isinstance(error_data, list) and len(error_data) >= 2:
                    error_msg = error_data[1]
                else:
                    error_msg = str(error_data)
                
                if self.debug:
                    console.print(f"[red]DEBUG:[/red] Error response: {data}")
                console.print(f"[red]Error:[/red] {error_msg}")
                return None
            
            # Check for success response
            if data.get("success"):
                # Reset rate limit backoff on success
                self.rate_limit_backoff = 0
                return data
            else:
                error_msg = (
                    data.get('message') or 
                    str(data.get('error', 'Unknown error'))
                )
                if self.debug:
                    console.print(f"[red]DEBUG:[/red] Full response: {data}")
                console.print(f"[red]Error:[/red] {error_msg}")
                return None
                
        except requests.exceptions.ProxyError as e:
            # Handle proxy errors specifically
            self.proxy_failures += 1
            
            # If we've tried too many proxies, fall back to direct connection
            if self.proxy_failures >= self.max_proxy_failures:
                console.print(f"[yellow]Multiple proxies failed ({self.proxy_failures}). Falling back to direct connection...[/yellow]")
                self.proxy = None
                self.proxy_failures = 0  # Reset counter
                self._select_browser_profile()
                self._setup_session()
                if retry_count < self.retry_attempts:
                    self._wait_with_jitter(1.0)
                    return self.request_trial_license(name, email, retry_count)
                else:
                    error_msg = f"Proxy error: {str(e)}"
                    if self.debug:
                        logger.exception("Proxy error")
                    console.print(f"[red]Network error:[/red] {error_msg}")
                    return None
            
            # Try a different proxy if we have more available
            if self.auto_proxy and hasattr(self, 'proxy_manager') and self.proxy_manager.proxies:
                console.print(f"[yellow]Proxy failed ({self.proxy}). Trying different proxy ({self.proxy_failures}/{self.max_proxy_failures})...[/yellow]")
                new_proxy = self.proxy_manager.get_random_proxy()
                if new_proxy and new_proxy != self.proxy:
                    self.proxy = new_proxy
                    self._select_browser_profile()
                    self._setup_session()
                    if retry_count < self.retry_attempts:
                        self._wait_with_jitter(1.0)  # Short delay before retry
                        return self.request_trial_license(name, email, retry_count)  # Don't increment retry_count for proxy switches
                else:
                    # No more proxies available, fall back to direct
                    console.print("[yellow]No more proxies available. Falling back to direct connection...[/yellow]")
                    self.proxy = None
                    self.proxy_failures = 0
                    self._select_browser_profile()
                    self._setup_session()
                    if retry_count < self.retry_attempts:
                        self._wait_with_jitter(1.0)
                        return self.request_trial_license(name, email, retry_count)
            
            # If no proxy manager or no more proxies, fall back to direct
            if retry_count < self.retry_attempts:
                console.print(f"[yellow]Proxy failed. Retrying without proxy...[/yellow]")
                self.proxy = None
                self.proxy_failures = 0
                self._select_browser_profile()
                self._setup_session()
                self._wait_with_jitter(self.retry_delay)
                return self.request_trial_license(name, email, retry_count + 1)
            
            error_msg = f"Proxy error: {str(e)}"
            if self.debug:
                logger.exception("Proxy error")
            console.print(f"[red]Network error:[/red] {error_msg}")
            return None
            
        except requests.exceptions.Timeout as e:
            if self.proxy and retry_count < self.retry_attempts:
                console.print(f"[yellow]Timeout with proxy. Retrying without proxy...[/yellow]")
                self.proxy = None
                self._select_browser_profile()
                self._setup_session()
                self._wait_with_jitter(self.retry_delay)
                return self.request_trial_license(name, email, retry_count + 1)
            
            if retry_count < self.retry_attempts:
                console.print(f"[yellow]Timeout. Retrying in {self.retry_delay}s...[/yellow]")
                self._select_browser_profile()
                self._setup_session()
                self._wait_with_jitter(self.retry_delay)
                return self.request_trial_license(name, email, retry_count + 1)
            error_msg = f"Request timed out after 15 seconds: {str(e)}"
            if self.debug:
                logger.exception("Timeout error")
            console.print(f"[red]Network error:[/red] {error_msg}")
            return None
            
        except requests.exceptions.ConnectionError as e:
            if self.proxy and retry_count < self.retry_attempts:
                console.print(f"[yellow]Connection error with proxy. Retrying without proxy...[/yellow]")
                self.proxy = None
                self._select_browser_profile()
                self._setup_session()
                self._wait_with_jitter(self.retry_delay)
                return self.request_trial_license(name, email, retry_count + 1)
            
            if retry_count < self.retry_attempts:
                console.print(f"[yellow]Connection error. Retrying in {self.retry_delay}s...[/yellow]")
                self._select_browser_profile()
                self._setup_session()
                self._wait_with_jitter(self.retry_delay)
                return self.request_trial_license(name, email, retry_count + 1)
            error_msg = f"Connection error: {str(e)}"
            if self.debug:
                logger.exception("Connection error")
            console.print(f"[red]Network error:[/red] {error_msg}")
            return None
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code in [429, 503] and retry_count < self.retry_attempts:
                backoff_time = self._calculate_rate_limit_backoff(retry_count)
                console.print(f"[yellow]HTTP {e.response.status_code}. Waiting {backoff_time:.0f}s...[/yellow]")
                self._select_browser_profile()
                self._setup_session()
                time.sleep(backoff_time)
                return self.request_trial_license(name, email, retry_count + 1)
            error_msg = f"HTTP {e.response.status_code}: {str(e)}"
            if self.debug:
                logger.exception("HTTP error")
                console.print(f"[red]DEBUG:[/red] Response text: {e.response.text[:500]}")
            console.print(f"[red]HTTP error:[/red] {error_msg}")
            return None
            
        except requests.exceptions.RequestException as e:
            if retry_count < self.retry_attempts:
                console.print(f"[yellow]Request failed. Retrying in {self.retry_delay}s...[/yellow]")
                self._select_browser_profile()
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