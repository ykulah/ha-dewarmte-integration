import aiohttp
import logging
import asyncio
from datetime import datetime, timedelta, timezone
from custom_components.dewarmte.const import API_REFRESH_URL, TOKEN_REFRESH_MIN, API_TOKEN_URL, \
    API_BASE_URL, API_PRODUCTS_PATH

_LOGGER = logging.getLogger(__name__)

class DeWarmteAPIClient:
    #TOKEN_URL = "https://api.mydewarmte.com/v1/auth/token/"
    #REFRESH_URL = "https://api.mydewarmte.com/v1/auth/token/refresh/"

    TOKEN_URL = API_TOKEN_URL
    REFRESH_URL = API_REFRESH_URL
    BASE_URL = API_BASE_URL
    def __init__(self, email, password, session: aiohttp.ClientSession):
        self._email = email
        self._password = password
        self._session = session
        self._access_token = None
        self._refresh_token = None
        self._access_expires_at = None  # datetime

    async def authenticate(self):
        """Initial authentication using email and password."""
        payload = {
            "email": self._email,
            "password": self._password,
        }
        headers = {"Content-Type": "application/json"}

        async with self._session.post(self.TOKEN_URL, json=payload, headers=headers) as resp:
            if resp.status != 200:
                _LOGGER.error("Failed to authenticate: %s", resp.status)
                raise Exception("Authentication failed")

            data = await resp.json()
            self._access_token = data["access"]
            self._refresh_token = data["refresh"]
            self._access_expires_at = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_REFRESH_MIN)

            _LOGGER.info("Authenticated: access token acquired")

    async def refresh_access_token(self):
        """Refresh access token using refresh token."""
        if not self._refresh_token:
            _LOGGER.warning("No refresh token available, full re-auth required")
            return await self.authenticate()

        payload = {"refresh": self._refresh_token}
        headers = {"Content-Type": "application/json"}

        async with self._session.post(self.REFRESH_URL, json=payload, headers=headers) as resp:
            if resp.status == 200:
                data = await resp.json()
                self._access_token = data["access"]
                self._access_expires_at = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_REFRESH_MIN)
                _LOGGER.debug("Access token refreshed")
            else:
                _LOGGER.warning("Failed to refresh access token: %s", resp.status)
                await self.authenticate()

    async def async_ensure_authenticated(self):
        """Check and refresh access token if needed."""
        await self._ensure_valid_token()

    async def _ensure_valid_token(self):
        """Ensure access token is fresh."""
        if not self._access_token or not self._access_expires_at or datetime.now(timezone.utc) >= self._access_expires_at:
            _LOGGER.debug("Access token expired or missing, refreshing...")
            await self.refresh_access_token()

    async def _request(self, method, path, **kwargs):
        """Make an authenticated request with token refresh handling."""
        await self._ensure_valid_token()

        #url = f"https://api.mydewarmte.com{path}"
        url = f"{self.BASE_URL}{path}"
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self._access_token}"
        headers["Content-Type"] = "application/json"
        kwargs["headers"] = headers

        async with self._session.request(method, url, **kwargs) as resp:
            if resp.status == 401:
                _LOGGER.warning("401 Unauthorized, attempting token refresh...")
                await self.refresh_access_token()
                headers["Authorization"] = f"Bearer {self._access_token}"
                async with self._session.request(method, url, **kwargs) as retry_resp:
                    retry_resp.raise_for_status()
                    return await retry_resp.json()

            resp.raise_for_status()
            return await resp.json()

    async def async_get_devices(self):

        # products_resp = await self._request("GET", "/v1/customer/products")
        products_resp = await self._request("GET", API_PRODUCTS_PATH)
        if products_resp["count"] > 0:
            return products_resp["results"]
        else:
            return []