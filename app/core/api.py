"""API client for BlackLight endpoints"""

import warnings
import urllib3
# Disable urllib3 warnings completely
urllib3.disable_warnings(urllib3.exceptions.NotOpenSSLWarning)

import requests
import logging
from typing import Dict, Optional
from rich.console import Console

console = Console()
logger = logging.getLogger(__name__)


class BlackLightAPI:
    """Client for interacting with BlackLight license endpoints"""
    
    BASE_URL = "https://michelf.ca/processus"
    
    def __init__(self, lang: str = "en", debug: bool = False):
        self.lang = lang
        self.debug = debug
        self.session = requests.Session()
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
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
        })
        
        if self.debug:
            logging.basicConfig(
                level=logging.DEBUG,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            # Enable requests debug logging
            import http.client
            http.client.HTTPConnection.debuglevel = 1
    
    def request_trial_license(
        self, 
        name: str, 
        email: str
    ) -> Optional[Dict]:
        """
        Request a trial license for BlackLight 3
        
        Args:
            name: Name for the license
            email: Email address for the license
            
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
            console.print(f"[dim]DEBUG:[/dim] POST {url}")
            console.print(f"[dim]DEBUG:[/dim] Payload: {payload}")
        
        try:
            response = self.session.post(url, json=payload, timeout=10)
            
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
            error_msg = f"Request timed out after 10 seconds: {str(e)}"
            if self.debug:
                logger.exception("Timeout error")
            console.print(f"[red]Network error:[/red] {error_msg}")
            return None
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Connection error: {str(e)}"
            if self.debug:
                logger.exception("Connection error")
            console.print(f"[red]Network error:[/red] {error_msg}")
            return None
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP {e.response.status_code}: {str(e)}"
            if self.debug:
                logger.exception("HTTP error")
                console.print(f"[red]DEBUG:[/red] Response text: {e.response.text[:500]}")
            console.print(f"[red]HTTP error:[/red] {error_msg}")
            if self.debug and hasattr(e, 'response'):
                console.print(f"[dim]DEBUG:[/dim] Response body: {e.response.text[:500]}")
            return None
        except requests.exceptions.RequestException as e:
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