import aiohttp
import asyncio
import logging
import os
from typing import List, Dict, Any

class DataExtractor:
    BASE_URL = "https://restcountries.com/v3.1/all"
    MAX_RETRIES = 3
    TIMEOUT = (10, 30)
    USER_AGENT = os.getenv("USER_AGENT", "ETL-Agent/1.0")
    
    def __init__(self) -> None:
        self.session: aiohttp.ClientSession = None
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    async def extract(self) -> List[Dict[str, Any]]:
        if self.session is None:
            self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.TIMEOUT[0], connect=self.TIMEOUT[1]))
        
        retries = 0
        backoff = 1
        while retries < self.MAX_RETRIES:
            try:
                async with self.session.get(self.BASE_URL, headers={"User-Agent": self.USER_AGENT}) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    elif response.status == 429 or 500 <= response.status < 600:
                        self.logger.warning(f"Received status {response.status}. Retrying...")
                        await asyncio.sleep(backoff)
                        backoff *= 2
                        retries += 1
                    else:
                        self.logger.error(f"Unrecoverable error: {response.status}")
                        response.raise_for_status()
            except aiohttp.ClientError as e:
                self.logger.error(f"Client error occurred: {e}")
                raise
        raise Exception("Max retries exceeded")

    async def close(self) -> None:
        if self.session:
            await self.session.close()