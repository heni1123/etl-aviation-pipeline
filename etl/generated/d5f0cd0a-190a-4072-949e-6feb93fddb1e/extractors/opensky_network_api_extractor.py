import aiohttp
import asyncio
import logging
from typing import Any, Dict, List

class OpenskyNetworkExtractor:
    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.base_url = config["url"]
        self.params = config["params"]
        self.session = None
        self.logger = logging.getLogger("OpenSkyNetworkExtractor")
        logging.basicConfig(level=logging.INFO)

    async def extract(self) -> List[Dict[str, Any]]:
        try:
            return await self._fetch_page(self.params)
        except Exception as e:
            self.logger.error(f"Error during extraction: {e}")
            raise

    async def _fetch_page(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        response = await self._retry_with_backoff(self._make_request, params)
        return response.get("states", [])

    async def _make_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        async with self.session.get(self.base_url, params=params, timeout=aiohttp.ClientTimeout(total=10, connect=30), headers={"User-Agent": "ETL-Agent/1.0"}) as response:
            if response.status == 200:
                return await response.json()
            elif response.status == 429:
                await self._handle_rate_limit(response)
            elif 500 <= response.status < 600:
                raise Exception(f"Server error: {response.status}")
            else:
                raise Exception(f"Unrecoverable error: {response.status}")

    async def _handle_rate_limit(self, response) -> None:
        retry_after = int(response.headers.get("Retry-After", 1))
        self.logger.warning(f"Rate limit hit, retrying after {retry_after} seconds.")
        await asyncio.sleep(retry_after)

    async def _retry_with_backoff(self, func, *args) -> Any:
        attempts = 0
        while attempts < 3:
            try:
                return await func(*args)
            except Exception as e:
                attempts += 1
                wait_time = 2 ** attempts
                self.logger.warning(f"Attempt {attempts} failed: {e}. Retrying in {wait_time} seconds.")
                await asyncio.sleep(wait_time)
        raise Exception("Max retries exceeded")

    async def close(self) -> None:
        if self.session:
            await self.session.close()

    async def __aenter__(self) -> 'OpenskyNetworkExtractor':
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()