import aiohttp
import asyncio
import logging
from typing import Dict, List, Any

class AdsbdbExtractor:
    def __init__(self, config: Dict) -> None:
        self.base_url = config["url"]
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10, connect=30)
        )
        self.logger = logging.getLogger("adsbdb_extractor")
        logging.basicConfig(level=logging.INFO)

    async def extract(self) -> List[Dict[str, Any]]:
        callsigns = ["CALLSIGN1", "CALLSIGN2"]  # Replace with actual callsigns
        results = []
        for callsign in callsigns:
            try:
                response = await self._fetch_page(callsign)
                results.append(response)
            except Exception as e:
                self.logger.error(f"Error extracting data for {callsign}: {e}")
        return results

    async def _fetch_page(self, callsign: str) -> Dict[str, Any]:
        url = self.base_url.format(callsign=callsign)
        response = await self._retry_with_backoff(self.session.get, url)
        if response.status == 200:
            data = await response.json()
            return data
        elif response.status == 429:
            await self._handle_rate_limit(response)
        elif response.status in {401, 403, 404}:
            raise Exception(f"Unrecoverable error: {response.status}")
        else:
            response.raise_for_status()

    async def _handle_rate_limit(self, response) -> None:
        self.logger.warning("Rate limit exceeded, retrying...")
        await asyncio.sleep(5)  # Simple backoff strategy
        return await self._fetch_page(response.url)

    async def _retry_with_backoff(self, func, *args) -> Any:
        for attempt in range(3):
            try:
                return await func(*args)
            except aiohttp.ClientError as e:
                if attempt < 2:
                    backoff_time = 2 ** attempt
                    self.logger.warning(f"Retrying in {backoff_time} seconds...")
                    await asyncio.sleep(backoff_time)
                else:
                    raise e

    async def close(self) -> None:
        await self.session.close()