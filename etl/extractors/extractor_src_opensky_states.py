import httpx
import asyncio
import logging
from typing import List, Dict
from httpx import HTTPStatusError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthenticationError(Exception):
    pass

class SrcOpenskyStatesExtractor:
    BASE_URL = "https://opensky-network.org/api/states/all"
    RETRY_ATTEMPTS = 3
    BACKOFF_FACTOR = 2

    async def fetch_data(self) -> List[Dict]:
        params = {
            "lamin": "28.0",
            "lomin": "-10.0",
            "lamax": "47.0",
            "lomax": "37.0"
        }
        
        async with httpx.AsyncClient() as client:
            for attempt in range(self.RETRY_ATTEMPTS):
                try:
                    logger.info("Sending request to %s with params %s", self.BASE_URL, params)
                    response = await client.get(self.BASE_URL, params=params, headers={"Accept": "application/json"})
                    response.raise_for_status()
                    data = response.json()
                    logger.info("Request successful, latency: %d ms", response.elapsed.total_seconds() * 1000)
                    return data.get('states', [])
                except HTTPStatusError as e:
                    if e.response.status_code in {401, 403}:
                        raise AuthenticationError("Authentication failed") from e
                    elif e.response.status_code == 429:
                        logger.warning("Rate limit exceeded, waiting for 60 seconds before retrying...")
                        await asyncio.sleep(60)
                    else:
                        logger.error("HTTP error occurred: %s", e)
                        raise
                except Exception as e:
                    logger.error("An error occurred: %s", e)
                    if attempt < self.RETRY_ATTEMPTS - 1:
                        backoff_time = self.BACKOFF_FACTOR ** attempt
                        logger.warning("Retrying in %d seconds...", backoff_time)
                        await asyncio.sleep(backoff_time)
                    else:
                        raise
        return []