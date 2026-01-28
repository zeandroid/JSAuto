"""Generic API client for job board interactions."""
import logging
import time
from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class APIClient:
    """Reusable HTTP client with retry logic and rate limiting."""

    def __init__(self, base_url: str = "", timeout: int = 30, max_retries: int = 3):
        """
        Initialize the API client.

        Args:
            base_url: Base URL for API calls (e.g., 'https://api.creativecircle.com').
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retries for failed requests.
        """
        self.base_url = base_url
        self.timeout = timeout
        self.session = self._create_session(max_retries)

    def _create_session(self, max_retries: int) -> requests.Session:
        """Create requests session with retry strategy."""
        session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Make a GET request.

        Args:
            endpoint: API endpoint (appended to base_url).
            params: Query parameters.
            headers: Request headers.

        Returns:
            Response JSON as dictionary.

        Raises:
            requests.RequestException: If request fails.
        """
        url = f"{self.base_url}{endpoint}" if self.base_url else endpoint
        try:
            response = self.session.get(
                url, params=params, headers=headers, timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"GET request failed for {url}: {e}")
            raise

    def post(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Make a POST request.

        Args:
            endpoint: API endpoint.
            json_data: JSON payload.
            headers: Request headers.

        Returns:
            Response JSON as dictionary.
        """
        url = f"{self.base_url}{endpoint}" if self.base_url else endpoint
        try:
            response = self.session.post(
                url, json=json_data, headers=headers, timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"POST request failed for {url}: {e}")
            raise

    def close(self):
        """Close the session."""
        self.session.close()
