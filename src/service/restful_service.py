import requests
import json
import logging
from typing import Optional, Dict, Any, Union
from decorator.singleton import singleton


@singleton
class RestfulService:
    def __init__(self, default_timeout: int = 30):
        self.default_timeout = default_timeout
        self.logger = logging.getLogger(__name__)

    def _make_request(
        self,
        method: str,
        url: str,
        payload: Optional[Union[Dict[str, Any], str]] = None,
        timeout: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        if timeout is None:
            timeout = self.default_timeout

        if headers is None:
            headers = {"Content-Type": "application/json"}
        elif "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"

        if payload is not None and isinstance(payload, dict):
            payload = json.dumps(payload)

        try:
            self.logger.info(f"Making {method} request to {url}")

            if method.upper() == "GET":
                response = requests.get(url, timeout=timeout, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, data=payload, timeout=timeout, headers=headers)
            elif method.upper() == "PUT":
                response = requests.put(url, data=payload, timeout=timeout, headers=headers)
            elif method.upper() == "DELETE":
                response = requests.delete(url, timeout=timeout, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            self.logger.info(f"Response status: {response.status_code}")
            return response

        except requests.exceptions.Timeout:
            self.logger.error(f"Request timeout after {timeout} seconds")
            raise
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {str(e)}")
            raise

    def get(
        self,
        url: str,
        timeout: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        return self._make_request("GET", url, timeout=timeout, headers=headers)

    def post(
        self,
        url: str,
        payload: Optional[Union[Dict[str, Any], str]] = None,
        timeout: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        return self._make_request("POST", url, payload=payload, timeout=timeout, headers=headers)

    def put(
        self,
        url: str,
        payload: Optional[Union[Dict[str, Any], str]] = None,
        timeout: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        return self._make_request("PUT", url, payload=payload, timeout=timeout, headers=headers)

    def delete(
        self,
        url: str,
        timeout: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        return self._make_request("DELETE", url, timeout=timeout, headers=headers)
