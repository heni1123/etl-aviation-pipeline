import aiohttp
import asyncio
import logging
from typing import Dict, List, Any

class RestCountriesExtractor:
    def __init__(self, config: Dict) -> None:
        self.base_url = config["url"]
        self.params = config["params"]
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10, connect=30),
            headers={"User-Agent": "ETL-Agent/1.0"}
        )
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    async def extract(self) -> List[Dict[str, Any]]:
        origin_country = self.params.get("origin_country")
        url = self.base_url.format(origin_country=origin_country)
        return await self._fetch_page({"fields": self.params["fields"]})

    async def _fetch_page(self, params: Dict) -> Dict:
        url = self.base_url.format(origin_country=params.get("origin_country"))
        response = await self._retry_with_backoff(self.session.get, url, params)
        if response.status == 200:
            data = await response.json()
            return data
        elif response.status == 429:
            await self._handle_rate_limit(response)
        elif 500 <= response.status < 600:
            await self._retry_with_backoff(self.session.get, url, params)
        else:
            response.raise_for_status()

    async def _handle_rate_limit(self, response) -> None:
        retry_after = int(response.headers.get("Retry-After", 1))
        self.logger.warning(f"Rate limit exceeded. Retrying after {retry_after} seconds.")
        await asyncio.sleep(retry_after)

    async def _retry_with_backoff(self, func, *args) -> Any:
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                return await func(*args)
            except aiohttp.ClientError as e:
                if attempt < max_attempts - 1:
                    backoff_time = 2 ** attempt
                    self.logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {backoff_time} seconds.")
                    await asyncio.sleep(backoff_time)
                else:
                    self.logger.error(f"Max attempts reached. Raising error: {e}")
                    raise

    async def close(self) -> None:
        await self.session.close()