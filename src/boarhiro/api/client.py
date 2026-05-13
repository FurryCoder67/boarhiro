"""
HTTP client for communicating with BOARHIRO inference server.
"""

from typing import Optional, Dict, Any
import requests

from boarhiro.logger import get_logger
from boarhiro.utils import ServerError


class ServerClient:
    """Client for communicating with BOARHIRO inference server."""

    def __init__(self, server_url: str = "http://localhost:5000", timeout: float = 30.0):
        """
        Initialize server client.

        Args:
            server_url: Base URL of the inference server
            timeout: Request timeout in seconds
        """
        self.server_url = server_url
        self.timeout = timeout
        self.logger = get_logger("api-client")

    def generate(self, prompt: str, temperature: float = 0.7) -> str:
        """
        Generate response from the model.

        Args:
            prompt: Input prompt
            temperature: Sampling temperature (0.0-1.0)

        Returns:
            Generated response

        Raises:
            ServerError: If request fails
        """
        try:
            response = requests.post(
                f"{self.server_url}/generate",
                json={"prompt": prompt, "temperature": temperature},
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")
        except requests.exceptions.RequestException as e:
            self.logger.error("Generate request failed", error=str(e))
            raise ServerError(f"Failed to generate response: {e}", {"prompt": prompt})

    def health_check(self) -> bool:
        """
        Check if server is healthy.

        Returns:
            True if server is responding, False otherwise
        """
        try:
            response = requests.get(
                f"{self.server_url}/health",
                timeout=self.timeout,
            )
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
