"""API client for BlackLight endpoints"""

import requests
from typing import Dict, Optional
from rich.console import Console

console = Console()


class BlackLightAPI:
    """Client for interacting with BlackLight license endpoints"""
    
    BASE_URL = "https://michelf.ca/processus"
    
    def __init__(self, lang: str = "en"):
        self.lang = lang
        self.session = requests.Session()
        self.session.headers.update({
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json",
            "sec-ch-ua": '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
        })
    
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
        
        try:
            response = self.session.post(url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("success"):
                return data
            else:
                console.print(f"[red]Error:[/red] {data.get('message', 'Unknown error')}")
                return None
                
        except requests.exceptions.RequestException as e:
            console.print(f"[red]Network error:[/red] {str(e)}")
            return None
        except ValueError as e:
            console.print(f"[red]Invalid response:[/red] {str(e)}")
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
        
        try:
            response = self.session.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            console.print(f"[red]Network error:[/red] {str(e)}")
            return None
        except ValueError as e:
            console.print(f"[red]Invalid response:[/red] {str(e)}")
            return None